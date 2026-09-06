# Posture paragraph drift check

The ACDP maintenance-posture paragraph has exactly one owner — the spec repo's
`README.md` — and is copied **verbatim** into sibling repos. This directory holds
the registry of those copies and the check that keeps them honest.

## Why this exists

A stale copy is invisible to the repo holding it. The copy does not change;
canonical moves out from under it. Nothing in that repo's diff, review, or CI can
see it, because from inside that repo nothing happened.

This is not hypothetical. Both known copies have been stale at some point:

- `.github/profile/README.md` still described RFC-ACDP-0015 as `Draft` for nine
  days after it was promoted to `Final` on 2026-08-28.
- `acdp-verifier-py/README.md` carried the same staleness, found only because
  someone happened to grep for it while working on something else.

Both were caught by hand. That is the gap this closes.

## What the check reports

Four conditions, deliberately. A checker that computes only "does this copy differ
from canonical?" is permanently green for a copy that was never registered as a
copy in the first place — which is the failure most likely to actually happen.

| Condition | Meaning | Fails the run |
|---|---|---|
| `DRIFT` | A registered copy no longer matches canonical | yes |
| `MISSING` | A registered copy no longer contains the paragraph at all | yes |
| `UNREGISTERED` | A repo asserted to hold no copy now holds one, **or** a repo exists in the org that `copies.json` does not account for | yes |
| `UNCOVERED` | A repo the check provably cannot read | no — reported every run |

Exit codes are `0` in sync, `1` findings, `2` **the check could not see**. The
last one is separate on purpose: a run that could not read canonical is not a run
that found no drift, and collapsing the two is how a blind check gets read as a
clean one.

## Files

| File | Purpose |
|---|---|
| `copies.json` | The registry: canonical, every copy, every repo asserted to hold none, and why the two known non-copies are excluded |
| `check_drift.py` | The check. Stdlib only |
| `regenerate.py` | Rewrites this repo's copy from canonical. Shares `extract()` with the checker so the writer and the police agree |
| `test_check_drift.py` | 28 tests, run in CI before the check itself |

## Usage

```sh
python3 posture/check_drift.py                      # every registered copy
python3 posture/check_drift.py --scope own          # only the copy this repo owns
python3 posture/check_drift.py --checkout .         # read our copy from the working tree
python3 posture/check_drift.py --source local       # read sibling checkouts side-by-side
python3 posture/regenerate.py --check               # would our copy change?
python3 posture/regenerate.py                       # rewrite it from canonical
python3 -m unittest discover -s posture -v          # the tests
```

`--checkout .` is load-bearing in CI. On a pull request the API still serves the
**base** branch, so without it the check reads the paragraph the PR is trying to
change and passes a hand-edit.

## Fixing a finding

- **Ours** (`.github/profile/README.md`) — run `python3 posture/regenerate.py` and
  commit. Never retype the paragraph: a hand-typed copy that is 99% right is worse
  than an obviously stale one, because the diff looks deliberate.
- **A sibling's** — file an issue in that repo. Do not edit a sibling repo from
  here; that boundary is the org's convention, not a limitation of this script.
- **`UNREGISTERED`** — register it in `copies.json`, or record there why it is not
  a copy, in the same change that introduced it.

## Adding a copy

Add it to `copies.json` under `copies` **in the same change that creates it**, and
remove that repo from `no_copy.repos`. The completeness guard means a repo cannot
simply be forgotten — but it can only tell you a repo is unaccounted for, not that
a file inside an accounted-for repo has quietly become a second copy.

## Known coverage limits

Stated rather than left to be discovered, because a check whose limits are unclear
gets trusted for more than it does.

1. **`acdp-website` is not covered.** It is private, and a `GITHUB_TOKEN` scoped to
   this repo cannot read it. Reported as `UNCOVERED` on every run.
2. **The unregistered-copy sweep reads READMEs only.** A copy pasted into some other
   file in an accounted-for repo is not detected. READMEs are where the paragraph
   has actually spread; widening this to full code search needs a token this
   workflow deliberately does not have.
3. **Comparison is whitespace-normalised**, so hard-wrap width and the
   `**Project status.**` run-in prefix are free. Any other wording difference —
   including punctuation — is drift.
4. **Nothing here watches the reverse direction.** If canonical itself becomes
   wrong, every copy matches it and the check is green. Correctness of the wording
   is the spec repo's call; this only enforces agreement.
