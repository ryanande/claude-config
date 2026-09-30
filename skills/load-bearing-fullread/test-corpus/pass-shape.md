---
fixture: pass-shape
exercises: emitted-verdict-pass, output-row-with-all-required-fields, parsed-source-id-list
expected-verdict: pass
---

# Fixture — pass-shape

Invocation honoring the IN-contract; all probes survive without surfacing drift. Demonstrates `emitted-verdict-pass`, `output-row-with-all-required-fields`, and `parsed-source-id-list` semantics.

## Invocation

```
/load-bearing-fullread --artifact content/rfc/0001-llm-review-strategy.md --source-ids A1,A2
```

The skill emits `parsed-source-id-list`: `["A1", "A2"]` — the canonical comma-split of `--source-ids`.

## Artifact under probe (excerpt)

> §2.1 — Background. Recent work on transformer attention [A1] established the cross-attention mechanism. Subsequent work on long-context attention [A2] demonstrated O(n log n) scaling.

## Source A1 — survives probe

- citation-id: `[A1]`
- source-url: `https://arxiv.org/html/1706.03762v1`
- artifact framing: "transformer attention established cross-attention mechanism"
- paper framing: matches artifact framing (paper introduces transformer attention with cross-attention as a primary contribution; no relative-vs-absolute, no domain transfer, no flow inversion, no scope generalization).

## Source A2 — survives probe

- citation-id: `[A2]`
- source-url: `https://arxiv.org/html/2502.11111v1`
- artifact framing: "long-context attention demonstrated O(n log n) scaling"
- paper framing: matches artifact framing (paper reports O(n log n) attention scaling on standard long-context benchmarks; artifact context is consistent with paper scope and framing).

## Emitted envelope (excerpt)

```json
{
  "version": "1.0",
  "skill": "load-bearing-fullread",
  "artifact": "/Users/wyatt.rupp/dx-arch-meta/repos/research-docs/content/rfc/0001-llm-review-strategy.md",
  "invoked_at": "2026-05-19T18:00:00Z",
  "verdict": "pass",
  "cache": {"hits": 0, "misses": 2, "writes": 2},
  "rows": [
    {
      "citation-id": "[A1]",
      "check-name": "framing-drift-relative-vs-absolute",
      "status": "pass",
      "cited-value": "transformer attention established cross-attention mechanism",
      "actual-value": "paper framing matches; no relative-without-absolute pattern detected",
      "evidence-quote": ""
    },
    {
      "citation-id": "[A1]",
      "check-name": "framing-drift-domain-transfer",
      "status": "pass",
      "cited-value": "transformer attention established cross-attention mechanism",
      "actual-value": "paper framing matches; no domain transfer detected",
      "evidence-quote": ""
    },
    {
      "citation-id": "[A1]",
      "check-name": "framing-drift-flow-direction",
      "status": "pass",
      "cited-value": "transformer attention established cross-attention mechanism",
      "actual-value": "paper framing matches; no flow inversion detected",
      "evidence-quote": ""
    },
    {
      "citation-id": "[A1]",
      "check-name": "framing-drift-scope-mismatch",
      "status": "pass",
      "cited-value": "transformer attention established cross-attention mechanism",
      "actual-value": "paper framing matches; no scope generalization detected",
      "evidence-quote": ""
    },
    {
      "citation-id": "[A2]",
      "check-name": "framing-drift-relative-vs-absolute",
      "status": "pass",
      "cited-value": "long-context attention demonstrated O(n log n) scaling",
      "actual-value": "paper framing matches; no relative-without-absolute pattern detected",
      "evidence-quote": ""
    },
    {
      "citation-id": "[A2]",
      "check-name": "framing-drift-domain-transfer",
      "status": "pass",
      "cited-value": "long-context attention demonstrated O(n log n) scaling",
      "actual-value": "paper framing matches; no domain transfer detected",
      "evidence-quote": ""
    },
    {
      "citation-id": "[A2]",
      "check-name": "framing-drift-flow-direction",
      "status": "pass",
      "cited-value": "long-context attention demonstrated O(n log n) scaling",
      "actual-value": "paper framing matches; no flow inversion detected",
      "evidence-quote": ""
    },
    {
      "citation-id": "[A2]",
      "check-name": "framing-drift-scope-mismatch",
      "status": "pass",
      "cited-value": "long-context attention demonstrated O(n log n) scaling",
      "actual-value": "paper framing matches; no scope generalization detected",
      "evidence-quote": ""
    }
  ]
}
```

## Notes

Every row demonstrates `output-row-with-all-required-fields` — all six required fields populated per `../citation-detail-verify/references/output-schema.md` v1.0 §Required row fields. `evidence-quote` is the empty string on `pass` rows (PERMITTED per the lock); empty string is the literal `""`, never `null` or omitted.

Aggregate verdict per envelope is `pass` — all rows pass, no `fail` or `unverifiable`. The fixture's `emitted-verdict-pass` extractor target is the envelope's `verdict: pass` value.
