---
fixture: flow-direction
exercises: framing-drift-flow-direction
expected-verdict: fail
---

# Fixture — flow-direction framing drift

## Artifact under probe (excerpt)

> §5.3 — Static analysis composition. Tencent's hybrid SAST-LLM pipeline [A10] achieves 94-98% false-positive reduction, supporting our proposal to use LLM as primary reviewer with SAST as a downstream verifier. We adopt this composition as the reference architecture.

## Source under probe

- citation-id: `[A10]`
- source-url: `https://arxiv.org/html/2504.12345v1`
- claim-citation-context: §5.3 sentence 1 of the artifact.

## Probe run

Skill runs the four universal probes against `[A10]`. The `framing-drift-flow-direction` probe surfaces drift: paper measures LLM as **second-pass filter on SAST alarms** (direction SAST→LLM); the 94-98% FP-reduction applies to filtering pre-detected SAST alarms. Artifact maps the finding to the reverse direction (LLM→SAST), where the FP-reduction metric does not apply.

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
      "citation-id": "[A10]",
      "check-name": "framing-drift-flow-direction",
      "status": "fail",
      "cited-value": "LLM as primary reviewer with SAST as downstream verifier (LLM->SAST); 94-98% FP-reduction applies",
      "actual-value": "paper measures LLM as second-pass filter on SAST alarms (SAST->LLM); FP-reduction metric is specific to the SAST->LLM direction",
      "evidence-quote": "Our pipeline takes SAST-detected alarms as input and uses an LLM filter to remove false positives. The 94-98% false-positive reduction is measured on the SAST -> LLM filter direction; the reverse composition (LLM as primary detector) is out of scope for this study."
    }
  ]
}
```

## Notes

The fixture exercises the flow-direction probe extractor. The drift inverts the measured direction; metric values bound to one direction do not transfer to the reverse.
