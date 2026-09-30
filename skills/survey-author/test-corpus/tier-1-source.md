---
title: Fixture — tier-1-source (arXiv URL classified at tier 1)
date: 2026-05-19
fixture: survey-author
expected_tier: 1
expected_status: pass
seed_url: "https://arxiv.org/abs/2510.55555"
---

# Fixture — tier-1-source

Invocation seeded with a single tier-1 candidate URL (arXiv preprint with measured results in the abstract). Expected: `/survey-author` runs the two-pass classifier per `../references/source-tier-rubric.md` §URL-pattern catalog + §Content-probe sniff vocabulary, and emits a tier-1 classification evidence trace.

## Invocation

```
/survey-author --question "What does the evidence say about LLM-based code-review effectiveness?" --tags llm-review,code-quality --target-repo research-docs --seed-urls https://arxiv.org/abs/2510.55555
```

## Expected skill behavior

**Pass 1 — URL-pattern.** `arxiv\.org/abs/.+` matches the URL pattern set for tier-1 candidates per `../references/source-tier-rubric.md`.

**Pass 2 — content probe.** WebFetch on the URL returns an HTML document containing `Abstract`, `DOI:`, and `Bibtex` substrings within the sniff window per `../references/source-tier-rubric.md` §Tier-1 confirmation vocabulary. Pass-2 confirms.

**Disposition.** URL is classified as tier 1. The skill emits one `applied-tier-1-rubric` evidence trace into the scaffolded survey's `sources:` table (`tier: 1`) and into the Stage 3 driver check-row.

## Expected envelope shape

Per `../references/output-schema.md` §Envelope shape:

```json
{
  "version": "1.0",
  "skill": "survey-author",
  "artifact": "research-docs/content/survey/<slug>.md",
  "invoked_at": "<ISO-8601 UTC>",
  "verdict": "pass",
  "rows": [
    {
      "criterion-id": "applied-tier-1-rubric",
      "status": "pass",
      "evidence-quote": "URL https://arxiv.org/abs/2510.55555 matched tier-1 pattern arxiv.org/abs/ ; content-probe confirmed via 'Abstract' + 'DOI:' substrings"
    }
  ]
}
```

## Expected scaffolded survey `sources:` row

```yaml
sources:
  - id: S1
    title: "Tier-1 arXiv preprint"
    url: "https://arxiv.org/abs/2510.55555"
    tier: 1
```

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect applied-tier-1-rubric in ~/.claude/skills/survey-author/test-corpus/tier-1-source.md count >=1`.

The literal token `applied-tier-1-rubric` appears in this fixture body at least once (in the envelope JSON above and in the disposition paragraph), satisfying the author-time literal-token grep gate per `openspec/changes/survey-author-skill/tasks.md` §8.
