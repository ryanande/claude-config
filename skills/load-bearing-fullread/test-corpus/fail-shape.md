---
fixture: fail-shape
exercises: emitted-verdict-fail
expected-verdict: fail
---

# Fixture — fail-shape

Invocation that surfaces at least one framing-drift finding. Demonstrates `emitted-verdict-fail` semantics — any `fail` row dominates the aggregate verdict per `../citation-detail-verify/references/output-schema.md` v1.0 §Verdict computation.

## Invocation

```
/load-bearing-fullread --artifact content/rfc/0002-ensemble-strategy.md --source-ids A8
```

## Source A8 — surfaces drift

- citation-id: `[A8]`
- source-url: `https://arxiv.org/html/2509.05439v1`
- artifact framing: "ensemble methods reliably improve F1 by +43.67%"
- paper framing: +43.67% is RELATIVE lift on absolute baseline 15.25%; absolute final 21.91%. Probe surfaces drift.

## Emitted envelope (excerpt)

```json
{
  "version": "1.0",
  "skill": "load-bearing-fullread",
  "artifact": "/Users/wyatt.rupp/dx-arch-meta/repos/research-docs/content/rfc/0002-ensemble-strategy.md",
  "invoked_at": "2026-05-19T18:00:00Z",
  "verdict": "fail",
  "cache": {"hits": 0, "misses": 1, "writes": 1},
  "rows": [
    {
      "citation-id": "[A8]",
      "check-name": "framing-drift-relative-vs-absolute",
      "status": "fail",
      "cited-value": "ensemble methods reliably improve F1 by +43.67%",
      "actual-value": "+43.67% relative on absolute baseline F1 = 15.25%; final absolute F1 = 21.91%",
      "evidence-quote": "Aggregation improves F1 from 15.25% (single-model baseline) to 21.91% (three-model ensemble), corresponding to a +43.67% relative improvement."
    },
    {
      "citation-id": "[A8]",
      "check-name": "framing-drift-domain-transfer",
      "status": "pass",
      "cited-value": "ensemble methods reliably improve F1 by +43.67%",
      "actual-value": "paper measures on SWRBench; artifact scope matches",
      "evidence-quote": ""
    },
    {
      "citation-id": "[A8]",
      "check-name": "framing-drift-flow-direction",
      "status": "pass",
      "cited-value": "ensemble methods reliably improve F1 by +43.67%",
      "actual-value": "no directional measurement in artifact context",
      "evidence-quote": ""
    },
    {
      "citation-id": "[A8]",
      "check-name": "framing-drift-scope-mismatch",
      "status": "pass",
      "cited-value": "ensemble methods reliably improve F1 by +43.67%",
      "actual-value": "artifact scope matches paper benchmark coverage",
      "evidence-quote": ""
    }
  ]
}
```

## Notes

The envelope's aggregate `verdict: fail` derives from one `fail` row. The `emitted-verdict-fail` extractor target is this `verdict` field value. Every row populates all six required fields.
