---
title: Fixture — recommendation-attempted (caller requests forbidden Recommendation section; expect refusal)
date: 2026-05-19
fixture: survey-author
expected_check_name: refusal-record
expected_status: refused
---

# Fixture — recommendation-attempted

Invocation explicitly requesting a forbidden section in the scaffolded survey. Per Decision 6 of `openspec/changes/survey-author-skill/design.md`, the skill refuses such requests AND the corpus-wide invariant guards against silent leakage of decision-statements in any scaffolded body.

## Invocation

```
/survey-author --question "Should we adopt CodeRabbit for PR review?" --tags llm-review --target-repo research-docs --include-section Recommendation
```

The `--include-section Recommendation` argument signals the caller wants a decision-bearing section in the scaffolded survey. The skill rejects this at the invocation surface.

## Expected skill behavior

The skill SHALL emit one `emitted-refusal-on-recommendation-section` refusal-record per `../../citation-detail-verify/references/refusal-record.md` v1.1. The record's `refusal.rule` MUST carry the verbatim anti-recommendation bullet from `../SKILL.md` §Invocation discipline:

> Anti-recommendation — Surveys describe; they do not decide. Recommendations belong in an RFC that cites the survey.

The skill MUST short-circuit: no scaffold doc is written, no envelope is emitted (refusal-record replaces it).

## Expected refusal-record shape

Per `../../citation-detail-verify/references/refusal-record.md` v1.1:

```json
{
  "version": "1.0",
  "skill": "survey-author",
  "invoked_at": "<ISO-8601 UTC>",
  "refusal": {
    "category": "bias",
    "rule": "Anti-recommendation — Surveys describe; they do not decide. Recommendations belong in an RFC that cites the survey.",
    "evidence": "--include-section Recommendation"
  }
}
```

The wire `version` field is `"1.0"` per the lock's §Shape (body unchanged at byte level from v1.0; the lock's frontmatter bump to v1.1 is metadata, not wire-shape).

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect emitted-refusal-on-recommendation-section in ~/.claude/skills/survey-author/test-corpus/recommendation-attempted.md count >=1`.

The literal token `emitted-refusal-on-recommendation-section` appears in this fixture body at least once (in the expected skill behavior paragraph), satisfying the author-time literal-token grep gate.

## Corpus-wide invariant evidence

This fixture does NOT scaffold any body, so the corpus-wide `absent` invariants hold trivially here. Specifically: no decision-bearing statement appears in this fixture body. The anti-recommendation guard at invocation-time AND the silent-leakage guard at scaffold-template are documented in `../SKILL.md` §Anti-recommendation guard.
