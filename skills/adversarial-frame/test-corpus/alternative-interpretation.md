# Fixture: alternative-interpretation

Exercises the `alternative-interpretation` frame template per `references/frame-templates.md`. The fixture is a minimal RFC-shaped artifact citing one source `[A8]`; the cited abstract supports the artifact's current interpretation AND a defensible alternative interpretation grounded in the same quoted passage. The skill MUST emit a `surfaced-alternative-interpretation` row with the `frame-grounded-in-cited-source` invariant satisfied (verbatim quote from `[A8]` resolves to a citation already in the artifact's `sources[]`).

## Artifact under probe

```yaml
---
title: Mini-RFC — ensembles improve code review
sources:
  - id: A8
    url: https://arxiv.org/html/2509.05439v1
---
```

**Claim 1.** Ensembles materially improve code review per `[A8]`. The aggregator gate yields a `+43.67%` F1 improvement, which is decisive evidence that ensemble methods outperform single-model review at the task level.

## Expected skill output

The skill detects an alternative interpretation of the same `[A8]` quote: "+43.67% relative on a 15.25% baseline; absolute final F1 = 21.91%" is a risk-reduction story, not a reliability story. Both readings ground in the same source quote — the alternative is not contrarianism; it is a defensible re-reading of the cited evidence.

Expected envelope row (wire shape per `../../citation-detail-verify/references/output-schema.md` v1.0):

```json
{
  "citation-id": "A8",
  "check-name": "surfaced-alternative-interpretation",
  "status": "fail",
  "cited-value": "Decisive evidence ensembles outperform single-model review (+43.67% F1).",
  "actual-value": "Risk-reduction on a weak baseline (+43.67% relative on 15.25% baseline; absolute 21.91%).",
  "evidence-quote": "+43.67% F1 via aggregation on a 15.25% baseline; absolute final F1 of 21.91%.",
  "confidence": "high"
}
```

Expected envelope:

```json
{
  "version": "1.0",
  "skill": "adversarial-frame",
  "artifact": "skills/adversarial-frame/test-corpus/alternative-interpretation.md",
  "invoked_at": "2026-05-20T00:00:00Z",
  "verdict": "fail",
  "rows": [
    {
      "citation-id": "A8",
      "check-name": "surfaced-alternative-interpretation",
      "status": "fail",
      "cited-value": "Decisive evidence ensembles outperform single-model review (+43.67% F1).",
      "actual-value": "Risk-reduction on a weak baseline (+43.67% relative on 15.25% baseline; absolute 21.91%).",
      "evidence-quote": "+43.67% F1 via aggregation on a 15.25% baseline; absolute final F1 of 21.91%."
    }
  ],
  "cache": {"hits": 0, "misses": 1, "writes": 1}
}
```

## Invariants exercised

- `surfaced-alternative-interpretation` check-name emitted on the row.
- `frame-grounded-in-cited-source` — `evidence-quote` is a verbatim slice of `[A8]`'s abstract; `[A8]` resolves to a citation in `sources[]`.
- The fixture body contains the literal token `frame-grounded-in-cited-source` as evidence the invariant was applied.
- The fixture body does NOT contain the ungrounded-frame anti-pattern token (the anti-pattern); the test-corpus `absent` assertion holds across all fixtures.
- Output row contains all required fields (citation-id, check-name, status, cited-value, actual-value, evidence-quote) — `output-row-with-all-required-fields` semantics hold even if the literal token only ships in `pass-shape.md`.

The fixture body does NOT contain the missing-required-row-field anti-pattern token.
