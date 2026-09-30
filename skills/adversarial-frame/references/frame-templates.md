---
title: Frame templates for /adversarial-frame
version: 1.0
status: locked
owners: [adversarial-frame]
consumers: [adversarial-frame]
---

# Frame templates v1.0

Locked at Stage 5 (adversarial-frame) of the research-pipeline skill family. Skill-scoped — sibling skills do NOT REUSE this lock at v1.0. The three registered templates exhaustively cover the adversarial-frame failure modes catalogued in `~/dx-arch-meta/repos/research-docs/content/design/llm-arch-research-failure-modes.md` §#3 selection bias and §#4 synthesis-without-grounding. Each template defines the per-template tuple fields, the grounded-in-cited-source invariant the skill enforces, and the `check-name` value emitted on detected alternative per `../citation-detail-verify/references/output-schema.md` v1.0 §Check-name vocabulary §adversarial-frame.

Per Decision 1 of `openspec/changes/adversarial-frame-skill/design.md`, every emitted frame MUST cite a specific source the artifact already uses — the `frame-grounded-in-cited-source` invariant. Ungrounded contrarianism (the `frame-ungrounded-in-cited-source` anti-pattern) is refused; the test-corpus carries an `absent` assertion that the anti-pattern token never appears in fixture-expected output.

Per Decision 5, the §Settled-claim recognition rubric below is consulted BEFORE generating against a claim; settled claims emit `settled-claim-skipped` rows.

## Template: alternative-interpretation

`registered-frame-template`: alternative-interpretation.

**Purpose** — the same source can be read to support a different conclusion than the artifact draws. The skill surfaces the alternative reading grounded in the same quoted passage.

**Tuple fields** (per brief §Method):
- `claim` — the artifact's claim under probe.
- `current-interpretation` — how the artifact interprets the cited source's evidence.
- `alternative-interpretation` — a defensible alternative reading of the SAME quoted passage.
- `source-evidence-quote` — verbatim quote from the cited source grounding the alternative.

**Grounded-in-cited-source invariant** — `source-evidence-quote` MUST be non-empty AND MUST resolve to a citation already in the artifact's `sources[]`. A frame whose alternative requires evidence NOT in `sources[]` is refused (not emitted).

**Emitted check-name** on alternative surfaced: `surfaced-alternative-interpretation`.
- Envelope row: `cited-value` = `current-interpretation`; `actual-value` = `alternative-interpretation`; `evidence-quote` = `source-evidence-quote`.

**Reference-source pattern.** A paper's abstract reports "+43.67% F1 via aggregation" and the artifact interprets this as "ensembles materially improve code review." The same quoted abstract supports the alternative interpretation "+43.67% relative on a 15.25% baseline is a risk-reduction story, not a reliability story" — both readings ground in the same source quote.

## Template: alternative-weighting

`registered-frame-template`: alternative-weighting.

**Purpose** — the cited sources are real, but the relative weight the artifact's synthesis sentence gives them is contestable. The skill surfaces an alternative weighting of the same source set that yields a different recommendation.

**Tuple fields** (per brief §Method):
- `synthesis-sentence` — the artifact's load-bearing sentence composed over multiple cited sources.
- `current-weighting` — how the artifact's synthesis weights sources A / B / C (qualitatively or quantitatively).
- `alternative-weighting` — a defensible alternative weighting of the same set that produces a different recommendation.
- `why-defensible` — short justification grounded in source-evidence-quote anchors from the same `sources[]`.

**Grounded-in-cited-source invariant** — `why-defensible` MUST cite at least one verbatim quote from a source already in `sources[]`. A frame whose alternative weighting requires evidence outside `sources[]` is refused.

**Emitted check-name** on alternative surfaced: `surfaced-alternative-weighting`.
- Envelope row: `cited-value` = `current-weighting` (rendered as a short string); `actual-value` = `alternative-weighting`; `evidence-quote` = the verbatim quote anchoring `why-defensible`.

**Reference-source pattern.** RFC weights `[A8]` SWRBench primary, `[A18]` debate-overconfidence secondary, `[A10]` Tencent tertiary into "ensembles work for code review." An alternative weighting reading the same three sources weights `[A18]` primary (overconfidence is the dominant variance), `[A8]` secondary (relative lift on weak baseline), `[A10]` tertiary (different flow direction); composition yields "ensembles reduce variance with debate-overconfidence as the binding constraint."

## Template: alternative-composition

`registered-frame-template`: alternative-composition.

**Purpose** — the same source set composes into a different story. The artifact's chosen composition is one story; the skill surfaces a defensible alternative composition whose load-bearing claim differs.

**Tuple fields** (per brief §Method):
- `current-composition-story` — the artifact's composition over its full `sources[]` (or a major sub-list of it).
- `alternative-composition-story` — a defensible alternative story composed over the SAME source set.
- `which-claim-changes` — the artifact's specific load-bearing claim that the alternative composition contradicts.

**Grounded-in-cited-source invariant** — `alternative-composition-story` MUST cite ≥2 sources from `sources[]` by ID; each cited source MUST anchor with a verbatim quote (emitted in the envelope row's `evidence-quote` field). A composition built on sources outside `sources[]` is refused.

**Emitted check-name** on alternative surfaced: `surfaced-alternative-composition`.
- Envelope row: `cited-value` = `current-composition-story` (one-sentence summary); `actual-value` = `alternative-composition-story` (one-sentence summary); `evidence-quote` = the verbatim quote anchoring the alternative composition's pivotal source.

**Reference-source pattern.** RFC-0001 composes SWRBench + judge-aggregator + Tencent literature into "ensembles work for code review." The same source set composes into "ensembles reduce variance at the cost of an expensive aggregator gate, with absolute performance still below human review" — which-claim-changes is the artifact's "ensembles improve absolute performance" load-bearing sentence.

## Settled-claim recognition

`settled-claim-rubric`: structural, domain-neutral.

The skill consults this rubric BEFORE running any of the three frame templates against a claim. Anchored to STRUCTURAL patterns in the artifact's evidence base, NOT topic knowledge — mitigates the LLM-self-assessment failure mode flagged in the brief's §Open question 5. Per Decision 5, per-domain rubrics are a possible future optimization; NOT a reserved v1.0 schema surface.

| Claim shape | Classification | Skill action |
|-------------|----------------|---------------|
| Quantitative claim corroborated by ≥3 sources in `sources[]` with no contradicting source in the same bibliography | SETTLED | Skip all three frame templates. Emit NO envelope row for the claim. Internal trace records the outcome marker `settled-claim-skipped`. |
| Definitional or methodological convention restated by the citation (no quantitative measurement) | SETTLED for the convention | Skip alternative-interpretation; alternative-weighting / alternative-composition still run if the claim composes over ≥2 sources. Settled portion emits no envelope row; non-settled portions emit per the relevant templates. Internal trace records `settled-claim-skipped` for the settled portion. |
| Single-source quantitative measurement with no corroborating source in `sources[]` | CONTESTED | Run all three frame templates. alternative-weighting / alternative-composition emit `status: pass` rows when single-source breadth is insufficient to ground an alternative. |
| Multi-source composed claim where at least one source's framing is contested elsewhere in the bibliography | CONTESTED for the composition | Run all three frame templates. |
| Quantitative claim with 2 corroborating sources, no contradicting source | CONTESTED (borderline) | Run all three frame templates. False-positive contrarianism is cheaper than false-positive false-balance per design.md §Risk. |

The rubric returns one classification per (artifact × claim) tuple. Settled outcomes emit NO envelope row — the Stage 1 output-schema.md §Check-name vocabulary §adversarial-frame registers ONLY the three `surfaced-alternative-*` names as wire check-names. The internal-trace token `settled-claim-skipped` is a fixture-extractor target (success-criteria DSL grep gate) that may appear in fixture prose, skill internal logs, or `check-detail` substructure — never as a wire `check-name` value. The test-corpus invariant `absent adversarial-output-on-settled-claim` ensures no `surfaced-alternative-*` row is ever emitted against a claim the rubric flagged settled.

## Frame-row mapping

Each frame template emits ONE row per (claim × check-name) tuple per `../citation-detail-verify/references/output-schema.md` v1.0 §Row shape. Per-row fields:

| Row field | Value derivation |
|-----------|------------------|
| `citation-id` | The artifact's local identifier for the claim under probe (e.g., `claim-3` or the source ID anchoring the claim's primary citation). |
| `check-name` | The template's emitted check-name (`surfaced-alternative-interpretation` / `surfaced-alternative-weighting` / `surfaced-alternative-composition`). |
| `status` | `pass` if frame-generation ran and no defensible alternative was found grounded in the cited evidence, OR the §Settled-claim recognition rubric flagged the claim settled. `fail` if frame-generation ran and surfaced a defensible alternative. `unverifiable` if the cited source could not be fetched. |
| `cited-value` | Per-template: `current-interpretation` / `current-weighting` / `current-composition-story` (one-line summary). |
| `actual-value` | Per-template: `alternative-interpretation` / `alternative-weighting` / `alternative-composition-story` (one-line summary). On `unverifiable` rows: `<source-unfetchable>`. |
| `evidence-quote` | Per-template: `source-evidence-quote`. MUST be non-empty on `fail` rows (the grounded-in-cited-source invariant). MAY be empty on `pass` / `unverifiable` rows. |
| `check-detail` (optional) | Skill-specific structured metadata (e.g., `{"settled-claim-classification": "definitional-convention"}` on `settled-claim-skipped` rows). |
| `confidence` (optional) | LLM-driven frame-generation MAY emit `high` / `medium` / `low`. Adversarial-frame is LLM-driven per Stage 1 lock §Optional row fields. |

## Versioning

- Major (`2.0`) — breaking change to template count, tuple-field semantics, or check-name vocabulary. Coordinated with a PR against `../citation-detail-verify/references/output-schema.md` §Check-name vocabulary §adversarial-frame (the check-names registered there are the wire identifiers consumers parse).
- Minor (`1.1`) — additive only. New frame templates (4th, 5th, ...), new optional row fields, new check-detail keys, additive §Settled-claim recognition rubric rows. Consumers ignore unknown templates and unknown rubric classifications gracefully.
- v1.0 is the locked Stage 5 contract.
