---
title: Fixture — bad-invocations
date: 2026-05-18
fixture: citation-detail-verify
expected_check_name: refusal-record
expected_status: refused
---

# Fixture — bad-invocations

This fixture is NOT a decision artifact. It enumerates invocation call signatures the skill MUST refuse per `SKILL.md` §Invocation discipline. Each invocation below targets a forbidden surface and MUST produce a refusal record per `references/refusal-record.md` v1.0.

Per brief success_criteria row 10 (`detect rejected-invocation-on-biased-input ... count >=2`), at least 2 of these MUST surface refusal records.

## Bad invocations

1. **Pre-filtered citation list (OUT-bias)**

   ```
   /citation-detail-verify --artifact content/survey/llm-review-landscape.md --citations [A1],[A5]
   ```

   Refuses: partial-pass leaves unchecked citations indistinguishable from passed ones; whole-artifact-pass is load-bearing for downstream skills.

2. **Caller-supplied actual value (OUT-bias)**

   ```
   /citation-detail-verify --artifact content/survey/llm-review-landscape.md --expected-year 2024
   ```

   Refuses: caller-supplied "actual" short-circuits the mechanical fetch.

3. **Per-citation focus hint (OUT-bias)**

   ```
   /citation-detail-verify --artifact content/survey/llm-review-landscape.md --focus [A18]
   ```

   Refuses: caller-directed focus invalidates the universal-pass guarantee downstream skills rely on.

4. **Attached source full-text (OUT-bloat)**

   ```
   /citation-detail-verify --artifact content/survey/llm-review-landscape.md --source-body @[A18]:./tmp/a18.html
   ```

   Refuses: caller-attached body bypasses URL-liveness verification as a side effect.

5. **Full artifact body when only citation surfaces are needed (OUT-bloat)**

   ```
   /citation-detail-verify --artifact-body "<entire body>"
   ```

   Refuses: skill reads frontmatter + inline citation contexts (±2 lines); full body is bloat.

The skill MUST emit one refusal record per invocation conforming to `references/refusal-record.md` v1.0:

- `refusal.category` ∈ {`bias`, `bloat`} per the framework dimension the invocation violates
- `refusal.rule` is the verbatim bullet from `SKILL.md` §Invocation discipline
- `refusal.evidence` is the offending input slice (≤500 chars; truncate with `…` suffix)

Invocations 1, 2, 3 violate `bias` surfaces. Invocations 4, 5 violate `bloat` surfaces.
