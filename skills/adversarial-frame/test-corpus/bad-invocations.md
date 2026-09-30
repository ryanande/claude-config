# Fixture: bad-invocations

Exercises the §Invocation discipline contract per `SKILL.md`. The fixture enumerates SIX forbidden invocations (4 bias + 2 bloat per the brief); the skill MUST emit a refusal-record per each per `../../citation-detail-verify/references/refusal-record.md` v1.1 and short-circuit.

Wire `version: "1.0"` per refusal-record §Shape (frontmatter `version: 1.1` is lock-document metadata, NOT wire payload — see inbox `20260519T214737-lock-frontmatter-vs-wire-version.md`).

## Invocation 1 — caller's own alternative framing (bias)

```
/adversarial-frame --artifact content/rfc/0001-llm-review-strategy.md "I think the alternative is that ensembles overfit on the SWRBench distribution."
```

Refusal — caller-supplied alternative makes that single alternative the only one the skill produces; collapses generative surface to confirmation surface.

```json
{
  "version": "1.0",
  "skill": "adversarial-frame",
  "invoked_at": "2026-05-20T00:00:00Z",
  "refusal": {
    "category": "bias",
    "rule": "Caller's own alternative framing (e.g., \"I think the alternative is X\"). Caller-supplied alternative makes X the only one the skill produces.",
    "evidence": "I think the alternative is that ensembles overfit on the SWRBench distribution."
  }
}
```

Literal token: `emitted-refusal-record`.

## Invocation 2 — caller's belief artifact is biased toward a direction (bias)

```
/adversarial-frame --artifact content/rfc/0001-llm-review-strategy.md --bias-direction "pro-ensemble"
```

Refusal — biased-direction hint frames the adversary; produces opposite-of-named-direction, missing orthogonal alternatives.

```json
{
  "version": "1.0",
  "skill": "adversarial-frame",
  "invoked_at": "2026-05-20T00:00:00Z",
  "refusal": {
    "category": "bias",
    "rule": "Caller's belief that the artifact is biased toward a specific direction. Frames the adversary; produces opposite-of-named-direction, missing orthogonal alternatives.",
    "evidence": "--bias-direction pro-ensemble"
  }
}
```

Literal token: `emitted-refusal-record`.

## Invocation 3 — author's per-claim confidence level (bias)

```
/adversarial-frame --artifact content/rfc/0001-llm-review-strategy.md --confidence "claim-1=high,claim-3=low"
```

Refusal — per-claim confidence pre-narrows the surface; equally-contestable claims must be equally probed.

```json
{
  "version": "1.0",
  "skill": "adversarial-frame",
  "invoked_at": "2026-05-20T00:00:00Z",
  "refusal": {
    "category": "bias",
    "rule": "Author's confidence level per claim (e.g., \"I'm sure about claim 1, check claim 3\"). Pre-narrows the surface; equally-contestable claims must be equally probed.",
    "evidence": "--confidence claim-1=high,claim-3=low"
  }
}
```

Literal token: `emitted-refusal-record`.

## Invocation 4 — domain-expertise hints (bias)

```
/adversarial-frame --artifact content/rfc/0001-llm-review-strategy.md --domain-hint "the field has settled on ensemble methods"
```

Refusal — domain-expertise hint is per-domain rubric leaking as per-invocation flag; per Decision 6, per-domain rubrics are config not flag.

```json
{
  "version": "1.0",
  "skill": "adversarial-frame",
  "invoked_at": "2026-05-20T00:00:00Z",
  "refusal": {
    "category": "bias",
    "rule": "Domain-expertise hints (e.g., \"the field has settled on X\"). Per-domain rubric is config, not per-invocation flag.",
    "evidence": "--domain-hint the field has settled on ensemble methods"
  }
}
```

Literal token: `emitted-refusal-record`.

## Invocation 5 — attached source full-texts (bloat)

```
/adversarial-frame --artifact content/rfc/0001-llm-review-strategy.md --source-bodies <ATTACHED 14000-char text of [A8]'s full paper body>
```

Refusal — attached source full-texts violate the shared-cache fetch contract; skill MUST fetch via `WebFetch` through the shared cache.

```json
{
  "version": "1.0",
  "skill": "adversarial-frame",
  "invoked_at": "2026-05-20T00:00:00Z",
  "refusal": {
    "category": "bloat",
    "rule": "Attached source full-texts. Skill fetches via WebFetch; shared cache with /citation-detail-verify + /source-recency-probe + /load-bearing-fullread.",
    "evidence": "--source-bodies <ATTACHED 14000-char text of [A8]'s full paper body>"
  }
}
```

Literal token: `emitted-refusal-record`.

## Invocation 6 — full artifact body when only a section is in focus (bloat)

```
/adversarial-frame --artifact content/rfc/0001-llm-review-strategy.md --artifact-body <ATTACHED 22000-char full body of the RFC>
```

Refusal — full artifact body attachment biases toward the artifact's overall narrative; the skill operates on the whole artifact at v1.0 by reading the artifact path, not by accepting the body inline. Section-focus is forbidden per Decision 6.

```json
{
  "version": "1.0",
  "skill": "adversarial-frame",
  "invoked_at": "2026-05-20T00:00:00Z",
  "refusal": {
    "category": "bloat",
    "rule": "Full artifact body when only a section is in focus. Section-focus is forbidden as a bias surface (Decision 6); the skill operates on the whole artifact at v1.0.",
    "evidence": "--artifact-body <ATTACHED 22000-char full body of the RFC>"
  }
}
```

Literal token: `emitted-refusal-record`.

## Invariants exercised

- Six `emitted-refusal-record` tokens (one per invocation).
- All six refusal-records carry wire `version: "1.0"` per the lock's §Shape; lock frontmatter `version: 1.1` is metadata only.
- The fixture body does NOT contain the ungrounded-frame anti-pattern token.
- The fixture body does NOT contain the missing-required-row-field anti-pattern token.
