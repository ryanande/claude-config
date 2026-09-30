---
title: Fixture — pass-shape (clean scaffold, all rubrics applied, verdict pass)
date: 2026-05-19
fixture: survey-author
expected_check_name: any
expected_status: pass
---

# Fixture — pass-shape

Invocation honoring the IN-contract per `../SKILL.md` §Input. Three required args + optional seed-URLs producing a clean tier-classified scaffold. Every Stage 3 driver check-row is fully populated; aggregate verdict is `pass`.

## Invocation

```
/survey-author --question "What does the evidence say about LLM-based code-review effectiveness across PR-review and code-review contexts?" --tags llm-review,code-quality --target-repo research-docs --seed-urls https://arxiv.org/abs/2510.55555,https://research.google/pubs/some-llm-codereview-post/,https://example-vendor.com/products/ai-code-reviewer/
```

Three seed URLs covering all three tiers.

## Expected skill behavior

Each URL is tier-classified per `../references/source-tier-rubric.md` two-pass classifier. All three classifications complete cleanly; the scaffolded survey is written to `research-docs/content/survey/<slug>.md`. The Stage 3 driver envelope carries three rows (one per seed URL), each populated with all three required fields per `../references/output-schema.md` §Required row fields.

The emitted-verdict-pass trajectory yields the envelope below.

## Expected envelope shape

```json
{
  "version": "1.0",
  "skill": "survey-author",
  "artifact": "research-docs/content/survey/llm-based-code-review-effectiveness.md",
  "invoked_at": "<ISO-8601 UTC>",
  "verdict": "pass",
  "rows": [
    {
      "criterion-id": "applied-tier-1-rubric",
      "status": "pass",
      "evidence-quote": "arxiv.org/abs/2510.55555 confirmed via 'Abstract' + 'DOI:' sniff"
    },
    {
      "criterion-id": "applied-tier-2-rubric",
      "status": "pass",
      "evidence-quote": "research.google/pubs/... confirmed via 'Methodology' + 'n=' sniff"
    },
    {
      "criterion-id": "applied-tier-3-rubric",
      "status": "pass",
      "evidence-quote": "example-vendor.com/products/... default tier-3 (no pass-1 match)"
    }
  ]
}
```

Every row above is an output-row-with-all-required-fields per `../references/output-schema.md` §Required row fields: `criterion-id` non-empty, `status` ∈ {pass, fail, unverifiable}, `evidence-quote` present.

## Success-criteria evidence

This fixture grounds two brief DSL rows:

- `detect emitted-verdict-pass in ~/.claude/skills/survey-author/test-corpus/pass-shape.md count >=1`
- `detect output-row-with-all-required-fields in ~/.claude/skills/survey-author/test-corpus/pass-shape.md count >=1`

Both literal tokens (`emitted-verdict-pass` and `output-row-with-all-required-fields`) appear in this fixture body at least once, satisfying the author-time literal-token grep gate.

## Corpus-wide invariant evidence

The scaffolded body that would result from this invocation contains the required sections per `../references/output-schema.md` §Required section structure: Scope, Method, Landscape, Comparison, Open questions, Sources, Refresh log. No decision-statement section appears (per §Forbidden section titles). Per the survey schema, the body terminates at the Refresh log table.
