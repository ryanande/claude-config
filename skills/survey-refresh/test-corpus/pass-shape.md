---
title: Fixture — pass-shape (clean refresh, all rows pass, verdict pass)
date: 2026-05-20
fixture: survey-refresh
expected_check_name: any
expected_status: pass
---

# Fixture — pass-shape

Invocation honoring the IN-contract per `../SKILL.md` §Input. Every URL in `sources[]` is live, no body-SHA divergence vs prior-session cache, `## Refresh log` table consistent with frontmatter bump, no informational URL-added rows (tag set already covered by existing sources). Aggregate verdict is `pass`.

## Invocation

```
/survey-refresh research-docs/content/survey/llm-review-landscape.md
```

Path only.

## Survey state at invocation (excerpt)

```yaml
---
title: "Landscape — LLM-based code review"
last-refreshed: 2026-05-15
tags: [llm-review, code-quality]
sources:
  - "[S1] arXiv 2510.55555 — https://arxiv.org/abs/2510.55555"
---
```

`## Refresh log` table most-recent row date: `2026-05-15`. All sources URLs return HTTP 200 with bodies SHA-matching prior-session cache entries.

## Expected skill behavior

Each URL is re-fetched via the shared cache; bodies SHA-match prior-session entries. The `## Refresh log` table verification produces a `detected-last-refreshed-bumped` row with `status: pass`. No `detected-url-removed`, `detected-citation-stale`, or `detected-url-added` rows emitted (tag-set coverage check is silent when complete).

The emitted-verdict-pass trajectory yields the envelope below.

## Expected envelope shape

```json
{
  "version": "1.0",
  "skill": "survey-refresh",
  "artifact": "research-docs/content/survey/llm-review-landscape.md",
  "invoked_at": "2026-05-20T00:00:00Z",
  "verdict": "pass",
  "rows": [
    {
      "citation-id": "last-refreshed",
      "check-name": "detected-last-refreshed-bumped",
      "status": "pass",
      "cited-value": "2026-05-15",
      "actual-value": "2026-05-15",
      "evidence-quote": "| 2026-05-15 | Re-walked sources[]; bumped last-refreshed. |"
    }
  ],
  "cache": {"hits": 1, "misses": 0, "writes": 0}
}
```

Every row above is an output-row-with-all-required-fields per the Stage 1 lock §Required row fields: `citation-id` non-empty, `check-name` registered, `status` ∈ {pass, fail, unverifiable}, `cited-value`/`actual-value`/`evidence-quote` populated. Wire `version` is `"1.0"`.

## Success-criteria evidence

This fixture grounds two brief DSL rows:

- `detect emitted-verdict-pass in ~/.claude/skills/survey-refresh/test-corpus/pass-shape.md count >=1`
- `detect output-row-with-all-required-fields in ~/.claude/skills/survey-refresh/test-corpus/pass-shape.md count >=1`

Both literal tokens (`emitted-verdict-pass` and `output-row-with-all-required-fields`) appear in this fixture body at least once.

## Sidecar disposition evidence

The skill writes the envelope + a markdown summary to `research-docs/content/survey/refresh-report-2026-05-20.md`. The input survey doc is byte-identical before and after the skill run. Per Decision 9 sidecar-only disposition.
