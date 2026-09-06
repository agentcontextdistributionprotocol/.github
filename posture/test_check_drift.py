#!/usr/bin/env python3
"""Tests for the posture drift check.

Stdlib only, no install step -- this repo has no package manifest and should not
grow one for a single script.

The cases that matter are the ones where a plausible implementation is confidently
wrong: a false DRIFT caused by hard-wrapping (which the first cut of this checker
actually produced), and any path where the check cannot see but reports success.
"""

import json
import sys
import unittest
from pathlib import Path

import check_drift as cd

HERE = Path(__file__).parent
CANON_PARA = (
    "ACDP is maintained by a single maintainer on a best-effort basis; changes land "
    "when a consumer needs them, with no SLA. The stable surface is the 0.1.0 / 0.2.0 "
    "/ 0.3.0 / 0.4.0 Final lines, which are wire-frozen. RFC-ACDP-0016 (typed external "
    "anchors) is Draft on the open 0.5.0 line, and RFC-ACDP-0009 is Reserved; neither "
    "is a dependable surface until promoted. Promotion to Final requires the "
    "conformance pack to pass against two independent implementations (`acdp-rs` and "
    "`acdp-verifier-py`); the second implementation is therefore part of the "
    "protocol's governance machinery, not an optional extra. Security reports: see "
    "SECURITY.md in the org profile."
)

MANIFEST = {
    "anchors": {"start": "ACDP is maintained by a single maintainer",
                "end": "Security reports: see SECURITY.md in the org profile."},
    "canonical": {"repo": "org/spec", "path": "README.md"},
    "copies": [
        {"repo": "org/self", "path": "profile/README.md", "owner": "self"},
        {"repo": "org/other", "path": "README.md", "owner": "org/other"},
    ],
    "no_copy": {"repos": ["org/clean"]},
    "unscannable": [{"repo": "org/private", "reason": "private"}],
}


def wrap(text, width):
    """Hard-wrap like the real copies are, so the end anchor lands mid-line."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    return "\n".join(lines)


class FakeSource:
    def __init__(self, files, repos=("org/spec", "org/self", "org/other",
                                     "org/clean", "org/private"), fail=()):
        self.files, self.repos, self.fail = files, list(repos), set(fail)

    def read(self, repo, path):
        if repo in self.fail:
            raise cd.Unavailable(f"boom for {repo}")
        return self.files.get((repo, path))

    def org_repos(self, org):
        return self.repos


def sources(self_body=None, other_body=None, **kw):
    return FakeSource({
        ("org/spec", "README.md"): f"# Spec\n\n## Project status\n\n{CANON_PARA}\n",
        ("org/self", "profile/README.md"):
            self_body if self_body is not None
            else "# Org\n\n**Project status.** " + wrap(CANON_PARA, 78) + "\n",
        ("org/other", "README.md"):
            other_body if other_body is not None
            else "# Other\n\n## Project status\n\n" + wrap(CANON_PARA, 74) + "\n",
        ("org/clean", "README.md"): "# Clean\n\nNothing to see.\n",
    }, **kw)


class TestExtraction(unittest.TestCase):
    def test_end_anchor_split_across_a_newline_is_still_found(self):
        """The bug that shipped in the first cut: anchoring on raw text misses a
        wrapped end anchor and reports a confident false DRIFT."""
        wrapped = wrap(CANON_PARA, 74)
        self.assertNotIn(MANIFEST["anchors"]["end"], wrapped)  # raw text: absent
        got = cd.extract(wrapped, **MANIFEST["anchors"])
        self.assertEqual(got, CANON_PARA)                      # normalised: found

    def test_wrapping_width_does_not_affect_result(self):
        a = cd.extract(wrap(CANON_PARA, 60), **MANIFEST["anchors"])
        b = cd.extract(wrap(CANON_PARA, 100), **MANIFEST["anchors"])
        self.assertEqual(a, b)

    def test_run_in_prefix_is_excluded(self):
        got = cd.extract("**Project status.** " + CANON_PARA, **MANIFEST["anchors"])
        self.assertTrue(got.startswith("ACDP is maintained"))

    def test_website_footer_paraphrase_is_not_matched(self):
        """Must not be picked up as a copy -- it makes no version claim."""
        footer = "Maintained by a single maintainer on a best-effort basis, with no SLA."
        self.assertIsNone(cd.extract(footer, **MANIFEST["anchors"]))

    def test_changelog_entry_is_not_matched(self):
        entry = ('- **README: new "Project status" section** stating the maintenance '
                 'posture (single maintainer, best-effort, no SLA), the stable '
                 'wire-frozen surface (0.1.0/0.2.0/0.3.0 Final).')
        self.assertIsNone(cd.extract(entry, **MANIFEST["anchors"]))

    def test_absent_paragraph_returns_none(self):
        self.assertIsNone(cd.extract("# Readme\n\nnothing\n", **MANIFEST["anchors"]))


class TestRun(unittest.TestCase):
    def check(self, src, scope="all"):
        return cd.run(MANIFEST, src, scope)

    def test_all_in_sync(self):
        findings, uncovered, _ = self.check(sources())
        self.assertEqual(findings, [])
        self.assertEqual([u["repo"] for u in uncovered], ["org/private"])

    def test_real_wording_change_is_drift(self):
        stale = CANON_PARA.replace("0.4.0 Final lines", "0.3.0 Final lines")
        findings, _, _ = self.check(sources(other_body=wrap(stale, 74)))
        self.assertEqual([f["kind"] for f in findings], ["DRIFT"])
        self.assertEqual(findings[0]["repo"], "org/other")

    def test_removed_paragraph_is_missing_not_drift(self):
        findings, _, _ = self.check(sources(other_body="# Other\n\ngone\n"))
        self.assertEqual([f["kind"] for f in findings], ["MISSING"])

    def test_deleted_file_is_missing(self):
        src = sources()
        del src.files[("org/other", "README.md")]
        findings, _, _ = self.check(src)
        self.assertEqual([f["kind"] for f in findings], ["MISSING"])

    def test_copy_appearing_in_a_no_copy_repo_is_unregistered(self):
        src = sources()
        src.files[("org/clean", "README.md")] = "# Clean\n\n" + wrap(CANON_PARA, 80)
        findings, _, _ = self.check(src)
        self.assertEqual([f["kind"] for f in findings], ["UNREGISTERED"])
        self.assertEqual(findings[0]["repo"], "org/clean")

    def test_new_org_repo_absent_from_registry_is_unregistered(self):
        """The hole a copy-vs-canonical-only checker never sees."""
        src = sources()
        src.repos.append("org/brand-new")
        findings, _, _ = self.check(src)
        self.assertEqual([f["kind"] for f in findings], ["UNREGISTERED"])
        self.assertEqual(findings[0]["repo"], "org/brand-new")

    def test_registry_naming_a_dead_repo_is_a_note_not_a_finding(self):
        src = sources()
        src.repos.remove("org/clean")
        findings, _, notes = self.check(src)
        self.assertEqual(findings, [])
        self.assertTrue(any("org/clean" in n for n in notes))

    def test_scope_own_ignores_a_sibling_drift(self):
        stale = CANON_PARA.replace("0.4.0", "0.3.0")
        src = sources(other_body=wrap(stale, 74))
        self.assertEqual(self.check(src, scope="all")[0][0]["kind"], "DRIFT")
        self.assertEqual(self.check(src, scope="own")[0], [])

    def test_scope_own_still_catches_our_own_drift(self):
        stale = CANON_PARA.replace("0.4.0", "0.3.0")
        findings, _, _ = self.check(sources(self_body=wrap(stale, 78)), scope="own")
        self.assertEqual([f["kind"] for f in findings], ["DRIFT"])


class TestCannotSeeIsNeverAPass(unittest.TestCase):
    """Every blind path must raise Operational (exit 2), never return no findings."""

    def test_unreadable_canonical(self):
        with self.assertRaises(cd.Operational):
            cd.run(MANIFEST, sources(fail=["org/spec"]), "all")

    def test_missing_canonical_file(self):
        src = sources(); del src.files[("org/spec", "README.md")]
        with self.assertRaises(cd.Operational):
            cd.run(MANIFEST, src, "all")

    def test_canonical_wording_moved_past_the_anchors(self):
        src = sources()
        src.files[("org/spec", "README.md")] = "# Spec\n\nrewritten, no anchors\n"
        with self.assertRaises(cd.Operational):
            cd.run(MANIFEST, src, "all")

    def test_unreadable_copy(self):
        with self.assertRaises(cd.Operational):
            cd.run(MANIFEST, sources(fail=["org/other"]), "all")

    def test_org_enumeration_failure(self):
        class Blind(FakeSource):
            def org_repos(self, org):
                raise cd.Unavailable("no org access")
        with self.assertRaises(cd.Operational):
            cd.run(MANIFEST, Blind(sources().files), "all")

    def test_unreadable_no_copy_repo_is_uncovered_not_silent(self):
        _, uncovered, _ = cd.run(MANIFEST, sources(fail=["org/clean"]), "all")
        self.assertIn("org/clean", [u["repo"] for u in uncovered])


class TestShippedManifest(unittest.TestCase):
    """The real copies.json must stay loadable and self-consistent."""

    def setUp(self):
        self.m = json.loads((HERE / "copies.json").read_text(encoding="utf-8"))

    def test_anchors_match_this_repos_own_copy(self):
        text = (HERE.parent / "profile" / "README.md").read_text(encoding="utf-8")
        self.assertIsNotNone(cd.extract(text, self.m["anchors"]["start"],
                                        self.m["anchors"]["end"]))

    def test_every_repo_listed_exactly_once(self):
        seen = [self.m["canonical"]["repo"]]
        seen += [c["repo"] for c in self.m["copies"]]
        seen += self.m["no_copy"]["repos"]
        seen += [u["repo"] for u in self.m["unscannable"]]
        self.assertEqual(len(seen), len(set(seen)), f"duplicate disposition: {seen}")

    def test_exactly_one_copy_is_owned_by_this_repo(self):
        own = [c for c in self.m["copies"] if c.get("owner") == "self"]
        self.assertEqual(len(own), 1)
        self.assertEqual(own[0]["path"], "profile/README.md")


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestSelfCheckout(unittest.TestCase):
    """On a PR the API serves the base branch. Without --checkout the check reads the
    paragraph the PR is trying to change and passes a hand-edit."""

    def setUp(self):
        import tempfile
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "profile").mkdir()
        stale = CANON_PARA.replace("0.4.0 Final lines", "0.3.0 Final lines")
        (self.tmp / "profile" / "README.md").write_text(
            "# Org\n\n**Project status.** " + wrap(stale, 78) + "\n", encoding="utf-8")

    def tearDown(self):
        import shutil; shutil.rmtree(self.tmp)

    def test_without_checkout_the_edit_is_invisible(self):
        findings, _, _ = cd.run(MANIFEST, sources(), "own")
        self.assertEqual(findings, [], "remote source legitimately sees the base branch")

    def test_with_checkout_the_edit_is_caught(self):
        findings, _, _ = cd.run(MANIFEST, sources(), "own", self_checkout=self.tmp)
        self.assertEqual([f["kind"] for f in findings], ["DRIFT"])
        self.assertEqual(findings[0]["repo"], "org/self")

    def test_checkout_only_redirects_the_copy_we_own(self):
        stale = CANON_PARA.replace("0.4.0", "0.3.0")
        findings, _, _ = cd.run(MANIFEST, sources(other_body=wrap(stale, 74)), "all",
                                self_checkout=self.tmp)
        kinds = {(f["repo"], f["kind"]) for f in findings}
        self.assertEqual(kinds, {("org/self", "DRIFT"), ("org/other", "DRIFT")})

    def test_deleted_file_in_checkout_is_missing(self):
        (self.tmp / "profile" / "README.md").unlink()
        findings, _, _ = cd.run(MANIFEST, sources(), "own", self_checkout=self.tmp)
        self.assertEqual([f["kind"] for f in findings], ["MISSING"])


class TestExitCodeContract(unittest.TestCase):
    """The 1-versus-2 boundary, asserted at the CLI where it is actually consumed.

    .github/workflows/posture-drift.yml routes on these exact codes: 1 renders
    "Drift found", 2 renders "The check could not see -- do not read it as no
    drift". Collapsing them turns a blind run into a drift report, which is the
    failure this whole check exists to avoid.

    Everything above tests run(); none of it touches main(), so the mapping from
    Operational to 2 and findings to 1 was unasserted -- changing `return 2` to
    `return 1` passed all 28 of them. Asserted here with exact codes, never
    "non-zero", so the two cannot quietly collapse back together.

    Run as a subprocess so argparse wiring and the return-to-exit path are
    covered too, not just the function bodies.
    """

    SCRIPT = HERE / "check_drift.py"

    def setUp(self):
        import tempfile
        self.ws = Path(tempfile.mkdtemp())
        self.write("spec/README.md", f"# Spec\n\n## Project status\n\n{CANON_PARA}\n")
        self.write("ours/profile/README.md",
                   "# Org\n\n**Project status.** " + wrap(CANON_PARA, 81) + "\n")
        self.write("theirs/README.md",
                   "# Theirs\n\n## Project status\n\n" + wrap(CANON_PARA, 80) + "\n")
        self.write("clean/README.md", "# Clean\n\nNothing.\n")
        self.manifest = self.ws / "manifest.json"
        self.manifest.write_text(json.dumps({
            "anchors": MANIFEST["anchors"],
            "canonical": {"repo": "org/spec", "path": "README.md", "local_dir": "spec"},
            "copies": [
                {"repo": "org/ours", "path": "profile/README.md",
                 "local_dir": "ours", "owner": "self"},
                {"repo": "org/theirs", "path": "README.md", "local_dir": "theirs",
                 "owner": "org/theirs"},
            ],
            "no_copy": {"repos": ["org/clean"]},
            "unscannable": [],
        }), encoding="utf-8")

    def tearDown(self):
        import shutil; shutil.rmtree(self.ws)

    def write(self, rel, text):
        f = self.ws / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")

    def run_cli(self, *extra):
        import subprocess
        return subprocess.run(
            [sys.executable, str(self.SCRIPT), "--manifest", str(self.manifest),
             "--source", "local", "--workspace", str(self.ws), *extra],
            capture_output=True, text=True)

    def test_in_sync_exits_0(self):
        r = self.run_cli()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("in sync", r.stdout)

    def test_drift_exits_exactly_1(self):
        self.write("theirs/README.md", "# Theirs\n\n## Project status\n\n" +
                   wrap(CANON_PARA.replace("0.4.0 Final", "0.3.0 Final"), 80) + "\n")
        r = self.run_cli()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("DRIFT", r.stdout)

    def test_missing_exits_exactly_1(self):
        (self.ws / "theirs" / "README.md").unlink()
        self.assertEqual(self.run_cli().returncode, 1)

    def test_unregistered_exits_exactly_1(self):
        self.write("clean/README.md", "# Clean\n\n" + wrap(CANON_PARA, 80) + "\n")
        r = self.run_cli()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("UNREGISTERED", r.stdout)

    def test_unreadable_canonical_exits_exactly_2_not_1(self):
        """The one that matters: blind must not be reportable as drift."""
        import shutil; shutil.rmtree(self.ws / "spec")
        r = self.run_cli()
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("FATAL", r.stderr)
        self.assertNotIn("DRIFT", r.stdout)

    def test_canonical_anchors_broken_exits_exactly_2(self):
        self.write("spec/README.md", "# Spec\n\nrewritten, no anchors\n")
        self.assertEqual(self.run_cli().returncode, 2)

    def test_unreadable_copy_exits_exactly_2_not_1(self):
        """A copy we cannot read is not a copy we found drift in."""
        import shutil; shutil.rmtree(self.ws / "theirs")
        r = self.run_cli()
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_drift_and_blind_never_share_a_code(self):
        # Introduce real drift first. Comparing an in-sync run against a blind one
        # would pass even with the codes collapsed, which is what this asserts against.
        self.write("theirs/README.md", "# Theirs\n\n## Project status\n\n" +
                   wrap(CANON_PARA.replace("0.4.0 Final", "0.3.0 Final"), 80) + "\n")
        drift = self.run_cli()
        self.assertEqual(drift.returncode, 1)
        self.write("spec/README.md", "# Spec\n\nno anchors\n")
        blind = self.run_cli()
        self.assertEqual(blind.returncode, 2)
        self.assertNotEqual(drift.returncode, blind.returncode,
                            "exit codes collapsed: the workflow cannot tell a blind "
                            "run from a drift report")
