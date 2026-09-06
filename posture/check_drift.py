#!/usr/bin/env python3
"""Check that every registered copy of the ACDP maintenance-posture paragraph
still matches its canonical source.

The paragraph has one owner -- the spec repo's README -- and is copied verbatim
into sibling repos. Nothing in a single repo's review can see a copy going
stale, because the copy does not change: canonical moves out from under it. This
check is the thing that looks across all of them.

It reports four conditions, not one. A checker that computes only "copy differs
from canonical" is permanently green for a repo whose copy was never registered
as a copy in the first place, which is the failure most likely to actually
happen:

  DRIFT         a registered copy no longer matches canonical
  MISSING       a registered copy no longer contains the paragraph at all
  UNREGISTERED  a repo asserted to hold no copy now holds one, or a repo exists
                in the org that the registry does not account for at all
  UNCOVERED     a repo this check provably cannot read (reported every run, so
                coverage is never overstated; not a failure)

Exit codes:
  0  everything the check can see is in sync
  1  findings (DRIFT / MISSING / UNREGISTERED)
  2  operational failure -- could not read canonical, or a fetch failed for a
     reason other than "file absent". Never silently downgraded to a pass: a
     check that cannot see is not a check that found nothing.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"
UA = "acdp-posture-drift-check"


# --- extraction ------------------------------------------------------------
# Normalise BEFORE anchoring. Copies are hard-wrapped at different widths, so
# the end anchor is split across a newline in some of them; anchoring on raw
# text reports a confident false DRIFT. This ordering is load-bearing and is
# pinned by test_check_drift.py.

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract(text: str, start: str, end: str) -> str | None:
    flat = normalize(text)
    i = flat.find(start)
    if i < 0:
        return None
    j = flat.find(end, i)
    if j < 0:
        return None
    return flat[i : j + len(end)]


# --- sources ---------------------------------------------------------------

class Unavailable(Exception):
    """Fetch failed for a reason that is NOT 'the file is absent'."""


class Operational(Exception):
    """The check could not see what it needed to. Distinct from a finding, and
    distinct on the way out: exit 2, never exit 1. Collapsing the two is how a
    blind run gets read as a clean run."""


def _request(url: str, token: str | None, accept: str) -> bytes:
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": UA})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None  # genuinely absent
        raise Unavailable(f"HTTP {e.code} for {url}") from e
    except Exception as e:
        raise Unavailable(f"{type(e).__name__} for {url}") from e


class RemoteSource:
    """Reads files from GitHub. Public repos work unauthenticated; a token only
    raises the rate limit and unlocks private repos the token can see."""

    def __init__(self, token: str | None):
        self.token = token

    def read(self, repo: str, path: str) -> str | None:
        raw = _request(
            f"{API}/repos/{repo}/contents/{path}",
            self.token,
            "application/vnd.github.raw",
        )
        return None if raw is None else raw.decode("utf-8")

    def org_repos(self, org: str) -> list[str]:
        names, page = [], 1
        while True:
            raw = _request(
                f"{API}/orgs/{org}/repos?per_page=100&page={page}",
                self.token,
                "application/vnd.github+json",
            )
            if raw is None:
                raise Unavailable(f"org {org} not visible")
            batch = json.loads(raw)
            if not batch:
                break
            names += [r["full_name"] for r in batch if not r.get("archived")]
            if len(batch) < 100:
                break
            page += 1
        return names


class LocalSource:
    """Reads sibling checkouts side-by-side in a workspace dir, so the check is
    runnable before pushing. Cannot enumerate the org, so the completeness
    guard is skipped and said to be skipped."""

    def __init__(self, workspace: Path):
        self.workspace = workspace

    def read(self, repo: str, path: str, local_dir: str | None = None) -> str | None:
        d = local_dir or repo.split("/")[-1]
        f = self.workspace / d / path
        if not (self.workspace / d).is_dir():
            raise Unavailable(f"no checkout at {self.workspace / d}")
        return f.read_text(encoding="utf-8") if f.is_file() else None

    def org_repos(self, org: str) -> list[str] | None:
        return None


# --- the check -------------------------------------------------------------

def run(manifest: dict, source, scope: str,
        self_checkout: Path | None = None) -> tuple[list[dict], list[dict], list[str]]:
    """self_checkout: read the copy this repo OWNS from this working tree instead of
    from the API. Load-bearing in CI. On a pull request the API still serves the base
    branch, so a remote-only check reads the paragraph the PR is trying to change and
    passes a hand-edit -- green, confident, and wrong."""
    findings: list[dict] = []
    uncovered: list[dict] = []
    notes: list[str] = []

    start = manifest["anchors"]["start"]
    end = manifest["anchors"]["end"]
    local = isinstance(source, LocalSource)

    def read(entry: dict, path: str | None = None):
        p = path if path is not None else entry["path"]
        if self_checkout is not None and entry.get("owner") == "self":
            f = self_checkout / p
            return f.read_text(encoding="utf-8") if f.is_file() else None
        if local:
            return source.read(entry["repo"], p, entry.get("local_dir"))
        return source.read(entry["repo"], p)

    # canonical -- any failure here is operational, never a finding
    canon_entry = manifest["canonical"]
    try:
        canon_text = read(canon_entry)
    except Unavailable as e:
        raise Operational(f"cannot read canonical source: {e}. "
                          f"Not reporting 'no drift' -- the check could not see.") from e
    if canon_text is None:
        raise Operational(
            f"canonical file {canon_entry['repo']}/{canon_entry['path']} is gone."
        )
    canonical = extract(canon_text, start, end)
    if canonical is None:
        raise Operational(
            f"canonical paragraph not found in {canon_entry['repo']}/"
            f"{canon_entry['path']}. Either the wording changed past the anchors "
            f"(update posture/copies.json) or the section was removed."
        )

    # registered copies
    for c in manifest["copies"]:
        if scope == "own" and c.get("owner") != "self":
            notes.append(f"skipped (scope=own): {c['repo']}/{c['path']}")
            continue
        try:
            text = read(c)
        except Unavailable as e:
            raise Operational(f"cannot read {c['repo']}/{c['path']}: {e}") from e
        if text is None:
            findings.append({"kind": "MISSING", "repo": c["repo"], "path": c["path"],
                             "detail": "registered copy: file does not exist"})
            continue
        got = extract(text, start, end)
        if got is None:
            findings.append({"kind": "MISSING", "repo": c["repo"], "path": c["path"],
                             "detail": "registered copy: paragraph not found in file"})
        elif got != canonical:
            findings.append({"kind": "DRIFT", "repo": c["repo"], "path": c["path"],
                             "detail": first_difference(canonical, got)})

    # repos asserted to hold no copy
    for repo in manifest["no_copy"]["repos"]:
        entry = {"repo": repo, "local_dir": repo.split("/")[-1]}
        try:
            text = read(entry, "README.md")
        except Unavailable as e:
            uncovered.append({"repo": repo, "reason": f"README unreadable: {e}"})
            continue
        if text and extract(text, start, end) is not None:
            findings.append({"kind": "UNREGISTERED", "repo": repo, "path": "README.md",
                             "detail": "holds the paragraph but is listed under no_copy; "
                                       "register it in posture/copies.json"})

    for u in manifest["unscannable"]:
        uncovered.append({"repo": u["repo"], "reason": u["reason"]})

    # completeness: does the registry account for every repo in the org?
    org = canon_entry["repo"].split("/")[0]
    try:
        live = source.org_repos(org)
    except Unavailable as e:
        raise Operational(f"cannot enumerate org {org}: {e}") from e
    if live is None:
        notes.append("completeness guard skipped: local mode cannot enumerate the org")
    else:
        known = {canon_entry["repo"]}
        known |= {c["repo"] for c in manifest["copies"]}
        known |= set(manifest["no_copy"]["repos"])
        known |= {u["repo"] for u in manifest["unscannable"]}
        for repo in sorted(set(live) - known):
            findings.append({"kind": "UNREGISTERED", "repo": repo, "path": "-",
                             "detail": "repo exists in the org but posture/copies.json "
                                       "does not say whether it holds a copy"})
        # An unscannable repo is expected to be absent from a listing made with a
        # token that cannot see it -- that is not evidence the repo is gone.
        unscannable = {u["repo"] for u in manifest["unscannable"]}
        for repo in sorted(known - set(live) - unscannable):
            notes.append(f"registry lists {repo}, which the org no longer returns "
                         f"(renamed, archived or deleted) -- prune posture/copies.json")

    return findings, uncovered, notes


def first_difference(a: str, b: str) -> str:
    i = 0
    while i < min(len(a), len(b)) and a[i] == b[i]:
        i += 1
    lo = max(0, i - 40)
    return (f"diverges at char {i}\n"
            f"      canonical: ...{a[lo:i+60]}\n"
            f"      copy:      ...{b[lo:i+60]}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", type=Path,
                    default=Path(__file__).parent / "copies.json")
    ap.add_argument("--source", choices=["remote", "local"], default="remote")
    ap.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2],
                    help="local mode: dir holding sibling checkouts")
    ap.add_argument("--scope", choices=["all", "own"], default="all",
                    help="'own' checks only copies this repo owns -- used on PRs so a "
                         "sibling's drift cannot block unrelated work here")
    ap.add_argument("--checkout", type=Path, default=None,
                    help="read the copy this repo owns from this working tree rather "
                         "than from the API -- required in CI, where the API would "
                         "otherwise serve the base branch and pass a hand-edited PR")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    source = (LocalSource(args.workspace) if args.source == "local"
              else RemoteSource(os.environ.get("GITHUB_TOKEN")))

    try:
        findings, uncovered, notes = run(manifest, source, args.scope, args.checkout)
    except Operational as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({"findings": findings, "uncovered": uncovered,
                          "notes": notes}, indent=2))
    else:
        for n in notes:
            print(f"note: {n}")
        for u in uncovered:
            print(f"UNCOVERED  {u['repo']}\n      {u['reason']}")
        for f in findings:
            print(f"{f['kind']:<13}{f['repo']}/{f['path']}\n      {f['detail']}")
        covered = len(manifest["copies"]) + len(manifest["no_copy"]["repos"])
        print(f"\nchecked {covered} repos against canonical "
              f"({manifest['canonical']['repo']}/{manifest['canonical']['path']}); "
              f"{len(uncovered)} uncovered; {len(findings)} finding(s)")
        if not findings:
            print("posture paragraph is in sync everywhere this check can see.")

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
