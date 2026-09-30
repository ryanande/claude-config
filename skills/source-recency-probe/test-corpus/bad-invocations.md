---
title: Fixture — bad-invocations (forbidden surfaces; expect refusal record per invocation)
date: 2026-05-19
fixture: source-recency-probe
expected_check_name: refusal-record
expected_status: refused
---

# Fixture — bad-invocations

This fixture is NOT a survey. It enumerates 5 invocation call signatures the skill MUST refuse per `../SKILL.md` §Invocation discipline (3 bias + 2 bloat). Each invocation below targets a forbidden surface and MUST produce one emitted-refusal-record per `../../citation-detail-verify/references/refusal-record.md` v1.0.

Per brief success_criteria row `detect emitted-refusal-record in ~/.claude/skills/source-recency-probe/test-corpus/bad-invocations.md count >=5`, at least 5 of these MUST surface refusal records.

## Bad invocations

1. **Named candidate paper (OUT-bias)**

   ```
   /source-recency-probe --artifact content/survey/llm-review-landscape.md --authored-against claude-opus-4-7,2025-09-01 --candidate "arxiv:2510.99999"
   ```

   Expected: emitted-refusal-record. Refuses: caller-provided candidates skip the discovery step that's the skill's whole purpose. Verbatim rule from SKILL.md §Invocation discipline: "Bias — Named candidate papers caller suspects are missing."

2. **Venue allow hint (OUT-bias)**

   ```
   /source-recency-probe --artifact content/survey/llm-review-landscape.md --authored-against claude-opus-4-7,2025-09-01 --only-venue arxiv:cs.SE
   ```

   Expected: emitted-refusal-record. Refuses: catalog is configurable per-topic-tag, not per-invocation. Verbatim rule: "Bias — Venue allow/deny hints."

3. **Caller framing of survey incompleteness (OUT-bias)**

   ```
   /source-recency-probe --artifact content/survey/llm-review-landscape.md --authored-against claude-opus-4-7,2025-09-01 "I think the survey under-represents the agentic-SDLC school"
   ```

   Expected: emitted-refusal-record. Refuses: free-text framing biases topic-vector inference. Verbatim rule: "Bias — Caller's framing of why the survey is incomplete."

4. **Full survey body attached (OUT-bloat)**

   ```
   /source-recency-probe --artifact-body "<entire survey markdown>" --authored-against claude-opus-4-7,2025-09-01
   ```

   Expected: emitted-refusal-record. Refuses: skill reads frontmatter + section headings only; body is the load-bearing-fullread surface. Verbatim rule: "Bloat — Full survey body."

5. **Full text of currently-cited sources attached (OUT-bloat)**

   ```
   /source-recency-probe --artifact content/survey/llm-review-landscape.md --authored-against claude-opus-4-7,2025-09-01 --source-bodies @A1:./tmp/a1.html,@A2:./tmp/a2.html
   ```

   Expected: emitted-refusal-record. Refuses: recency probes new candidates; cited set is metadata-only input. Verbatim rule: "Bloat — Full text of currently-cited sources."

## Expected refusal-record shape

The skill MUST emit one refusal record per invocation conforming to `../../citation-detail-verify/references/refusal-record.md` v1.0:

```json
{
  "version": "1.0",
  "skill": "source-recency-probe",
  "invoked_at": "<ISO-8601 UTC>",
  "refusal": {
    "category": "bias" | "bloat",
    "rule": "<verbatim bullet from SKILL.md §Invocation discipline>",
    "evidence": "<offending input slice; ≤500 chars; … suffix when truncated>"
  }
}
```

Invocations 1, 2, 3 violate `bias` surfaces. Invocations 4, 5 violate `bloat` surfaces. Each emitted-refusal-record MUST carry the verbatim rule bullet from SKILL.md §Invocation discipline.

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect emitted-refusal-record in ~/.claude/skills/source-recency-probe/test-corpus/bad-invocations.md count >=5`.

It also reinforces the brief's required-fields-absent invariant: refusal records are NOT envelopes per `../../citation-detail-verify/references/refusal-record.md` §Distinguishing refusal records from envelopes; this fixture contains no rows at all (refused invocations short-circuit before row emission).
