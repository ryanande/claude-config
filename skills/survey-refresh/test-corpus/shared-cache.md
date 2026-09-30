---
title: Fixture — shared-cache (sibling-skill pre-warmed cache hit)
date: 2026-05-20
fixture: survey-refresh
expected_check_name: any
expected_status: pass
---

# Fixture — shared-cache

Invocation against a survey whose `sources[]` URL was pre-warmed in the cache by a sibling skill (e.g., `/citation-detail-verify` ran on a draft RFC that cited the same URL earlier in the session). Per cache-contract §Cross-skill telemetry, the cache-hit-on-shared-fetch surfaces in the envelope `cache` field.

## Invocation

```
/survey-refresh research-docs/content/survey/llm-review-landscape.md
```

Path only.

## Pre-condition: sibling-skill cache write

Earlier in the same session, `/citation-detail-verify` ran on a draft RFC and fetched `https://arxiv.org/abs/2510.55555`. The cache entry at `~/.claude/skills/citation-detail-verify/cache/<key>/` carries `meta.json.fetched_by: "citation-detail-verify"`, `session_id: <current>`. Per cache-contract §Session-scope freshness policy, the entry is fresh for the current session.

## Survey state at invocation (excerpt)

```yaml
---
title: "Landscape — LLM-based code review"
last-refreshed: 2026-05-15
sources:
  - "[S1] arXiv 2510.55555 — https://arxiv.org/abs/2510.55555"
---
```

## Expected skill behavior

1. Read frontmatter; enumerate `sources[]`.
2. WebFetch `[S1]` → cache key matches the pre-warmed entry; per cache-contract §Read protocol step 2, return the cached body. No network fetch performed.
3. SHA-compare against any prior-session entry (out of scope for this fixture — the focus is the cross-skill hit).
4. `## Refresh log` table verification → consistent. `detected-last-refreshed-bumped` row with `status: pass`.
5. Envelope `cache` field populates per cache-contract §Cross-skill telemetry: `{"hits": 1, "misses": 0, "writes": 0}`.

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

Wire `version` is `"1.0"`. `cache.hits: 1` IS the cache-hit-on-shared-fetch telemetry signal.

## Success-criteria evidence

This fixture grounds one brief DSL row:

- `detect cache-hit-on-shared-fetch in ~/.claude/skills/survey-refresh/test-corpus/shared-cache.md count >=1`

Literal token `cache-hit-on-shared-fetch` appears in this fixture body at least once.

## Cross-skill cache evidence

The cache entry was written by `/citation-detail-verify` and read by `/survey-refresh` in the same session — exactly the structural cache reuse the Stage 1 cache-contract (now v1.4) was designed to enable. The 1.0 → 1.1 amendment to the cache-contract `consumers:` list (this PR) makes `/survey-refresh` a coordination-contract first-class consumer; the cross-skill cache-hit-on-shared-fetch counts as cross-skill telemetry from this PR onward.
