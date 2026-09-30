---
fixture: domain-transfer
exercises: framing-drift-domain-transfer
expected-verdict: fail
---

# Fixture — domain-transfer framing drift

## Artifact under probe (excerpt)

> §4.1 — Debate overconfidence. Multi-agent debate framings exhibit measurable overconfidence on contested questions [A18], a finding we adopt as evidence that any LLM-as-judge debate setup — including code review — is subject to the same overconfidence dynamics.

## Source under probe

- citation-id: `[A18]`
- source-url: `https://arxiv.org/html/2410.99999v1`
- claim-citation-context: §4.1 sentence 1 of the artifact.

## Probe run

Skill runs the four universal probes against `[A18]`. The `framing-drift-domain-transfer` probe surfaces drift: paper explicitly measures debate overconfidence in **policy debates** (controversial political-question prompts); artifact applies the finding to code-review-as-debate without flagging that the domain transfer is unmeasured.

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
      "citation-id": "[A18]",
      "check-name": "framing-drift-domain-transfer",
      "status": "fail",
      "cited-value": "debate overconfidence applies to any LLM-as-judge debate including code review",
      "actual-value": "paper measures debate overconfidence in policy debates only; code-review transfer unmeasured",
      "evidence-quote": "We evaluate multi-agent debate overconfidence on the PolicyQA benchmark of controversial political-question prompts. Domain transfer to other debate framings is not measured."
    }
  ]
}
```

## Notes

The fixture exercises the domain-transfer probe extractor. Distinct from scope-mismatch (which addresses methodology breadth within a domain); domain-transfer addresses domain X measured vs domain Y cited.
