# PROGRESS — ORG-1 + ORG-2 (maintenance posture & complete repo map)

**Plan:** [`plans/org-1-org-2-maintenance-posture.md`](plans/org-1-org-2-maintenance-posture.md)
**Branch:** `org-1-org-2-maintenance-posture-and-repo-table` · **one branch, one PR**
**Repo:** `dotgithub` (local dir) = `agentcontextdistributionprotocol/.github` on GitHub
**Wave:** W1-ORG · **Track:** T5 (posture & hygiene) · **Priority:** now

## Phases

| # | Phase | Item | Status |
|---|---|---|---|
| 1 | Maintenance-posture paragraph into `profile/README.md` (verbatim from canonical source) | ORG-1a | DONE |
| 2 | `SECURITY.md` — qualify the 3-day acknowledgement so it does not read as an SLA | ORG-1b | DONE |
| 3 | Repo table completed to all ten repos, spec first | ORG-2 | not started |

Sequence phases in order — 1 and 3 touch the same file in different regions.

## Phase log

### Phase 1 — 2026-08-28
- **Verdict:** PASS, round 1/1. Verifier: fresh Opus subagent (trivial/low-risk tier).
- **Why this tier:** docs-only insertion, no logic, no cross-cutting concerns.
- **Gaps:** none.
- **Files touched:** `profile/README.md` (10-line insertion, paragraph + 2 blank lines).
- **Assumptions logged:** none — plan's decisions were followed exactly, no new judgment calls made during execution.
- **Next:** Phase 2 (SECURITY.md).

### Phase 2 — 2026-08-28
- **Verdict:** PASS, round 1/1. Verifier: fresh Opus subagent (trivial/low-risk tier).
- **Why this tier:** one-sentence additive doc edit, no logic.
- **Gaps:** none (verifier flagged one nit — AC1's literal-substring wording doesn't
  account for the plan's own hard-wrap, which puts a newline between "best-effort" and
  "target"; whitespace-normalized it matches. Not a defect in the edit, a wording gap in
  the AC itself. No action needed.)
- **Files touched:** `SECURITY.md` (1 line → 2 lines, additive sentence).
- **Assumptions logged:** none — plan's judgment call (additive edit, not a rewrite) was
  followed exactly.
- **Next:** Phase 3 (repo table).

## Key decisions (details and reasoning in the plan)

- Posture paragraph goes **after the lede, above `## Repositories`, with no `##` heading** (the text opens
  with its own `**Project status.**` run-in).
- Paragraph is **copied verbatim**; no repo-name adjustment applies. Generate it mechanically from the
  source, never retype. Target: 657 chars, pure ASCII.
- **SECURITY.md does need a change** — additive only: keep "We aim to acknowledge reports within 3 business
  days." and add "This is a best-effort target from a single maintainer, not a guaranteed response time."
- Table uses the **canonical §1 family order** (spec → implementations → registry → consumers → infra), and
  labels this repo **`.github`** (its real GitHub name), not `dotgithub` (the local clone dir).
- **No CI, no tests, no linter in this repo** — verification is scripted diff/grep checks plus reading the
  rendered PR. **Do not enable auto-merge.**

## Out of scope (do not touch)

ORG-3 (`bump-spec-ref` workflow template) and ORG-4 (issue/PR templates, security routing, the hardcoded
advisory URL in SECURITY.md, LICENSE, dependabot) — both Wave 2, separate PRs. Phase 2 touches SECURITY.md
line 10 only, leaving ORG-4 conflict-free.

## Repo map

### This repo — `/Users/ajitkoti/code/agentcontextdistributionprotocol/dotgithub/`

| Path | One line |
|---|---|
| `profile/README.md` | The org landing page GitHub renders — 23 lines: H1, lede, 8-row repo table, `## Delivery`. Edited by Phases 1 and 3. |
| `SECURITY.md` | Org-wide security policy — reporting channel, the 3-day acknowledgement line (`:10`), supply-chain notes. Phase 2 edits line 10 only. |
| `workflow-templates/auto-merge.yml` + `.properties.json` | Auto-merge caller stub offered to new org repos. Read-only for this work. |
| `workflow-templates/bump-acdp.yml` + `.properties.json` | SDK-bump caller stub offered to new org repos. Read-only; ORG-3 will add a sibling `bump-spec-ref`. |
| `plans/org-1-org-2-maintenance-posture.md` | The full plan — context, three phases, acceptance criteria, open questions. |
| `PROGRESS.md` | This file. |
| *(absent)* `.github/workflows/` | **No CI exists in this repo** — verified; nothing to run, nothing to keep green. |
| *(absent)* `LICENSE`, `dependabot.yml`, `.github/ISSUE_TEMPLATE/` | Known gaps, all owned by ORG-4 in Wave 2. |

### Outside this repo (read-only sources)

| Path | One line |
|---|---|
| `../agentcontextdistributionprotocol/plans/00-overview.md` | Family plan: §2:67-73 is the canonical posture paragraph (source of truth), §1 the canonical ten-repo order, §3 the ORG status board, §7 the wave assignment. Git-ignored, local-only. |
| `../agentcontextdistributionprotocol/plans/siblings/misc-siblings.md` | §ORG (lines 248-273) — the ORG-1..ORG-4 item statements and accept criteria. |
| `../acdp-ci/DELIVERY-STANDARD.md` | The org's CI/CD and delivery conventions this repo follows in place of a CLAUDE.md. |
