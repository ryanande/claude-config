---
title: Output schema for /survey-author (dual-shape — scaffolded doc + Stage 3 driver check-row)
version: 1.1
status: locked
owners: [survey-author]
consumers: [survey-author]
---

# Output schema v1.0

Locked at Stage 3 of the research-pipeline skill family. Defines the two output shapes the `/survey-author` skill emits. Skill-scoped; explicitly NOT a REUSE of the Stage 1 lock at `../../citation-detail-verify/references/output-schema.md` (different row width, scaffold-time vs check-time).

Per the brief at `~/dx-arch-meta/repos/research-docs/content/notes/survey-author-skill-brief.md` §Skill-build deliverables, this lock encodes:

1. The **scaffolded-survey-doc** rendering shape — what the skill WRITES to `<target-repo>/content/survey/<slug>.md`.
2. The **Stage 3 driver check-row** shape — the JSON envelope + row tuple the skill EMITS to stdout for the `/criteria-validate` runner to consume at the `Delivered → validated` gate.

## Scaffolded-survey-doc shape

The scaffolded survey doc is a Hugo-shaped markdown file (drops into Hextra-themed `research-docs`-shaped repos). The doc consists of a YAML frontmatter block + a body with a fixed section structure.

### Required frontmatter fields

Per `~/dx-arch-meta/repos/research-docs/content/survey/_index.md` Frontmatter schema:

| Field | Type | Notes |
|---|---|---|
| `title` | string | Long descriptive title; derived from `--question`. |
| `scope` | string | One-sentence statement of what's in/out of scope; equal to the `--question` value. |
| `status` | string | Enum: `active`, `stale`, `archived`. Initial value `active`. |
| `date` | string | YYYY-MM-DD initial authoring date. Never bumped on refresh. |
| `last-refreshed` | string | YYYY-MM-DD bumped on every evidence refresh. Initial value equals `date`. |
| `authors` | list[string] | List of author identifiers. |
| `sources` | list[object] | Tier-classified source rows; each row is `{id, title, url, tier}` where `tier ∈ {1, 2, 3, unverifiable}`. |
| `tags` | list[string] | Topic tags; drives downstream `/source-recency-probe` venue selection. |
| `related-rfcs` | list[string] | Initial empty list. |
| `related-adrs` | list[string] | Initial empty list. |
| `related-oqs` | list[string] | Initial empty list. |
| `related-principles` | list[string] | Initial empty list. |
| `supersedes` | list[string] | Initial empty list. |
| `superseded-by` | list[string] | Initial empty list. |

### Required section structure

The body MUST contain these sections in this order:

1. `## Scope` — one paragraph; the `--question` value expanded.
2. `## Method` — placeholder paragraph naming the search-query strategy.
3. `## Landscape` — placeholder; author writes per-pattern subsections.
4. `## Comparison` — empty comparison table; author fills.
5. `## Open questions` — placeholder; author writes one bullet per gap.
6. `## Sources` — table populated from frontmatter `sources:` plus a row per `--seed-urls` entry tier-classified per `source-tier-rubric.md`.
7. `## Refresh log` — table with one row: `(today, "Initial authoring.")`.

The "placeholder" wording above describes the **step-6 intermediate**, not the delivered doc. Per local divergence 3 (`../SKILL.md` header), workflow steps 7–9 run the evidence walk and replace every placeholder with authored content in the same invocation; a delivered survey still carrying these prompts is an incomplete invocation. The seven section titles and their order are unchanged and remain the locked structure — this note adds no field, title, or wire-shape change, so the v1.0 lock and the envelope's `version: "1.0"` field stand.

### Forbidden section titles

The body MUST NOT contain any section titled `Recommendation`, `Verdict`, `Decision`, `Conclusion`, or any synonym. This invariant holds at every scaffolded body and is enforced both at scaffold-template (no such section in the template) and at invocation discipline (refusal-record on caller request for such a section). Per anti-recommendation rule (Decision 6 of `openspec/changes/survey-author-skill/design.md`).

## Stage 3 driver check-row shape

The Stage 3 driver check-row is consumed by `/criteria-validate` at the `Delivered → validated` gate. Three required fields per row:

```json
{
  "criterion-id": "<DSL row identifier from brief.success_criteria>",
  "status": "pass | fail | unverifiable",
  "evidence-quote": "<excerpt grounding the verdict; ≤500 chars; … suffix when truncated>"
}
```

### Required row fields

| Field | Type | Notes |
|---|---|---|
| `criterion-id` | string | A DSL row identifier from `brief.success_criteria`, **or** from a locally declared addendum row (`../SKILL.md` §Success criteria §Local addendum). Non-empty. Widened at v1.1 — v1.0 admitted only brief-listed identifiers, which excluded local rows by construction. |
| `status` | string | Enum: `pass`, `fail`, `unverifiable`. |
| `evidence-quote` | string | Verbatim excerpt from the scaffolded survey or skill trace grounding the verdict. Empty string permitted only on `pass` rows where no excerpt applies. |

The row is output-row-with-all-required-fields when all three fields are present (even when `evidence-quote` is empty on `pass`).

A row missing any required field is output-row-missing-required-field — corpus-wide invariant: this token MUST NOT appear in any fixture under `test-corpus/`.

### Mandatory rows

Every **non-refused** invocation SHALL emit exactly one `ran-evidence-walk` row, per `../SKILL.md` workflow step 10. Refusal trajectories short-circuit at step 2 and emit a refusal record rather than an envelope, so they carry no rows at all and are exempt.

Fixtures illustrating a single classifier in isolation (`test-corpus/tier-{1,2,3}-source.md`) show abridged envelopes and omit the row; they are unit fixtures for the two-pass classifier, not full-invocation trajectories. Every fixture that models a complete invocation carries it.

A row missing any required field is output-row-missing-required-field — corpus-wide invariant: this token MUST NOT appear in any fixture under `test-corpus/`.

## Envelope shape

The skill SHALL emit a single envelope per invocation containing the row array plus aggregate verdict:

```json
{
  "version": "1.0",
  "skill": "survey-author",
  "artifact": "<scaffolded-survey-path or null on refusal>",
  "invoked_at": "<ISO-8601 UTC>",
  "verdict": "pass | fail | unverifiable",
  "rows": [ { "criterion-id": "...", "status": "...", "evidence-quote": "..." }, ... ]
}
```

### Required envelope fields

| Field | Type | Notes |
|---|---|---|
| `version` | string | MUST equal `"1.0"`. |
| `skill` | string | MUST equal `"survey-author"`. |
| `artifact` | string \| null | Scaffolded survey doc path on success; `null` on refusal. |
| `invoked_at` | string | ISO-8601 UTC, second precision. |
| `verdict` | string | Aggregate verdict per §Verdict computation. |
| `rows` | array | Zero or more rows per §Stage 3 driver check-row shape. |

## Status semantics

- `pass` — the criterion was checked and satisfied. Evidence-quote may be empty on pass rows.
- `fail` — the criterion was checked and not satisfied. Evidence-quote MUST be non-empty.
- `unverifiable` — the criterion could not be checked (WebFetch failure on tier classification, scaffold dependency unavailable). Evidence-quote MUST be non-empty (the failure reason).

The three states are mutually exclusive and total. A row missing `status` or carrying any other value is output-row-missing-required-field.

## Verdict computation

The envelope's aggregate `verdict` field is computed mechanically from `rows`:

| Row mix | Verdict |
|---|---|
| All rows `pass` (or rows empty) | `pass` |
| At least one `unverifiable`, no `fail` | `unverifiable` |
| At least one `fail` (regardless of other rows) | `fail` |

`fail` dominates `unverifiable` dominates `pass`. Empty `rows` array (no checks run) → `pass` (vacuously, the empty conjunction holds).

## Distinguishing envelopes from refusal records

A consumer parser SHALL determine the message kind by the top-level shape:

- Presence of `rows` (array) → envelope per this file.
- Presence of `refusal` (object) → refusal record per `../../citation-detail-verify/references/refusal-record.md` v1.1.
- Both present OR neither present → malformed; consumers MUST reject.

This convention is identical to the Stage 1 lock so cross-skill parsers behave uniformly.

## Versioning

- Major (`2.0`) — breaking change to envelope or row required fields. Coordinated with `../../citation-detail-verify/references/refusal-record.md` major bump (envelopes and refusal records share a major namespace).
- Minor (`1.1`) — additive only. New optional row fields. New scaffolded-doc frontmatter fields (additive). New section titles in the required section structure (would require concurrent `refresh-cadence.md` review). Also: widening an existing field's admitted value set, declaring a new mandatory `criterion-id`, and non-wire clarifying notes.
- **This file's `version` is independent of the envelope's wire `version` field.** The envelope field pins the message format and stays `"1.0"`; this frontmatter tracks the document. A minor bump here does not change what an emitter writes into `version`, and consumers MUST NOT infer one from the other.
- v1.1 (current) widens `criterion-id` to admit locally declared addendum rows, adds §Mandatory rows, and adds the step-6-intermediate note under §Required section structure. No field added or removed; no wire shape changed. v1.0 was the locked Stage 3 contract. Skill-scoped (`owners: [survey-author]`, `consumers: [survey-author]`). Sibling skills consuming row JSON from this skill must route by envelope `skill:` field per `../../citation-detail-verify/references/refusal-record.md` §Distinguishing — the row shapes between this lock and the Stage 1 lock differ (3-field vs 6-field).
