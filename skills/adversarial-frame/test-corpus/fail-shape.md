# Fixture: fail-shape

Exercises the aggregate verdict `emitted-verdict-fail` outcome. The fixture is a minimal artifact + `sources[]` with at least one alternative-interpretation / alternative-weighting / alternative-composition finding; the author must engage with each finding before the critic gate fires.

## Artifact under probe

```yaml
---
title: Mini-RFC — multi-finding draft
sources:
  - id: F1
    url: https://arxiv.org/html/example-fail-1
  - id: F2
    url: https://arxiv.org/html/example-fail-2
---
```

**Claim 1.** `[F1]` shows the technique improves measurement quality by 70% (single-source quantitative claim; rubric: CONTESTED).

**Claim 2.** Composing `[F1]` and `[F2]` yields the recommendation to adopt the technique repository-wide (multi-source composition; rubric: CONTESTED).

## Expected skill output

The skill surfaces an alternative interpretation of `[F1]` (the 70% lift is relative on a weak baseline; absolute final value is the load-bearing comparand) AND an alternative composition over `[F1]` + `[F2]` (the same source set composes into a different recommendation: pilot before repository-wide adoption). Both rows carry `status: fail`. Aggregate `verdict: fail`.

Expected envelope:

```json
{
  "version": "1.0",
  "skill": "adversarial-frame",
  "artifact": "skills/adversarial-frame/test-corpus/fail-shape.md",
  "invoked_at": "2026-05-20T00:00:00Z",
  "verdict": "fail",
  "rows": [
    {
      "citation-id": "F1",
      "check-name": "surfaced-alternative-interpretation",
      "status": "fail",
      "cited-value": "70% measurement-quality improvement, decisive.",
      "actual-value": "70% relative on a low baseline; absolute final value modest.",
      "evidence-quote": "Reported 70% improvement is relative to a baseline of 12.4 absolute units; final absolute value 21.1 units."
    },
    {
      "citation-id": "composition-story-1",
      "check-name": "surfaced-alternative-composition",
      "status": "fail",
      "cited-value": "Adopt technique repository-wide.",
      "actual-value": "Pilot on a subset; full adoption contingent on absolute-value reproducibility.",
      "evidence-quote": "Reproducibility of absolute final value depends on baseline characteristics specific to the original measurement context."
    }
  ],
  "cache": {"hits": 0, "misses": 2, "writes": 2}
}
```

Verdict outcome literal token: `emitted-verdict-fail`.

## Invariants exercised

- `emitted-verdict-fail` aggregate verdict (any `fail` row forces aggregate `fail`).
- Both fail rows carry non-empty `evidence-quote` (the grounded-in-cited-source invariant — quotes resolve to `[F1]` / `[F2]` in `sources[]`).
- The fixture body does NOT contain the ungrounded-frame anti-pattern token.
- The fixture body does NOT contain the missing-required-row-field anti-pattern token.
