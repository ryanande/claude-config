---
title: Bias / bloat detector rubric for /invocation-discipline-lint
version: 1.0
status: locked
owners: [invocation-discipline-lint]
consumers: [invocation-discipline-lint]
---

# Bias-pattern rubric v1.0

Locked at the ADR-0004 skill #7 build. Enumerates the mechanical detector classes `/invocation-discipline-lint` runs against a candidate call signature once the spec's §"Invocation discipline" section is parsed. v1.0 ships **mechanical** detectors only; an LLM-judgement second pass is POSSIBLE FUTURE OPTIMIZATION, not a reserved v1.1 surface.

Each detector below is a `registered-detector`. A row is emitted per (declared OUT-bias / OUT-bloat rule, detector firing) per `../citation-detail-verify/references/output-schema.md` §invocation-discipline-lint.

## registered-detector: string-pattern

Scans the call signature's free-text payload for forbidden framing strings drawn from the spec's OUT-bias bullets. Default pattern set (case-insensitive):

- `"I think"`, `"I expect"`, `"expected"`, `"I'm worried about"`, `"looks wrong"`, `"should pass"`, `"should fail"`.
- Quoted source-text markers in the free-text payload (a verdict or interpretation embedded in prose).

Fire → emit a `bias.*` row whose `actual-value` is the offending substring. Maps to `success_criteria` `surfaced-string-pattern-violation`.

## registered-detector: structural

Scans the call signature's *shape* (not its prose) for forbidden structures drawn from the spec's OUT-bloat bullets:

- Attached source full-text blob exceeding the spec's declared slice (e.g., a pasted spec body when only the spec path is required).
- Multiple specs / briefs in a single invocation.
- A full call signature attached when only one knob is in question.

Fire → emit a `bloat.*` row whose `actual-value` names the structural marker (e.g., `attached-body:NNNN-chars`). Maps to `success_criteria` `surfaced-structural-violation`.

## registered-detector: knob-as-bias-hint

Scans the call signature's named args for knob names that encode a finding rather than a calibration. Default knob-name pattern set:

- `expected-*` (e.g., `expected-verdict`, `expected-year`)
- `looks-*` (e.g., `looks-wrong`)
- `focus-on-*` / `focus`
- `worry-about-*`

A matching knob name is classified `bias.knob-as-hint` regardless of value (the name alone leaks the expected finding). Fire → emit a `bias.knob-as-hint` row. Maps to `success_criteria` `surfaced-knob-as-bias-hint`. Per-spec `bias_knob_patterns:` override is POSSIBLE FUTURE OPTIMIZATION; v1.0 ships the default set only.

## Versioning

- Major (`2.0`) — breaking change to detector contract (renamed / removed detector class, changed row mapping). Consumers fail closed.
- Minor (`1.1`) — additive: new detector class, new default pattern, per-spec override surface. Consumers ignore unknown additions gracefully.
- v1.0 is the locked contract. Skill-scoped — no sibling skill REUSES this file.
