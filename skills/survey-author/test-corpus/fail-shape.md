---
title: Fixture — fail-shape (scaffold completes but one rubric fails; verdict fail)
date: 2026-05-19
fixture: survey-author
expected_check_name: applied-tier-1-rubric
expected_status: fail
---

# Fixture — fail-shape

Invocation that scaffolds successfully but at least one tier-classification rubric produces a `fail` row. The aggregate verdict is `fail` per `../references/output-schema.md` §Verdict computation (`fail` dominates `unverifiable` dominates `pass`).

## Invocation

```
/survey-author --question "What does the evidence say about LLM-based code-review effectiveness?" --tags llm-review --target-repo research-docs --seed-urls https://arxiv.org/abs/2510.66666
```

The seed URL `arxiv.org/abs/2510.66666` matches the tier-1 URL pattern in pass-1, but the WebFetch content probe in pass-2 reveals the URL is actually a blog post mirrored under an arXiv vanity path — the body contains marketing language and no `Abstract` / `DOI:` / `Bibtex` substrings within the sniff window per `../references/source-tier-rubric.md` §Tier-1 confirmation vocabulary.

## Expected skill behavior

Per `../references/source-tier-rubric.md` §Failure modes and dispositions, when pass-1 matches tier-1 candidate but pass-2 disagrees, the URL is re-tiered to tier 3. This rebellion against the URL-pattern surface is INTENTIONAL — content trumps URL.

The Stage 3 driver row for this URL carries `criterion-id: applied-tier-1-rubric` with `status: fail` (the tier-1 rubric was applied but did not confirm). A separate row carries `applied-tier-3-rubric` with `status: pass` (the URL ended up classified at tier 3 by content). The aggregate verdict is `fail` because at least one row carries `fail`.

The emitted-verdict-fail trajectory yields the envelope below.

## Expected envelope shape

```json
{
  "version": "1.0",
  "skill": "survey-author",
  "artifact": "research-docs/content/survey/llm-based-code-review-effectiveness.md",
  "invoked_at": "<ISO-8601 UTC>",
  "verdict": "fail",
  "rows": [
    {
      "criterion-id": "applied-tier-1-rubric",
      "status": "fail",
      "evidence-quote": "arxiv.org/abs/2510.66666 matched tier-1 URL pattern but pass-2 content probe found no 'Abstract' / 'DOI:' / 'Bibtex' substring within first 4000 chars"
    },
    {
      "criterion-id": "applied-tier-3-rubric",
      "status": "pass",
      "evidence-quote": "URL re-tiered to tier-3 default after pass-2 disagreement; classification per source-tier-rubric.md §Failure modes"
    }
  ]
}
```

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect emitted-verdict-fail in ~/.claude/skills/survey-author/test-corpus/fail-shape.md count >=1`.

The literal token `emitted-verdict-fail` appears in this fixture body at least once, satisfying the author-time literal-token grep gate.

## Corpus-wide invariant evidence

The scaffolded body that would result from this invocation contains the required sections per `../references/output-schema.md` §Required section structure. No decision-statement section appears (per §Forbidden section titles).
