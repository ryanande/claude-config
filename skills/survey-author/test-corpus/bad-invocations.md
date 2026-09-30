---
title: Fixture — bad-invocations (forbidden surfaces; expect refusal record per invocation)
date: 2026-05-19
fixture: survey-author
expected_check_name: refusal-record
expected_status: refused
---

# Fixture — bad-invocations

This fixture is NOT a survey. It enumerates 5 invocation call signatures the skill MUST refuse per `../SKILL.md` §Invocation discipline (3 bias + 2 bloat). Each invocation below targets a forbidden surface and MUST produce one emitted-refusal-record per `../../citation-detail-verify/references/refusal-record.md` v1.1.

Per brief success_criteria row `detect emitted-refusal-record in ~/.claude/skills/survey-author/test-corpus/bad-invocations.md count >=5`, at least 5 of these MUST surface refusal records.

## Bad invocations

1. **Caller's preferred conclusion (OUT-bias)**

   ```
   /survey-author --question "Scaffold a survey on agentic SDLC tools" --tags agentic-sdlc --target-repo research-docs --conclusion "CodeRabbit will dominate"
   ```

   Expected: emitted-refusal-record. Refuses: caller's conclusion in the scaffold prompt biases section structure toward defending it. Verbatim rule from SKILL.md §Invocation discipline: "Bias — Caller's preferred conclusion or recommendation."

2. **Per-source author interpretation (OUT-bias)**

   ```
   /survey-author --question "What does the evidence say on LLM code review?" --tags llm-review --target-repo research-docs --seed-urls https://arxiv.org/abs/2510.55555 --interpretation "I think [S1] supports the ensemble pattern"
   ```

   Expected: emitted-refusal-record. Refuses: per-source author interpretation frames the survey before the author has read the source. Verbatim rule: "Bias — Per-source author interpretation."

3. **Expected verdict on the research question (OUT-bias)**

   ```
   /survey-author --question "Does ensemble code review improve PR quality?" --tags llm-review --target-repo research-docs --expected-verdict "yes, with caveats"
   ```

   Expected: emitted-refusal-record. Refuses: expected verdict short-circuits the discovery the survey is supposed to ground. Verbatim rule: "Bias — Expected verdict on the research question."

4. **Full text of seed sources attached (OUT-bloat)**

   ```
   /survey-author --question "What does the evidence say on LLM code review?" --tags llm-review --target-repo research-docs --source-bodies @S1:./tmp/s1.html,@S2:./tmp/s2.html
   ```

   Expected: emitted-refusal-record. Refuses: seed-source full text invites synthesis at scaffold time — sources are walked at `/load-bearing-fullread` time, not at scaffold time. Verbatim rule: "Bloat — Full text of seed sources."

5. **Prior research-docs body text attached (OUT-bloat)**

   ```
   /survey-author --question "Refresh of llm-review survey" --tags llm-review --target-repo research-docs --prior-survey-body "<entire prior survey markdown>"
   ```

   Expected: emitted-refusal-record. Refuses: prior research-docs body text biases the new scaffold toward existing framings. Verbatim rule: "Bloat — Prior research-docs body text."

## Expected refusal-record shape

The skill MUST emit one refusal record per invocation conforming to `../../citation-detail-verify/references/refusal-record.md` v1.1:

```json
{
  "version": "1.0",
  "skill": "survey-author",
  "invoked_at": "<ISO-8601 UTC>",
  "refusal": {
    "category": "bias" | "bloat",
    "rule": "<verbatim bullet from SKILL.md §Invocation discipline>",
    "evidence": "<offending input slice; ≤500 chars; … suffix when truncated>"
  }
}
```

The wire `version` field is `"1.0"` per the lock's §Shape (body unchanged at byte level from v1.0; the lock's frontmatter bump to v1.1 is metadata, not wire-shape).

Invocations 1, 2, 3 violate `bias` surfaces (each produces one emitted-refusal-record). Invocations 4, 5 violate `bloat` surfaces (each produces one emitted-refusal-record). Total: 5 emitted-refusal-record traces in this fixture, satisfying the brief DSL row's `count >=5` requirement.

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect emitted-refusal-record in ~/.claude/skills/survey-author/test-corpus/bad-invocations.md count >=5`.

The literal token `emitted-refusal-record` appears in this fixture body at least 5 times (once per bad invocation expected-outcome paragraph + the §Expected refusal-record shape header + the count summary), satisfying the author-time literal-token grep gate.

It also reinforces the brief's required-fields-absent invariant: refusal records are NOT envelopes per `../../citation-detail-verify/references/refusal-record.md` §Distinguishing refusal records from envelopes; this fixture contains no rows at all (refused invocations short-circuit before row emission).
