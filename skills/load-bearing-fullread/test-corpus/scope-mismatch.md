---
fixture: scope-mismatch
exercises: framing-drift-scope-mismatch
expected-verdict: fail
---

# Fixture — scope-mismatch framing drift

## Artifact under probe (excerpt)

> §6.2 — Verification filter. Fix-guided Verification Filter [A8] demonstrates effective filtering of incorrect fixes, supporting our proposal to apply this filter to multi-file PR diffs as a pre-merge gate.

## Source under probe

- citation-id: `[A8]`
- source-url: `https://arxiv.org/html/2509.05439v1`
- claim-citation-context: §6.2 sentence 1 of the artifact.

## Probe run

Skill runs the four universal probes against `[A8]`. The `framing-drift-scope-mismatch` probe surfaces drift: paper tests the Fix-guided Verification Filter on **single-function benchmark code** (HumanEval / MBPP); artifact generalizes to multi-file PR diffs without flagging the input-scope limit. Methodology transfer from single-function to multi-file is unmeasured.

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
      "check-name": "framing-drift-scope-mismatch",
      "status": "fail",
      "cited-value": "Fix-guided Verification Filter applies to multi-file PR diffs as pre-merge gate",
      "actual-value": "paper tests filter on single-function benchmark code (HumanEval, MBPP); multi-file PR diff scope unmeasured",
      "evidence-quote": "We evaluate the Fix-guided Verification Filter on HumanEval and MBPP single-function benchmarks. Transfer to multi-file diff scenarios is left to future work."
    }
  ]
}
```

## Notes

The fixture exercises the scope-mismatch probe extractor. Distinct from domain-transfer (which addresses domain X vs Y) — scope-mismatch addresses methodology breadth within a domain (single-function vs multi-file, single-model vs ensemble, etc.).
