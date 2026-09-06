#!/usr/bin/env python3
"""Mutation-test the drift check: prove each guard is actually load-bearing.

A green suite says the tests pass, not that they would catch anything. This
injects known bugs and requires each one to be caught.

Two failure modes are designed against, both learned the hard way:

1. AN UNAPPLIED MUTANT LOOKS EXACTLY LIKE AN UNCAUGHT BUG. A substitution that
   silently matches nothing leaves the source pristine, the suite passes, and the
   harness reports "survived" -- indistinguishable from a real hole, and wrong in
   the more alarming direction. Every substitution here asserts it matched exactly
   once, and a mutant that fails to apply is a hard error, never a result.

2. A COUNT OF KILLS IS NOT EVIDENCE OF A GOOD MUTANT. A crude edit that breaks the
   module outright gets killed by everything and reads as extra confidence, while
   proving nothing about the guard it was aimed at. So each mutant declares WHICH
   tests must kill it, and the actual killer set has to match exactly. Over-killing
   fails just as loudly as under-killing.

Never mutates the working tree: everything runs in a throwaway copy.

Exit 0 all mutants killed by exactly their expected tests; 1 a mutant survived or
was killed by the wrong set; 2 the harness itself could not run.
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent

# (name, file, needle, replacement, {tests that must kill it})
MUTANTS = [
    (
        "collapse exit 2 into exit 1",
        "check_drift.py",
        "        return 2\n",
        "        return 1\n",
        {"test_unreadable_canonical_exits_exactly_2_not_1",
         "test_canonical_anchors_broken_exits_exactly_2",
         "test_unreadable_copy_exits_exactly_2_not_1",
         "test_drift_and_blind_never_share_a_code"},
    ),
    (
        "report findings as success",
        "check_drift.py",
        "    return 1 if findings else 0\n",
        "    return 0\n",
        {"test_drift_exits_exactly_1",
         "test_missing_exits_exactly_1",
         "test_unregistered_exits_exactly_1",
         "test_drift_and_blind_never_share_a_code"},
    ),
    (
        "anchor before normalising",
        "check_drift.py",
        "    flat = normalize(text)\n",
        "    flat = text\n",
        # 17 killers, measured not guessed. Two notable SURVIVORS, both legitimate
        # and worth recording:
        #   test_anchors_match_this_repos_own_copy -- our profile/README.md happens
        #     to wrap with both anchor sentences intact on single lines, so raw-text
        #     extraction still finds it. That is a property of the current wrap, not
        #     a guarantee; it means that test does not defend this guard.
        #   test_missing_exits_exactly_1 -- an absent file is None before any
        #     extraction happens, so normalisation is not on that path.
        {
            "test_all_in_sync",
            "test_checkout_only_redirects_the_copy_we_own",
            "test_copy_appearing_in_a_no_copy_repo_is_unregistered",
            "test_deleted_file_is_missing",
            "test_drift_exits_exactly_1",
            "test_end_anchor_split_across_a_newline_is_still_found",
            "test_in_sync_exits_0",
            "test_new_org_repo_absent_from_registry_is_unregistered",
            "test_real_wording_change_is_drift",
            "test_registry_naming_a_dead_repo_is_a_note_not_a_finding",
            "test_removed_paragraph_is_missing_not_drift",
            "test_scope_own_ignores_a_sibling_drift",
            "test_scope_own_still_catches_our_own_drift",
            "test_unregistered_exits_exactly_1",
            "test_with_checkout_the_edit_is_caught",
            "test_without_checkout_the_edit_is_invisible",
            "test_wrapping_width_does_not_affect_result",
        },
    ),
    (
        "ignore --checkout, so CI reads the base branch",
        "check_drift.py",
        '        if self_checkout is not None and entry.get("owner") == "self":\n',
        "        if False:\n",
        {"test_with_checkout_the_edit_is_caught",
         "test_checkout_only_redirects_the_copy_we_own",
         "test_deleted_file_in_checkout_is_missing"},
    ),
    (
        "skip the org completeness guard",
        "check_drift.py",
        "        for repo in sorted(set(live) - known):\n",
        "        for repo in sorted(set()):\n",
        {"test_new_org_repo_absent_from_registry_is_unregistered"},
    ),
    (
        "treat an unreadable copy as absent",
        "check_drift.py",
        '            raise Operational(f"cannot read {c[\'repo\']}/{c[\'path\']}: {e}") from e\n',
        "            text = None\n",
        {"test_unreadable_copy", "test_unreadable_copy_exits_exactly_2_not_1"},
    ),
]


def run_suite(workdir: Path) -> set[str]:
    """Return the set of test names that failed or errored."""
    r = subprocess.run([sys.executable, "-m", "unittest", "test_check_drift", "-v"],
                       cwd=workdir, capture_output=True, text=True)
    return set(re.findall(r"^(?:FAIL|ERROR): (\w+)", r.stderr, re.M))


def main() -> int:
    src_files = ["check_drift.py", "test_check_drift.py", "copies.json", "regenerate.py"]
    with tempfile.TemporaryDirectory() as td:
        base = Path(td) / "pristine"
        base.mkdir()
        for f in src_files:
            shutil.copy2(HERE / f, base / f)
        # profile/README.md is read by TestShippedManifest
        (Path(td) / "pristine" / ".." / "profile").resolve().mkdir(exist_ok=True)
        shutil.copy2(HERE.parent / "profile" / "README.md",
                     Path(td) / "profile" / "README.md")

        # Control. If the suite is not green on pristine source here, every kill
        # count below is meaningless and the harness must say so rather than run.
        survivors = run_suite(base)
        if survivors:
            print(f"FATAL: suite is not green on unmutated source: {sorted(survivors)}",
                  file=sys.stderr)
            return 2
        print("control: unmutated suite green -- kill counts below are meaningful\n")

        failed = False
        for name, fname, needle, repl, expected in MUTANTS:
            work = Path(td) / "work"
            if work.exists():
                shutil.rmtree(work)
            shutil.copytree(base, work)

            text = (work / fname).read_text(encoding="utf-8")
            hits = text.count(needle)
            if hits != 1:
                print(f"FATAL: mutant {name!r} matched {hits} times, expected exactly 1. "
                      f"An unapplied mutant is not a result.", file=sys.stderr)
                return 2
            (work / fname).write_text(text.replace(needle, repl), encoding="utf-8")

            killers = run_suite(work)
            if not killers:
                print(f"SURVIVED  {name}\n      no test caught it")
                failed = True
            elif killers != expected:
                print(f"WRONG SET {name}")
                if killers - expected:
                    print(f"      unexpected killers (mutant may be cruder than "
                          f"intended): {sorted(killers - expected)}")
                if expected - killers:
                    print(f"      expected killers that passed: "
                          f"{sorted(expected - killers)}")
                failed = True
            else:
                print(f"killed    {name}  ({len(killers)} tests)")

        print()
        if failed:
            print("mutation testing FAILED -- a guard is not load-bearing, or a mutant "
                  "is not testing what it claims")
            return 1
        print(f"all {len(MUTANTS)} mutants killed by exactly their expected tests")
        return 0


if __name__ == "__main__":
    sys.exit(main())
