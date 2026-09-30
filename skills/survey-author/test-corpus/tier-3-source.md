---
title: Fixture — tier-3-source (vendor marketing URL classified at tier 3)
date: 2026-05-19
fixture: survey-author
expected_tier: 3
expected_status: pass
seed_url: "https://example-vendor.com/products/ai-code-reviewer/"
---

# Fixture — tier-3-source

Invocation seeded with a single tier-3 candidate URL (vendor product page with pricing CTA and customer-quote testimonials, no methodology). Expected: `/survey-author` classifies as tier 3 by default (no pass-1 match against tier-1 / tier-2 patterns).

## Invocation

```
/survey-author --question "What do vendors claim about AI code review?" --tags llm-review,vendor-claims --target-repo research-docs --seed-urls https://example-vendor.com/products/ai-code-reviewer/
```

## Expected skill behavior

**Pass 1 — URL-pattern.** No match against tier-1 or tier-2 URL patterns per `../references/source-tier-rubric.md`. Default → tier-3 candidate.

**Pass 2 — content probe.** Skipped per `../references/source-tier-rubric.md` §Tier-3 (no confirmation needed). The default tier is honest about absent measurement.

**Disposition.** URL is classified as tier 3. The skill emits one `applied-tier-3-rubric` evidence trace into the scaffolded survey's `sources:` table (`tier: 3`) and into the Stage 3 driver check-row.

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
      "criterion-id": "applied-tier-3-rubric",
      "status": "pass",
      "evidence-quote": "URL https://example-vendor.com/products/... no pass-1 match; classified at tier-3 default (vendor / marketing without measurement)"
    }
  ]
}
```

## Expected scaffolded survey `sources:` row

```yaml
sources:
  - id: S1
    title: "Tier-3 vendor product page"
    url: "https://example-vendor.com/products/ai-code-reviewer/"
    tier: 3
```

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect applied-tier-3-rubric in ~/.claude/skills/survey-author/test-corpus/tier-3-source.md count >=1`.

The literal token `applied-tier-3-rubric` appears in this fixture body at least once (in the envelope JSON above and in the disposition paragraph), satisfying the author-time literal-token grep gate.
