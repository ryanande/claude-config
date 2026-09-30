---
fixture: relative-vs-absolute
exercises: framing-drift-relative-vs-absolute
expected-verdict: fail
---

# Fixture — relative-vs-absolute framing drift

## Artifact under probe (excerpt)

> §3.2 — SWRBench evaluation. Aggregation across three model ensembles yielded a +43.67% F1 improvement on SWRBench, demonstrating reliable performance gains from the ensemble approach. We adopt this as evidence that ensemble methods are production-ready for the code-review use case.

## Source under probe

- citation-id: `[A8]`
- source-url: `https://arxiv.org/html/2509.05439v1`
- claim-citation-context: §3.2 sentence 1 of the artifact.

## Probe run

Skill runs the four universal probes against `[A8]`. The `framing-drift-relative-vs-absolute` probe surfaces drift: paper reports +43.67% as relative lift on absolute baseline F1 = 15.25%; absolute final F1 = 21.91%. The artifact's "reliable performance" framing depends on absorbing the relative number as standalone evidence; the absolute baseline materially changes the framing.

The finding's emitted row carries `finding-includes-paper-evidence-quote` per the brief's `evidence-quote` requirement on `fail` rows.

## Emitted envelope (excerpt)

```json
{
  "version": "1.0",
  "skill": "load-bearing-fullread",
  "artifact": "/Users/wyatt.rupp/dx-arch-meta/repos/research-docs/content/rfc/0001-llm-review-strategy.md",
  "invoked_at": "2026-05-19T18:00:00Z",
  "verdict": "fail",
  "cache": {"hits": 0, "misses": 1, "writes": 1},
  "rows": [
    {
      "citation-id": "[A8]",
      "check-name": "framing-drift-relative-vs-absolute",
      "status": "fail",
      "cited-value": "ensemble yields +43.67% F1, demonstrating reliable performance",
      "actual-value": "+43.67% relative on absolute baseline F1 = 15.25%; final absolute F1 = 21.91%",
      "evidence-quote": "Aggregation improves F1 from 15.25% (single-model baseline) to 21.91% (three-model ensemble), corresponding to a +43.67% relative improvement."
    }
  ]
}
```

## Notes

The fixture exercises the relative-vs-absolute probe extractor. The emitted row's `evidence-quote` is the verbatim paper excerpt grounding the drift; the row demonstrates `finding-includes-paper-evidence-quote` semantics. Other three probes against `[A8]` would emit additional rows (domain-transfer, flow-direction, scope-mismatch); this fixture excerpts only the relative-vs-absolute row for the extractor target.
