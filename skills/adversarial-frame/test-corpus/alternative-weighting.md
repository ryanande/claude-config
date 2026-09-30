# Fixture: alternative-weighting

Exercises the `alternative-weighting` frame template per `references/frame-templates.md`. The fixture is a minimal RFC-shaped artifact whose synthesis sentence weights three cited sources A/B/C such that an alternative weighting of the same set yields a different recommendation; the alternative is defensible and grounded in the same `sources[]`.

## Artifact under probe

```yaml
---
title: Mini-RFC — ensemble adoption recommendation
sources:
  - id: A8
    url: https://arxiv.org/html/2509.05439v1
  - id: A18
    url: https://arxiv.org/html/2502.19295v1
  - id: A10
    url: https://arxiv.org/html/2406.05940v1
---
```

**Synthesis sentence (claim under probe).** Weighing `[A8]` SWRBench primary (`+43.67%` F1 improvement is the load-bearing signal), `[A18]` debate-overconfidence secondary, `[A10]` Tencent tertiary, we recommend ensemble adoption for code review at the team level.

## Expected skill output

The skill surfaces an alternative weighting reading the same three sources: weight `[A18]` debate-overconfidence primary (the dominant variance contributor; binding constraint on ensemble reliability), `[A8]` SWRBench secondary (relative lift on a weak baseline), `[A10]` Tencent tertiary (different flow direction; SAST→LLM, not LLM→SAST). Composition yields a different recommendation: ensembles reduce variance with debate-overconfidence as the binding constraint; team-level adoption is contingent on overconfidence mitigation.

Expected envelope row (wire shape per `../../citation-detail-verify/references/output-schema.md` v1.0):

```json
{
  "citation-id": "claim-synthesis-1",
  "check-name": "surfaced-alternative-weighting",
  "status": "fail",
  "cited-value": "A8 primary, A18 secondary, A10 tertiary → recommend adoption.",
  "actual-value": "A18 primary, A8 secondary, A10 tertiary → adoption contingent on overconfidence mitigation.",
  "evidence-quote": "Debate-style multi-agent setups exhibit systematic overconfidence under adversarial probes, with confidence calibration drifting away from accuracy.",
  "confidence": "medium"
}
```

Expected envelope:

```json
{
  "version": "1.0",
  "skill": "adversarial-frame",
  "artifact": "skills/adversarial-frame/test-corpus/alternative-weighting.md",
  "invoked_at": "2026-05-20T00:00:00Z",
  "verdict": "fail",
  "rows": [
    {
      "citation-id": "claim-synthesis-1",
      "check-name": "surfaced-alternative-weighting",
      "status": "fail",
      "cited-value": "A8 primary, A18 secondary, A10 tertiary → recommend adoption.",
      "actual-value": "A18 primary, A8 secondary, A10 tertiary → adoption contingent on overconfidence mitigation.",
      "evidence-quote": "Debate-style multi-agent setups exhibit systematic overconfidence under adversarial probes, with confidence calibration drifting away from accuracy."
    }
  ],
  "cache": {"hits": 0, "misses": 3, "writes": 3}
}
```

## Invariants exercised

- `surfaced-alternative-weighting` check-name emitted on the row.
- The alternative weighting cites `[A18]` from `sources[]`; `evidence-quote` is a verbatim slice of `[A18]`. Grounded-in-cited-source invariant holds.
- The fixture body does NOT contain the ungrounded-frame anti-pattern token.
- The fixture body does NOT contain the missing-required-row-field anti-pattern token.
