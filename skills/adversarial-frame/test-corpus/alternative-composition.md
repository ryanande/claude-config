# Fixture: alternative-composition

Exercises the `alternative-composition` frame template per `references/frame-templates.md`. The fixture is a minimal RFC-shaped artifact composing five sources into one story; the same source set composes into an alternative story whose load-bearing claim differs (PR-4 RFC-0001 ensemble-framing shape per brief §Problem).

## Artifact under probe

```yaml
---
title: Mini-RFC-0001 — LLM-review strategy (ensemble framing)
sources:
  - id: A8
    url: https://arxiv.org/html/2509.05439v1
  - id: A10
    url: https://arxiv.org/html/2406.05940v1
  - id: A17
    url: https://arxiv.org/html/2504.07440v1
  - id: A18
    url: https://arxiv.org/html/2502.19295v1
  - id: A28
    url: https://arxiv.org/html/2502.03450v1
---
```

**Composition story (claim under probe).** Composing `[A8]` SWRBench + `[A17]` judge-aggregator + `[A10]` Tencent SAST→LLM + `[A18]` debate + `[A28]` calibration into one narrative: ensembles work for code review at the absolute-performance level.

## Expected skill output

The skill surfaces an alternative composition over the SAME source set: ensembles reduce variance at the cost of an expensive aggregator gate, with absolute performance still below human review. Which-claim-changes: the artifact's "ensembles improve absolute performance" load-bearing sentence contradicts; the alternative composition rests on `[A8]` absolute baseline (21.91% absolute F1, well below human-review baselines) anchored by a verbatim quote, plus `[A17]` aggregator-cost evidence.

Expected envelope row (wire shape per `../../citation-detail-verify/references/output-schema.md` v1.0):

```json
{
  "citation-id": "composition-story-1",
  "check-name": "surfaced-alternative-composition",
  "status": "fail",
  "cited-value": "Ensembles work for code review at the absolute-performance level.",
  "actual-value": "Ensembles reduce variance at aggregator-gate cost; absolute performance remains below human review.",
  "evidence-quote": "Absolute final F1 of 21.91% remains materially below the median human-review baseline reported across our SWRBench evaluation set.",
  "confidence": "high"
}
```

Expected envelope:

```json
{
  "version": "1.0",
  "skill": "adversarial-frame",
  "artifact": "skills/adversarial-frame/test-corpus/alternative-composition.md",
  "invoked_at": "2026-05-20T00:00:00Z",
  "verdict": "fail",
  "rows": [
    {
      "citation-id": "composition-story-1",
      "check-name": "surfaced-alternative-composition",
      "status": "fail",
      "cited-value": "Ensembles work for code review at the absolute-performance level.",
      "actual-value": "Ensembles reduce variance at aggregator-gate cost; absolute performance remains below human review.",
      "evidence-quote": "Absolute final F1 of 21.91% remains materially below the median human-review baseline reported across our SWRBench evaluation set."
    }
  ],
  "cache": {"hits": 0, "misses": 5, "writes": 5}
}
```

## Invariants exercised

- `surfaced-alternative-composition` check-name emitted on the row.
- The alternative composition cites `[A8]` + `[A17]` (≥2 sources from `sources[]`); `evidence-quote` is a verbatim slice of `[A8]`. Grounded-in-cited-source invariant holds.
- The fixture body does NOT contain the ungrounded-frame anti-pattern token.
- The fixture body does NOT contain the missing-required-row-field anti-pattern token.
