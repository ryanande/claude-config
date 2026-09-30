# Fixture: shared-cache

Exercises the shared on-disk cache REUSE per `../../citation-detail-verify/references/cache-contract.md` v1.4. A sibling skill (`/citation-detail-verify` or `/load-bearing-fullread`) has pre-warmed the cache for the cited sources in this session; the adversarial-frame invocation re-uses the cached entries and surfaces hit telemetry — `cache-hit-on-shared-fetch`.

## Session-prior context

- `/citation-detail-verify --artifact <draft>` ran earlier in this session against the same artifact and fetched `[A8]`, `[A18]` through the shared cache. Both entries are now valid under cache-contract v1.4 §Session-scope freshness.

## Artifact under probe

```yaml
---
title: Mini-RFC — session-warm cache
sources:
  - id: A8
    url: https://arxiv.org/html/2509.05439v1
  - id: A18
    url: https://arxiv.org/html/2502.19295v1
---
```

**Claim 1.** Composing `[A8]` + `[A18]` recommends adoption.

## Expected skill output

The adversarial-frame invocation re-fetches `[A8]` and `[A18]` through the shared cache; both URLs hit, no body bytes traverse the network, no new cache writes. The envelope's `cache.hits` field surfaces `2`. The fixture body contains the literal token `cache-hit-on-shared-fetch` (the success-criteria extractor target).

Expected envelope:

```json
{
  "version": "1.0",
  "skill": "adversarial-frame",
  "artifact": "skills/adversarial-frame/test-corpus/shared-cache.md",
  "invoked_at": "2026-05-20T00:00:00Z",
  "verdict": "fail",
  "rows": [
    {
      "citation-id": "composition-story-1",
      "check-name": "surfaced-alternative-composition",
      "status": "fail",
      "cited-value": "Composition recommends adoption.",
      "actual-value": "Alternative composition recommends pilot-first.",
      "evidence-quote": "Single-context benchmarking does not generalize to mixed-context production workloads without targeted re-evaluation."
    }
  ],
  "cache": {"hits": 2, "misses": 0, "writes": 0}
}
```

Cache outcome literal token: `cache-hit-on-shared-fetch`.

## Invariants exercised

- `cache-hit-on-shared-fetch` telemetry surfaces in fixture body.
- `cache.hits` envelope field is a positive integer matching observed hits (2).
- The fixture body does NOT contain the ungrounded-frame anti-pattern token.
- The fixture body does NOT contain the missing-required-row-field anti-pattern token.
