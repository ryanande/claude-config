---
title: Refresh-cadence model for /survey-author
version: 1.0
status: locked
owners: [survey-author]
consumers: [survey-author]
---

# Refresh-cadence model v1.0

Locked at Stage 3 of the research-pipeline skill family. Encodes why surveys refresh in place rather than promote-or-die or verdict-supersede. Skill-scoped; sibling skills do not consume this reference.

Per the brief at `~/dx-arch-meta/repos/research-docs/content/notes/survey-author-skill-brief.md` §Problem, external-evidence syntheses have a distinct decay model from `notes/` (promote-or-die) and `evals/` (verdict-superseded). The model name is canonical: **refresh-in-place-cadence-statement**.

## refresh-in-place-cadence-statement

A survey refreshes in place via three steps:

1. Bump the `last-refreshed:` frontmatter field to today's date.
2. Edit the body (`## Landscape`, `## Comparison`, `## Open questions`) to reflect new evidence — add rows to the `## Sources` table, retire rows whose URL no longer resolves, update cited numbers per reproduction.
3. Append one row to the `## Refresh log` table with `(date, change)` describing what changed in this refresh.

The survey's `slug` (filename) and `date:` (initial authoring date) DO NOT change across refreshes. A new survey is created (via `/survey-author`) only when the scope itself changes — and the original survey then carries `superseded-by:` pointing at the new one and `status: archived`.

This is the refresh-in-place-cadence-statement the rubric extracts: surveys refresh; they do not promote.

## Comparison to other content types

| Type | Decay model | Trigger | Disposition |
|---|---|---|---|
| `survey/` | refresh-in-place (this rubric) | `last-refreshed:` bump | edit body, append refresh-log row |
| `notes/` | promote-or-die | crystallization into a durable type | move file to `decisions/`, `design/`, `rfc/`, etc. |
| `evals/` | verdict-superseded | newer eval with better verdict | mark `superseded-by:`, flip `status: archived` |
| `design/` | refresh-on-implementation-drift | system changes vs doc | edit body in place |

Surveys are the only content type whose refresh frequency is driven by **external evidence cadence** rather than internal decision cadence. New papers and vendor work land continuously; the survey decays continuously. Other content types decay only when internal facts change.

## Refresh-log convention

The `## Refresh log` section terminates every scaffolded survey body. Format:

```markdown
## Refresh log

| Date | Change |
|---|---|
| 2026-05-19 | Initial authoring. |
```

Each refresh appends one row. No row deletions; the log is append-only so a reader can reconstruct the survey's evidence trajectory across time.

The first row on every scaffolded survey reads `Initial authoring.` with today's date.

## Why surveys do NOT promote-or-die

A survey is not a working draft. It describes the **external state of the world** at a point in time. The external state changes continuously, so the natural cadence is refresh, not promote. Promote-or-die requires a binary "is this still the same thing?" answer; for a survey on `llm-review-landscape`, the answer is always "same scope, newer evidence" — which is a refresh, not a promotion.

The contrast is important enough to encode at scaffold time. The `/survey-author` skill SHALL NOT scaffold any promote-or-die-style marker in the body (no "promote when N citations land" footer, no "die-by date" warning). Surveys age gracefully via the `status: stale` flip per `~/dx-arch-meta/repos/research-docs/content/survey/_index.md` Conventions; staleness is recoverable via refresh, not by promotion.

## Why surveys do NOT verdict-supersede

An eval ships with a verdict ("X beats Y on benchmark Z"). Newer evals with better verdicts supersede older ones. A survey ships with **no verdict** — it surfaces evidence; the decision happens in an RFC that cites the survey. Without a verdict to supersede, there is no per-row supersession trajectory for the survey itself.

If a later survey replaces the scope of an earlier one (different bounded topic, different evidence set), the older survey carries `superseded-by:` and flips `status: archived`. This is wholesale supersession, not verdict-driven supersession. The distinction matters because the wholesale path requires explicit scope change — `last-refreshed:` bumps alone never trigger archival.

## Versioning

- Major (`2.0`) — breaking change to the refresh-cadence model (e.g., adding a verdict surface to surveys would qualify; would also break `output-schema.md` §Required section structure).
- Minor (`1.1`) — additive only. New comparison rows in §Comparison to other content types. New refresh-log column convention (additive; existing columns unchanged).
- v1.0 is the locked Stage 3 contract. Skill-scoped (`owners: [survey-author]`, `consumers: [survey-author]`).
