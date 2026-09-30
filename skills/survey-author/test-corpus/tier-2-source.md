---
title: Fixture — tier-2-source (research-blog URL classified at tier 2)
date: 2026-05-19
fixture: survey-author
expected_tier: 2
expected_status: pass
seed_url: "https://research.google/pubs/some-llm-codereview-post/"
---

# Fixture — tier-2-source

Invocation seeded with a single tier-2 candidate URL (research-blog post with methodology section). Expected: `/survey-author` runs the two-pass classifier and emits a tier-2 classification evidence trace.

## Invocation

```
/survey-author --question "What does the evidence say about industry research-blog claims on LLM code review?" --tags llm-review,industry-research --target-repo research-docs --seed-urls https://research.google/pubs/some-llm-codereview-post/
```

## Expected skill behavior

**Pass 1 — URL-pattern.** `research\.google/pubs/.+` matches the URL pattern set for tier-2 candidates per `../references/source-tier-rubric.md`.

**Pass 2 — content probe.** WebFetch on the URL returns an HTML document containing `Methodology` as a section heading and `sample size n=` followed by a numeric value within the sniff window per `../references/source-tier-rubric.md` §Tier-2 confirmation vocabulary. Pass-2 confirms.

**Disposition.** URL is classified as tier 2. The skill emits one `applied-tier-2-rubric` evidence trace into the scaffolded survey's `sources:` table (`tier: 2`) and into the Stage 3 driver check-row.

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
      "criterion-id": "applied-tier-2-rubric",
      "status": "pass",
      "evidence-quote": "URL https://research.google/pubs/... matched tier-2 pattern research.google/pubs/ ; content-probe confirmed via 'Methodology' heading + 'sample size n=' value"
    }
  ]
}
```

## Expected scaffolded survey `sources:` row

```yaml
sources:
  - id: S1
    title: "Tier-2 research-blog post"
    url: "https://research.google/pubs/some-llm-codereview-post/"
    tier: 2
```

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect applied-tier-2-rubric in ~/.claude/skills/survey-author/test-corpus/tier-2-source.md count >=1`.

The literal token `applied-tier-2-rubric` appears in this fixture body at least once (in the envelope JSON above and in the disposition paragraph), satisfying the author-time literal-token grep gate.
