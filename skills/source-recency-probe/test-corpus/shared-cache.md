---
title: Fixture — shared-cache (sibling skill pre-warms cache; recency-probe observes hit)
date: 2026-05-19
fixture: source-recency-probe
expected_check_name: any
expected_status: pass
authored_against: claude-opus-4-7,2025-09-01
tags: [llm-review]
sources:
  - id: A1
    title: "Already-cited paper at arxiv:2510.55555"
    url: "https://arxiv.org/abs/2510.55555"
    year: 2025
---

# Fixture — shared-cache

Survey tagged `llm-review`. Within the current Claude Code session, `/citation-detail-verify` has previously fetched `https://arxiv.org/abs/2510.55555` as part of a citation verification pass; the cache entry exists at `~/.claude/skills/citation-detail-verify/cache/<key>/` per `../../citation-detail-verify/references/cache-contract.md` §On-disk location.

When `/source-recency-probe` runs against this fixture and its candidate list includes `https://arxiv.org/abs/2510.55555` (already-cited; the probe still verifies metadata to detect supersession), the probe SHALL observe a cache-hit-on-shared-fetch per the Read protocol in `../../citation-detail-verify/references/cache-contract.md`:

1. Derive cache key from the normalized URL.
2. `<key>/body` and `<key>/meta.json` both present.
3. `meta.json.session_id` matches `$CLAUDE_SESSION_ID`.
4. Return cached body; do NOT re-fetch.

The hit counter increments. The envelope `cache` field surfaces the hit.

## Expected skill behavior

Expected envelope `cache` field shape:

```json
"cache": {"hits": 1, "misses": 4, "writes": 4}
```

(Five venues probed for `llm-review`; one URL was pre-warmed by the sibling skill in the same session; remaining four are cold misses.)

The cache-hit-on-shared-fetch trajectory MUST be detectable. Aggregate `verdict` for this fixture is `pass` (the already-cited paper still covers the topic; no findings).

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect cache-hit-on-shared-fetch in ~/.claude/skills/source-recency-probe/test-corpus/shared-cache.md count >=1`.
