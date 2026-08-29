# ORG-1 + ORG-2 — maintenance posture & complete family repo map

**Repo:** `dotgithub` (local clone dir) = `agentcontextdistributionprotocol/.github` on GitHub
(`git remote -v` [C]) — the org profile repo.
**Branch / PR:** one branch, one PR covering both items.
**Wave:** W1-ORG (`00-overview.md:292`). **Track:** T5 (posture & hygiene). **Priority:** now.
**Layer moved:** *consumed* — this repo publishes no protocol surface; it is the org's front door.

---

## Context

### The two items

Source of truth for scope: `/Users/ajitkoti/code/agentcontextdistributionprotocol/agentcontextdistributionprotocol/plans/siblings/misc-siblings.md` §ORG (lines 248-261),
sequenced in `00-overview.md:137-138` and `:292`.

- **ORG-1 [T5, now]** — `profile/README.md` gets the single-maintainer / best-effort statement matching
  SPEC-5; *and* `SECURITY.md` is checked for response expectations consistent with best-effort rather than
  implying an SLA.
- **ORG-2 [T5, now]** — `profile/README.md`'s repo table lists 8 repos and omits
  `agentcontextdistributionprotocol` — the spec, the thing the org is named after. Add it as the first row.
  **Accept:** the table is a complete map of the family, spec first.

### Ground truth as of this plan (verified firsthand)

| Fact | Evidence |
|---|---|
| `profile/README.md` is 23 lines: H1 + 2-line lede, `## Repositories` (8-row table), `## Delivery` | read in full [C] |
| Prose in that file is hard-wrapped at ~80 cols; table rows are single long lines | [C] |
| `SECURITY.md` is 17 lines: `## Reporting a vulnerability`, `## Supply chain` | read in full [C] |
| The only response-time sentence is `SECURITY.md:10` — "We aim to acknowledge reports within 3 business days." | [C] |
| Repo has **no** `.github/workflows/` — no CI whatsoever | `ls .github/workflows` → No such file or directory [C] |
| Repo tree is exactly: `profile/`, `SECURITY.md`, `workflow-templates/` (+ `.git`) — no LICENSE, no dependabot, no issue templates | `ls -laR` [C] |
| Single commit in history: `.github: org profile, security policy, workflow templates` with a `- path: what` bullet body | `git log -3 --format=...` [C] |
| No `CLAUDE.md` in this repo → follow `acdp-ci/DELIVERY-STANDARD.md` conventions | `00-overview.md:75-77` [C] |
| Canonical posture paragraph lives at `00-overview.md:67-73` as an indented blockquote; 657 chars once unquoted+unwrapped; **pure ASCII** (no smart quotes) | extracted + checked [C] |

### The verbatim constraint

`00-overview.md:64-65` states the paragraph is copied **verbatim** by SPEC-5 / PY-5 / ORG-1, "adjusting only
the repo name, so three sessions don't produce three divergent postures". The paragraph names no repo other
than `acdp-rs` / `acdp-verifier-py` (which are cited as the two conformance implementations, not as "this
repo"), so **no adjustment applies here — it is copied unchanged.**

Note the canonical form in the source is a *blockquote with `> ` prefixes and hard line wraps*. "Verbatim"
therefore means **the same character sequence after stripping `> ` and unwrapping**, not a byte-identical
copy of the quoted block. The README must carry it as an ordinary paragraph (not a blockquote), hard-wrapped
to match the file's existing ~80-col prose style. The acceptance check below is wrap-insensitive by design.

The exact 657-char target string (single logical line):

```
**Project status.** ACDP is maintained by a single maintainer on a best-effort basis; changes land when a consumer needs them, with no SLA. The stable surface is the 0.1.0 / 0.2.0 / 0.3.0 Final lines, which are wire-frozen. RFC-ACDP-0015 (witness cosigning) is Draft on the 0.4.0 line and RFC-ACDP-0009 is Reserved; neither is a dependable surface until promoted. Promotion to Final requires the conformance pack to pass against two independent implementations (`acdp-rs` and `acdp-verifier-py`); the second implementation is therefore part of the protocol's governance machinery, not an optional extra. Security reports: see SECURITY.md in the org profile.
```

Do **not** retype this. Generate it mechanically from the source at edit time (Phase 1 Approach step 1).

### Explicitly out of scope

- **ORG-3** (`bump-spec-ref` workflow template) — gated on CI-2, W2 session.
- **ORG-4** (issue/PR templates + `ISSUE_TEMPLATE/config.yml` security routing; generalizing SECURITY.md's
  hardcoded `acdp-rs` advisory URL; LICENSE for `acdp-ci`+`dotgithub`; dependabot configs) — W2 session.
  **This is the ORG-1/ORG-4 seam to be careful about:** ORG-4 owns *structural* SECURITY.md work (URL
  generalization, private-reporting toggle, routing). ORG-1 owns exactly one SECURITY.md question — does it
  imply an SLA. Phase 2 below touches **only** line 10 and nothing else in that file, leaving ORG-4's edits
  conflict-free.
- Any change to `workflow-templates/`.

---

## Phase 1 — ORG-1a: maintenance-posture paragraph in the org profile

**Status:** DONE — implemented exactly as planned, no divergence. Verified PASS
(Opus verifier, round 1): verbatim match 657/657, insertions-only diff, all AC met.
**Delivers:** `profile/README.md` carries the canonical best-effort / no-SLA posture statement, character-identical to the family-plan source.
**Depends on:** nothing. (SPEC-5 is a sibling copy of the same paragraph, not a prerequisite — `00-overview.md:217` draws `SPEC-5 ──► ORG-1` as a fan-out from a shared source, and the source paragraph is already frozen in `00-overview.md:67-73`. This session does not wait on the spec session.)
**Files:** `profile/README.md` (insert only; existing lines unchanged)

### Approach

1. **Extract, don't retype.** Regenerate the paragraph from the canonical source so no transcription error
   can enter:
   ```sh
   python3 - <<'PY'
   import re
   SRC='/Users/ajitkoti/code/agentcontextdistributionprotocol/agentcontextdistributionprotocol/plans/00-overview.md'
   ls=open(SRC).read().split('\n')[66:73]          # lines 67-73, 1-indexed
   print(' '.join(re.sub(r'^\s*>\s?','',l).strip() for l in ls))
   PY
   ```
   Sanity-gate the output before using it: it must be 657 chars, start `**Project status.**`, and end
   `in the org profile.` If any of those fail, the source moved — re-read `00-overview.md` §2 and re-derive
   the line offsets rather than patching the numbers blindly.
2. **Insert as a standalone paragraph** immediately after the 2-line lede (current `README.md:3-4`) and
   before `## Repositories`, separated by blank lines.
3. **Hard-wrap to ~80 cols** to match the surrounding prose. Wrap at word boundaries only; never insert a
   line break inside a backticked token (`` `acdp-rs` ``, `` `acdp-verifier-py` ``) or between
   `**Project` and `status.**`.

### Decisions taken (and why)

- **Placement: after the lede, before `## Repositories`.** An org landing page is read top-down by someone
  deciding whether to adopt; "single maintainer, best-effort, no SLA, these lines are wire-frozen" is the
  single highest-signal fact for that decision and belongs above the repo inventory, not after it.
  Rejected: end-of-file (buried below `## Delivery`, which is CI trivia by comparison).
- **No `## Project status` heading.** The paragraph already opens with the bold run-in
  `**Project status.**`; adding a same-named `##` heading above it duplicates the label, and the run-in
  cannot be deleted without breaking the verbatim constraint. A bare paragraph after the lede reads
  correctly and keeps the file's flat structure. (The same reasoning will apply in SPEC-5 / PY-5, which is
  a further argument for consistency.)
- **"Security reports: see SECURITY.md in the org profile" is kept verbatim** even though, in the org
  profile itself, "in the org profile" is mildly self-referential. Divergence across the three copies is
  the failure mode the canonical-paragraph rule exists to prevent; a slightly redundant clause is a much
  smaller cost than three postures that drift. Also note GitHub renders `profile/README.md` at the org
  landing page, where SECURITY.md is one click away in the same repo — so the pointer is still true, just
  short.
- **Not a blockquote.** The `> ` prefixes are an artifact of quoting inside the plan file. Rendering the
  org's own posture as a quotation would misattribute it.

### Edge cases

- GitHub renders `profile/README.md` from a *different* path than it lives at (org landing page). Relative
  links break there; the file already uses absolute `https://github.com/...` links and this paragraph adds
  no links, so nothing to fix — but do not "helpfully" turn `SECURITY.md` into a relative link.
- The paragraph contains `/` and `;` inside prose but no Markdown-active characters beyond `**` and
  backticks; no escaping needed.
- Trailing-whitespace / final-newline hygiene: keep the file's existing LF endings and single trailing
  newline.

### Acceptance criteria

1. Normalizing both sides (strip `> `, collapse all runs of whitespace to a single space), the inserted
   paragraph **diff-matches the source at `00-overview.md:67-73` exactly** — zero characters different.
2. The paragraph sits between the lede and `## Repositories`, with exactly one blank line on each side.
3. No other line of `profile/README.md` is modified by this phase (`git diff` shows insertions only).
4. Every added line is ≤ 80 columns.
5. No backticked token is split across a line break.

### Tests

**There is no automated test suite and no CI in this repo** — no `.github/workflows/`, no linter config, no
build. Verification is therefore manual and scripted ad hoc:

- **Verbatim gate (the real test):**
  ```sh
  python3 - <<'PY'
  import re
  SRC='/Users/ajitkoti/code/agentcontextdistributionprotocol/agentcontextdistributionprotocol/plans/00-overview.md'
  DST='/Users/ajitkoti/code/agentcontextdistributionprotocol/dotgithub/profile/README.md'
  norm=lambda s: ' '.join(s.split())
  src=norm(' '.join(re.sub(r'^\s*>\s?','',l) for l in open(SRC).read().split('\n')[66:73]))
  body=open(DST).read()
  i=body.index('**Project status.**'); j=body.index('\n\n', i)
  dst=norm(body[i:j])
  print('MATCH' if src==dst else 'MISMATCH'); print(len(src), len(dst))
  PY
  ```
  Must print `MATCH` and `657 657`.
- **Render check:** view the PR's rendered diff on GitHub (or `gh pr view --web`) and confirm the bold
  run-in and both inline-code spans render, and no stray `>` blockquote bar appears.
- **Width check:** `awk 'length>80 {print FILENAME": "NR": "length}' profile/README.md` — table rows are
  expected to exceed 80 and are pre-existing; no *newly added* prose line may appear.

### Docs

This phase *is* the doc change. No changelog in this repo (none exists, and none is warranted for an org
profile). The family status board (`00-overview.md:137`) is maintained in the spec repo, not here — do not
edit it from this session.

---

## Phase 2 — ORG-1b: SECURITY.md response-expectation consistency

**Status:** not started
**Delivers:** `SECURITY.md` states a response expectation that cannot be read as an SLA, consistent with the posture paragraph landed in Phase 1.
**Depends on:** Phase 1 (only for narrative coherence — the SECURITY.md wording is justified by the posture statement; no file-level dependency).
**Files:** `SECURITY.md` (one line)

### The judgment (this is the deliverable of the phase, not a formality)

Current text, `SECURITY.md:10`, verbatim:

> We aim to acknowledge reports within 3 business days.

**Verdict: it needs a change — a minimal, additive one.**

Reasoning, both sides stated:

- *Argument it's already fine:* "We aim to" is explicitly aspirational. It is not "we will", not
  "guaranteed", and carries no remedy. Read strictly, it promises effort, not an outcome.
- *Argument it crosses the line (which wins):* a **specific number** is the thing a reader anchors on. In
  vulnerability-disclosure practice, "acknowledge within N business days" is the standard *form* of a
  disclosure SLA — researchers read it as the clock they may escalate against, and "we aim to" is exactly
  the hedge every real SLA also carries. More decisively: once Phase 1 puts "maintained by a single
  maintainer on a best-effort basis ... with no SLA" on the org's front page, a bare numeric commitment two
  clicks away is in **direct tension** with it. ORG-1's own accept language is "states response
  expectations consistent with best-effort rather than implying an SLA" — a naked "within 3 business days"
  does imply one.

**Recommended minimal edit — keep the existing sentence untouched, add one qualifying sentence after it:**

```
We aim to acknowledge reports within 3 business days. This is a best-effort
target from a single maintainer, not a guaranteed response time.
```

Why additive rather than a rewrite: the 3-day figure is genuinely useful expectation-setting for a
reporter (deleting it makes the policy *less* informative and helps nobody), and an additive change keeps
the diff to one line plus one sentence — the smallest edit that removes the SLA reading. It also stays
clear of every ORG-4 edit (which touches the advisory URL two lines above, not this line).

### Approach

1. Replace line 10 with the two-sentence version above, hard-wrapped at ~76-80 cols to match the file's
   existing wrap width.
2. Change nothing else — not the advisory URL (ORG-4), not the `security@zer07labs.com` address, not the
   `## Supply chain` section.

### Edge cases

- **"We" vs. a single maintainer.** The file uses the editorial "we" throughout while the posture paragraph
  says "a single maintainer". This is a cosmetic inconsistency, not an SLA implication; the added sentence
  says "a single maintainer" explicitly, which resolves the substantive part. A full pronoun sweep is
  gold-plating and would collide with ORG-4's rewrite of the same file. **Deliberately not done.**
- Do not add a *second* posture paragraph to SECURITY.md — the org profile is the single canonical site for
  it (that is what the paragraph's own last sentence points at).
- Resist the urge to bump 3 days to a vaguer "a few days": that discards information without improving the
  SLA reading, which the added sentence already fixes.

### Acceptance criteria

1. `SECURITY.md` contains the substring `not a guaranteed response time` and the phrase
   `best-effort target from a single maintainer`.
2. The original sentence `We aim to acknowledge reports within 3 business days.` survives byte-identical.
3. `git diff SECURITY.md` touches exactly the one paragraph at line 10 — the advisory URL, the email, and
   the whole `## Supply chain` section are untouched (0 changed lines outside that paragraph).
4. No claim in the file promises a remedy, a fix window, or an escalation path.

### Tests

No automated tests (see Phase 1). Verification:

- `git diff --stat SECURITY.md` → 1 file, small insertion count; `git diff SECURITY.md` reviewed by eye for
  scope.
- `grep -n "3 business days" SECURITY.md` → the original sentence still present, unaltered.
- Read the rendered file on the PR and re-ask the ORG-1 question cold: *does anything here read as a
  promise?* If yes, the phase is not done.

### Docs

Self-contained. If Phase 2's verdict had been "no change needed", that verdict itself would still have been
recorded here and cited in the PR body — the item is a judgment, and the judgment is the artifact.

---

## Phase 3 — ORG-2: complete the family repo map, spec first

**Status:** not started
**Delivers:** `profile/README.md`'s table is a complete 10-repo map of the family with the spec repo first.
**Depends on:** Phase 1 (same file; Phase 1 inserts above the table, Phase 3 rewrites the table body — sequence them to keep each commit's diff clean).
**Files:** `profile/README.md` (table body only; header row and `## Delivery` unchanged)

### Approach

Rewrite the table body to the canonical family order from `00-overview.md:22-33` §1 (specified →
implemented → consumed → infra), which is exactly the 10-repo order named in the item:

| # | Repo | Row source |
|---|---|---|
| 1 | `agentcontextdistributionprotocol` | **new** |
| 2 | `acdp-rs` | existing, description unchanged |
| 3 | `acdp-verifier-py` | existing, description unchanged |
| 4 | `acdp-registry-rs` | existing, description unchanged |
| 5 | `acdp-website` | existing, description unchanged |
| 6 | `acdp-control-plane` | existing, description unchanged |
| 7 | `acdp-playground` | existing, description unchanged |
| 8 | `acdp-ui-console` | existing, description unchanged |
| 9 | `acdp-ci` | existing, description unchanged |
| 10 | `.github` | **new** |

Only rows 1 and 10 are authored; the other eight are **moved verbatim**, descriptions untouched. Proposed
new-row text (matching the terse "What it is" register of the existing eight):

- Row 1 — `agentcontextdistributionprotocol`:
  *The specification — RFCs, conformance fixtures, and registries. The normative source for every
  implementation.*
- Row 10 — `.github`:
  *This repo — the org profile, the org-wide security policy, and shared workflow templates.*

Links are absolute `https://github.com/agentcontextdistributionprotocol/<repo>`, matching the existing rows.
Row 10's URL is `.../.github` (see decision below).

### Decisions taken (and why)

- **Order: canonical §1 family order, not minimal-diff.** The accept criterion is "a complete **map** of the
  family" — a map implies structure, not just completeness. §1's order groups by layer (spec → the two
  independent implementations → registry → the four consumers → infra), which tells a visitor how the family
  fits together; the current README order (`acdp-rs`, `acdp-registry-rs`, `acdp-control-plane`,
  `acdp-playground`, `acdp-verifier-py`, `acdp-ui-console`, `acdp-website`, `acdp-ci`) has no discernible
  logic and scatters the two conformance implementations. Reordering also makes the public map and the
  internal canonical table agree, which is worth more than a smaller diff in a 10-row table with one
  committer. *Alternative considered:* prepend row 1, append row 10, leave the middle eight in place —
  smaller diff, but preserves an arbitrary order. Recorded in Open Questions.
- **Row 10 is labelled `` `.github` ``, not `` `dotgithub` ``.** The family plan says `dotgithub` because
  that is the **local clone directory name**; the actual GitHub repo is
  `agentcontextdistributionprotocol/.github` (`git remote -v` [C]), which is mandatory — GitHub only reads
  an org profile from a repo literally named `.github`. A public-facing table must show the name a visitor
  will actually find. This is a naming reconciliation, not a scope change: the row is the `dotgithub` row
  the item asks for.
- **No new columns.** Adding a "Layer" column would encode §1's taxonomy explicitly, but §1 lives in a
  git-ignored local plan and the taxonomy has never been published; introducing it here is scope creep
  beyond "complete map, spec first". The row order carries the grouping implicitly. Two columns stay.

### Edge cases

- A row whose repo slug starts with `.` — `` [`.github`](https://github.com/.../.github) `` — renders fine
  in GitHub Markdown; the leading dot is not special inside a link label or a URL path segment. Verify in
  the rendered PR anyway.
- Pipe characters: none of the descriptions contain `|`; if a description is ever reworded to include one it
  must be escaped as `\|`.
- The `## Delivery` section already links `acdp-ci`; the table now also links it. Duplicate links are fine
  and pre-existing in kind — do not "deduplicate" by dropping the row.
- Alignment: the existing table does not pad columns to equal width, and the new rows should not either
  (mass-repadding would balloon the diff for zero rendered difference).

### Acceptance criteria

1. The table has **exactly 10 body rows**, in exactly this order:
   `agentcontextdistributionprotocol`, `acdp-rs`, `acdp-verifier-py`, `acdp-registry-rs`, `acdp-website`,
   `acdp-control-plane`, `acdp-playground`, `acdp-ui-console`, `acdp-ci`, `.github`.
2. Row 1 is the spec repo.
3. The set of repos in the table equals the set of ten in `00-overview.md` §1 — no omissions, no extras,
   no repo listed twice.
4. Every row's link resolves to `https://github.com/agentcontextdistributionprotocol/<slug>` with `<slug>`
   equal to the row's code-formatted label.
5. The eight pre-existing descriptions are **byte-identical** to their current text (only their position
   changed).
6. Header row (`| Repo | What it is |`) and separator (`|---|---|`) unchanged; column count is 2 on every
   row.

### Tests

No automated tests / no CI (see Phase 1). Verification:

```sh
cd /Users/ajitkoti/code/agentcontextdistributionprotocol/dotgithub
# 1. row count + order
grep -n '^| \[`' profile/README.md | nl
# 2. every link target matches its label
python3 - <<'PY'
import re
rows=[l for l in open('profile/README.md') if l.startswith('| [`')]
print('rows:', len(rows))
for i,l in enumerate(rows,1):
    m=re.match(r'\| \[`([^`]+)`\]\(https://github\.com/agentcontextdistributionprotocol/([^)]+)\)', l)
    assert m, l
    assert m.group(1)==m.group(2), l
    print(i, m.group(1))
PY
# 3. no repo lost or duplicated vs the canonical ten
```
Expected: `rows: 10`, labels printed in the order listed in acceptance criterion 1, no assertion failure.

Plus: confirm criterion 5 by checking `git diff` shows the eight existing rows as pure moves (identical
line content), and view the rendered table in the PR.

### Docs

This phase *is* the doc change.

---

## Long-term posture

- **The paragraph is now replicated in three places** (spec README via SPEC-5, `acdp-verifier-py` README via
  PY-5, here via ORG-1) with `00-overview.md` §2 as the only source. That is a **deliberate** duplication —
  the alternative (three repos linking to a git-ignored local plan file) is impossible, since the plan is
  not published. The maintenance cost is real: any future edit to the posture must be applied to all three
  or the family drifts. Mitigation for whoever edits it next: the source paragraph is the one in
  `00-overview.md` §2; grep the family for `**Project status.**` before changing any copy.
- **Version numbers age into lies.** The paragraph hardcodes `0.1.0 / 0.2.0 / 0.3.0 Final` and `0.4.0
  Draft`. When RFC-0015 goes Final (Wave 3, SPEC-1), this sentence becomes stale in all three repos
  simultaneously. That is a known, accepted consequence of the verbatim rule — and a reason the Wave-3
  session should treat "refresh the posture paragraph in three repos" as part of the promotion fan-out.
  Flagged here so it is not discovered as a surprise.
- **The org profile is the family's front door and has no owner-of-record process.** Nothing in this repo's
  CI (there is none) or in `acdp-ci` checks that the repo table stays complete. The eleventh repo, whenever
  it is created, will silently not appear here. A cheap future guard — a scheduled workflow diffing the
  table against the org's repo list via `gh api /orgs/.../repos` — is worth considering but is **not** part
  of ORG-1/ORG-2 and should not be smuggled into this PR.
- **This repo has no LICENSE and no dependabot config** [C]. Both are real gaps; both are explicitly ORG-4's,
  in Wave 2. Do not fix them here.

## Enterprise concerns

- **Disclosure-policy accuracy is the one place this PR carries real risk.** SECURITY.md is the document a
  security researcher relies on. Phase 2's edit *reduces* the promise it makes; that is the intent (aligning
  stated expectations with a single-maintainer reality is more honest than an unmeetable clock), but it does
  mean the org is publicly relaxing a stated response target. The change is additive and preserves the 3-day
  figure as a target, so a reporter loses no information — only the implied entitlement. Worth a sentence in
  the PR body so the decision is visible rather than buried in a diff.
- **No secrets, no credentials, no CI permissions are touched.** Nothing in this PR can affect the
  `acdp-deps-bot` App, the `v1` tag, or any publish path (`DELIVERY-STANDARD.md` §"Bot identity",
  lines 117-127).
- **Auto-merge:** `00-overview.md:76-77` forbids auto-merge on spec-adoption PRs. This is not a
  spec-adoption PR, but this repo has no CI and therefore no meaningful required checks — auto-merge would
  merge unreviewed prose. **Do not enable auto-merge; the human merges after reading the rendered diff.**
- **Public blast radius:** `profile/README.md` renders on the org's public landing page for every visitor,
  and takes effect the moment it merges — there is no staging surface. Proofread the rendered PR diff, not
  just the source.
- **Compliance/legal:** the posture paragraph is a public disclaimer of service levels. It is copied from an
  already-reviewed canonical source; do not soften, strengthen, or "clarify" it in this session.

## Open questions

None are blocking. Each has a defensible default already chosen; all are recorded as
**proposed default, pending confirmation** and can be reversed cheaply in review.

1. **Posture paragraph placement — after the lede, above `## Repositories`, with no heading.**
   *Proposed default, pending confirmation.* Alternative: a `## Project status` section at the end. Rejected
   because it buries the adoption-critical fact and duplicates the paragraph's own bold run-in label.
2. **SECURITY.md gets the additive qualifier sentence** (Phase 2 verdict).
   *Proposed default, pending confirmation.* Alternatives: (a) leave line 10 untouched — defensible, since
   "we aim to" is already a hedge, but leaves a bare number in tension with "no SLA"; (b) delete the 3-day
   figure entirely — rejected, it strips useful information from reporters. If the reviewer prefers (a),
   drop Phase 2 and note the verdict in the PR body; the rest of the PR is unaffected.
3. **Table order — canonical §1 family order (a full reorder), not prepend/append.**
   *Proposed default, pending confirmation.* The minimal-diff alternative (spec first, `.github` last,
   middle eight untouched) also satisfies the literal accept criterion. Reversal cost is one commit.
4. **Row 10 labelled `` `.github` `` rather than `` `dotgithub` ``.**
   *Proposed default, pending confirmation.* `.github` is the real repo name on GitHub and the only name a
   visitor can act on; `dotgithub` is this machine's clone directory. Low risk; flagged only because the
   family plan uses `dotgithub` throughout and the mismatch could look like an error to a reviewer reading
   both.
5. **New-row descriptions** (rows 1 and 10) are authored, not canonical — they are the only prose in this
   PR that is not copied from an approved source. Reword freely in review.

---

## Delivery

**Branch:** `org-1-org-2-maintenance-posture-and-repo-table` (matches `.drive.lock`).

**Commits** — conventional-commit style *as actually used in this repo*: the sole existing commit is
`.github: org profile, security policy, workflow templates` with a `- <path>: <what>` bullet body. That is a
scope-prefixed subject, lowercase-ish, no trailing period, imperative-adjacent. Match it; do **not**
introduce `feat:`/`docs:` prefixes this repo has never used.

| Phase | Proposed subject |
|---|---|
| 1 | `profile: state the best-effort maintenance posture` |
| 2 | `security: mark the 3-day acknowledgement as a target, not an SLA` |
| 3 | `profile: complete the repo table — spec first, all ten repos` |

Bodies use the same `- <path>: <what>` bullet form. Phase 1's body should cite the source
(`plans/00-overview.md §2, copied verbatim`) so a future reader knows the text is not free-form.

**One PR** for all three phases (ORG-1 + ORG-2 per `00-overview.md:292`). PR body should state: the
paragraph is verbatim from the canonical source and the diff-match check passed; the SECURITY.md verdict and
its reasoning; the table's 10 rows and their order; and that ORG-3/ORG-4 are deliberately untouched.
No auto-merge.

---

## Repo map

Files that matter for this work, in `/Users/ajitkoti/code/agentcontextdistributionprotocol/`:

| Path | Why it matters |
|---|---|
| `dotgithub/profile/README.md` | The org landing page — edited by all of Phase 1 and Phase 3. |
| `dotgithub/SECURITY.md` | Org-wide security policy — the ORG-1 SLA judgment (Phase 2), line 10 only. |
| `dotgithub/workflow-templates/` | `auto-merge` + `bump-acdp` stubs — **read-only here**; ORG-3 adds to it later. |
| `dotgithub/plans/org-1-org-2-maintenance-posture.md` | This plan. |
| `dotgithub/PROGRESS.md` | Live phase status + repo map for this work. |
| `agentcontextdistributionprotocol/plans/00-overview.md` | §2:64-73 the canonical posture paragraph (source of truth); §1 the canonical 10-repo order; §3 the ORG status board; §7 wave assignment. Git-ignored, local-only. |
| `agentcontextdistributionprotocol/plans/siblings/misc-siblings.md` | §ORG lines 248-273 — the ORG-1..ORG-4 item text and accept criteria. |
| `acdp-ci/DELIVERY-STANDARD.md` | The conventions this repo follows in lieu of a CLAUDE.md. |
