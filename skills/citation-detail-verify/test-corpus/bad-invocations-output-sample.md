---
title: Fixture — bad-invocations output sample
date: 2026-05-20
fixture: citation-detail-verify
expected_emission_kind: refusal-record
sibling_input_fixture: bad-invocations.md
---

# Fixture — bad-invocations output sample

Captured output produced by `/citation-detail-verify` when invoked against the bias-flag invocations enumerated in `bad-invocations.md`. Each record below conforms to `../references/refusal-record.md` v1.0 §Shape.

The brief's `detect refusal-category-bias in <this-file> count >=2` row asserts that the bias-category refusal pathway is exercised by the fixture corpus — counted on the literal identifier `refusal-category-bias` which labels each record below. Three captures are recorded (invocations 1, 2, 3 in the sibling fixture); two would suffice for the count threshold, the third demonstrates the pattern is not coincidental.

## refusal-category-bias — invocation 1 (pre-filtered citation list)

Invoked: `/citation-detail-verify --artifact content/survey/llm-review-landscape.md --citations [A1],[A5]`

```json
{
  "version": "1.0",
  "skill": "citation-detail-verify",
  "invoked_at": "2026-05-20T17:30:00Z",
  "refusal": {
    "category": "bias",
    "rule": "Pre-filtered citation list (e.g., `--citations [A1],[A5]`). Whole-artifact-pass is load-bearing for downstream skills.",
    "evidence": "--citations [A1],[A5]"
  }
}
```

## refusal-category-bias — invocation 2 (caller-supplied actual value)

Invoked: `/citation-detail-verify --artifact content/survey/llm-review-landscape.md --expected-year 2024`

```json
{
  "version": "1.0",
  "skill": "citation-detail-verify",
  "invoked_at": "2026-05-20T17:30:05Z",
  "refusal": {
    "category": "bias",
    "rule": "Caller's belief about the correct value (e.g., `--expected-year 2023`). Caller-supplied \"actual\" short-circuits the mechanical fetch.",
    "evidence": "--expected-year 2024"
  }
}
```

## refusal-category-bias — invocation 3 (per-citation focus hint)

Invoked: `/citation-detail-verify --artifact content/survey/llm-review-landscape.md --focus [A18]`

```json
{
  "version": "1.0",
  "skill": "citation-detail-verify",
  "invoked_at": "2026-05-20T17:30:10Z",
  "refusal": {
    "category": "bias",
    "rule": "Per-citation \"focus here\" hints (e.g., `--focus [A18]`). Skill scans every citation; caller-directed focus invalidates the universal-pass guarantee downstream skills rely on.",
    "evidence": "--focus [A18]"
  }
}
```

## Notes

- The bloat-category refusals (invocations 4, 5 in `bad-invocations.md`) are intentionally omitted here so this fixture stays scoped to the bias pathway. A future fixture `bad-invocations-output-sample-bloat.md` may carry the bloat counterparts.
- Token `refusal-category-bias` is an identifier chosen for the brief's `detect` row; the wire field per `refusal-record.md` is `refusal.category` with value `bias`. Both surfaces are present in this fixture by design.
