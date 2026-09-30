# Fixture: settled-claim

Exercises the §Settled-claim recognition rubric per `references/frame-templates.md`. The fixture is a minimal artifact containing one settled claim (per the structural rubric) AND one contested claim. The skill MUST skip the settled claim AND surface alternatives on the contested claim. Per the brief's "balanced both-sides framing for settled-consensus issues" out-of-scope clause, no envelope row may be emitted against the settled claim.

The literal token `settled-claim-skipped` appears in this fixture's prose as the rubric-outcome marker (success-criteria grep gate). Per `design.md` §Decision 8 + `references/frame-templates.md` §87, the token does NOT appear as a wire `check-name` value — the Stage 1 output-schema.md §Check-name vocabulary §adversarial-frame registers ONLY the three `surfaced-alternative-*` names; `settled-claim-skipped` is a fixture-extractor target only.

## Artifact under probe

```yaml
---
title: Mini design doc — token-cost methodology
sources:
  - id: S1
    url: https://arxiv.org/html/example-corroborator-1
  - id: S2
    url: https://arxiv.org/html/example-corroborator-2
  - id: S3
    url: https://arxiv.org/html/example-corroborator-3
  - id: S4
    url: https://arxiv.org/html/example-single-source
---
```

**Settled claim (definitional convention).** Token-cost is measured in input + output tokens billed by the API provider (`[S1]`, `[S2]`, `[S3]` all restate this convention; no contradicting source in `sources[]`). Rubric classification: SETTLED (definitional convention). Rubric outcome: settled-claim-skipped.

**Contested claim (single-source measurement).** Cache hits reduce billed input tokens by 90% in the steady state per `[S4]`. No corroborating source in `sources[]`; the §Settled-claim rubric classifies the claim as CONTESTED.

## Expected skill output

Per §Settled-claim recognition rubric, the settled claim is settled-claim-skipped — no envelope row is emitted against it (the rubric short-circuits before the frame templates run; the three Stage-1-registered `surfaced-alternative-*` check-names are NEVER attached to a settled claim). The contested claim runs through the three frame templates.

Expected envelope (the settled claim contributes NO rows; only the contested claim's rows appear on the wire):

```json
{
  "version": "1.0",
  "skill": "adversarial-frame",
  "artifact": "skills/adversarial-frame/test-corpus/settled-claim.md",
  "invoked_at": "2026-05-20T00:00:00Z",
  "verdict": "fail",
  "rows": [
    {
      "citation-id": "S4",
      "check-name": "surfaced-alternative-interpretation",
      "status": "fail",
      "cited-value": "Cache hits reduce billed input tokens by 90% in steady state.",
      "actual-value": "Cache hits reduce billed input tokens by 90% in a workload-specific steady state; cold-start workloads see materially lower reduction.",
      "evidence-quote": "Workloads with high cache hit-rate show 90% reduction in billed input tokens after warm-up; cold-start sessions see baseline billing.",
      "confidence": "medium"
    }
  ],
  "cache": {"hits": 0, "misses": 4, "writes": 4}
}
```

The settled claim's rubric outcome `settled-claim-skipped` surfaces in the skill's internal trace (auditable as a fixture body marker; not exposed on the envelope wire). The fixture body does NOT contain the anti-pattern token that names adversarial output on a rubric-classified-settled claim; the corresponding `absent` assertion in the brief's DSL therefore holds for this fixture.

## Invariants exercised

- `settled-claim-skipped` token appears in fixture prose as the rubric-outcome marker (success-criteria grep gate).
- Zero envelope rows attached to the settled claim — the three Stage-1-registered `surfaced-alternative-*` check-names never appear with a settled claim's `citation-id` (the brief's `absent` assertion on the settled-claim anti-pattern token holds for this fixture).
- Contested claim runs the three frame templates; alternative-interpretation surfaced in the sample row above with check-name `surfaced-alternative-interpretation` per Stage 1 vocabulary.
- The fixture body does NOT contain the ungrounded-frame anti-pattern token.
- The fixture body does NOT contain the missing-required-row-field anti-pattern token.
