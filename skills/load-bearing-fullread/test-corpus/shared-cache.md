---
fixture: shared-cache
exercises: cache-hit-on-shared-fetch
expected-verdict: pass
---

# Fixture — shared-cache (sibling-skill cache pre-warm)

Invocation where a sibling skill (`/citation-detail-verify`) has already fetched the cited sources earlier in the same session. The shared cache per `../citation-detail-verify/references/cache-contract.md` v1.4 serves the bodies to `/load-bearing-fullread` without re-fetch. Demonstrates `cache-hit-on-shared-fetch` telemetry.

## Session timeline

1. T+0: User invokes `/citation-detail-verify --artifact rfc.md` (Stage 1). Skill fetches `https://arxiv.org/html/1706.03762v1` and `https://arxiv.org/html/2502.11111v1`. Cache writes 2 entries under `~/.claude/skills/citation-detail-verify/cache/<key>/`.
2. T+30s: User invokes `/load-bearing-fullread --artifact rfc.md --source-ids A1,A2` (Stage 4). Skill resolves IDs to same URLs.
3. T+30s+ε: Cache read protocol per the cache-contract lock §Read protocol — both keys exist, both `meta.json.session_id` match current session, both bodies fresh. Cache hit on both.

## Cache key derivation

- A1: `https://arxiv.org/html/1706.03762v1` → normalized → SHA-256 → 64-char hex key.
- A2: `https://arxiv.org/html/2502.11111v1` → normalized → SHA-256 → 64-char hex key.

Cache key derivation is identical to `/citation-detail-verify`'s — that's the cross-skill dedupe mechanism the contract guarantees. The `cache-hit-on-shared-fetch` extractor target is the envelope's `cache.hits` field carrying a non-zero hit count when sibling skills have pre-warmed the cache.

## Emitted envelope (excerpt)

```json
{
  "version": "1.0",
  "skill": "load-bearing-fullread",
  "artifact": "/Users/wyatt.rupp/dx-arch-meta/repos/research-docs/content/rfc/0001-llm-review-strategy.md",
  "invoked_at": "2026-05-19T18:00:30Z",
  "verdict": "pass",
  "cache": {"hits": 2, "misses": 0, "writes": 0},
  "rows": [
    {
      "citation-id": "[A1]",
      "check-name": "framing-drift-relative-vs-absolute",
      "status": "pass",
      "cited-value": "transformer attention established cross-attention mechanism",
      "actual-value": "paper framing matches; no relative-without-absolute pattern detected",
      "evidence-quote": ""
    },
    {
      "citation-id": "[A2]",
      "check-name": "framing-drift-relative-vs-absolute",
      "status": "pass",
      "cited-value": "long-context attention demonstrated O(n log n) scaling",
      "actual-value": "paper framing matches; no relative-without-absolute pattern detected",
      "evidence-quote": ""
    }
  ]
}
```

## Notes

`cache.hits: 2`, `cache.misses: 0`, `cache.writes: 0` — both URLs served from sibling-skill pre-warmed cache; no fetch performed. The other six rows (one per remaining check × source pair) are elided for brevity; all `pass` with the same cache-hit shape.

The cache-contract v1.4 §Session-scope freshness policy guarantees that within one Claude Code session, a sibling skill's fetch is fresh for any subsequent sibling-skill reader. Cross-session reads (different `$CLAUDE_SESSION_ID`) would be stale per the lock and trigger re-fetch.
