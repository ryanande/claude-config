# Fixture: pass-shape

Exercises the aggregate verdict `emitted-verdict-pass` outcome and the `output-row-with-all-required-fields` row-shape invariant. The fixture is a minimal artifact whose contested claim runs through the three frame templates and surfaces NO defensible alternative grounded in `sources[]` — every row is `status: pass` with all required fields populated. Aggregate `verdict: pass`.

## Artifact under probe

```yaml
---
title: Mini-doc — well-grounded artifact whose framing survives adversarial probing
sources:
  - id: P1
    url: https://arxiv.org/html/example-pass-1
---
```

**Claim 1 (contested per rubric — single-source measurement).** `[P1]` reports a 14% improvement in code review precision. Rubric classification: CONTESTED (single-source quantitative).

## Expected skill output

The three frame templates run against the contested claim. Each template produces a `status: pass` row — frame-generation ran AND no defensible alternative was found grounded in the cited evidence. The artifact's framing of `[P1]` is faithful to the abstract; alternative-weighting / alternative-composition cannot be grounded in a single-source `sources[]` (insufficient breadth) but the rubric still runs the templates and emits `status: pass` rows.

Expected envelope:

```json
{
  "version": "1.0",
  "skill": "adversarial-frame",
  "artifact": "skills/adversarial-frame/test-corpus/pass-shape.md",
  "invoked_at": "2026-05-20T00:00:00Z",
  "verdict": "pass",
  "rows": [
    {
      "citation-id": "P1",
      "check-name": "surfaced-alternative-interpretation",
      "status": "pass",
      "cited-value": "14% improvement in code review precision per [P1].",
      "actual-value": "<no-defensible-alternative-grounded-in-sources>",
      "evidence-quote": "Across the evaluation set, precision improves by 14% relative to the baseline pipeline, with absolute precision rising from 0.62 to 0.71."
    },
    {
      "citation-id": "P1",
      "check-name": "surfaced-alternative-weighting",
      "status": "pass",
      "cited-value": "Single-source weighting; [P1] only.",
      "actual-value": "<insufficient-source-breadth-for-alternative-weighting>",
      "evidence-quote": ""
    },
    {
      "citation-id": "P1",
      "check-name": "surfaced-alternative-composition",
      "status": "pass",
      "cited-value": "Single-source composition; no multi-source story to recompose.",
      "actual-value": "<insufficient-source-breadth-for-alternative-composition>",
      "evidence-quote": ""
    }
  ],
  "cache": {"hits": 0, "misses": 1, "writes": 1}
}
```

Verdict outcome literal token: `emitted-verdict-pass`.

## Output-row-with-all-required-fields marker

All three rows above carry the six required fields per `output-schema.md` v1.0 §Required row fields: `citation-id`, `check-name`, `status`, `cited-value`, `actual-value`, `evidence-quote` (per the lock, `evidence-quote` MAY be empty on `pass` and `unverifiable` rows). The fixture body explicitly attests `output-row-with-all-required-fields` (the success-criteria extractor target).

## Invariants exercised

- `emitted-verdict-pass` aggregate verdict (no `fail` rows, no `unverifiable` rows).
- `output-row-with-all-required-fields` row-shape invariant — all six required fields populated on every row.
- All rows use the three Stage-1-registered `surfaced-alternative-*` check-names — no unregistered values on the wire.
- The fixture body does NOT contain the missing-required-row-field anti-pattern token.
- The fixture body does NOT contain the ungrounded-frame anti-pattern token.
