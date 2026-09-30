---
title: Fixture — citation-stale (HTTP 200 but body SHA differs from prior-session cache)
date: 2026-05-20
fixture: survey-refresh
expected_check_name: detected-citation-stale
expected_status: fail
---

# Fixture — citation-stale

Invocation against a survey whose `sources[]` carries a URL where the host returns HTTP 200 but the body has materially changed since the prior-session cache entry. Per Decision 8, the skill computes SHA256 of the normalized body for both prior-session and current, and emits a `detected-citation-stale` row when the SHAs differ.

## Invocation

```
/survey-refresh research-docs/content/survey/llm-review-landscape.md
```

Path only.

## Pre-condition: prior-session cache entry

The shared cache at `~/.claude/skills/citation-detail-verify/cache/<key>/` was warmed in a prior session (e.g., 4 months ago) when `/citation-detail-verify` or `/survey-refresh` fetched the same URL. `<key>` is the SHA256 of the normalized URL per cache-contract §Cache key derivation. The prior `meta.json` carries `session_id: <some-earlier-session>`.

Between then and now, the venue updated the page body (e.g., the DOI page redirects to a newer paper from the same authors; the abstract now reports different numbers).

## Survey state at invocation (excerpt)

```yaml
---
title: "Landscape — LLM-based code review"
last-refreshed: 2025-11-01
sources:
  - "[S3] Vendor blog — Reviewer-Bot v1 study — https://acme.example.com/blog/study-2025"
---
```

## Expected skill behavior

1. Read frontmatter; enumerate `sources[]`.
2. WebFetch `[S3]` via shared cache → HTTP 200; cache write replaces `body` + `meta.json` with current `session_id`.
3. Per Decision 8: look for a prior-session body for the same cache key. Prior body present (from the earlier session before overwrite — see §Limitations in `../references/refresh-report-schema.md` for the v1.0 caveat).
4. Compute SHA256 of normalized body (UTF-8 lowercase, strip ASCII whitespace) for prior-session and current. SHAs differ.
5. Emit `detected-citation-stale` row per `../references/refresh-report-schema.md` §`detected-citation-stale`.
6. Aggregate verdict `fail` (at least one `fail` row).

## Expected envelope shape (relevant row)

```json
{
  "version": "1.0",
  "skill": "survey-refresh",
  "artifact": "research-docs/content/survey/llm-review-landscape.md",
  "invoked_at": "2026-05-20T00:00:00Z",
  "verdict": "fail",
  "rows": [
    {
      "citation-id": "[S3]",
      "check-name": "detected-citation-stale",
      "status": "fail",
      "cited-value": "a3f5b1c9e8d7f6a4b2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9",
      "actual-value": "9b8a7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b",
      "evidence-quote": "Reviewer-Bot v2 study — n=2400 reviews — F1=0.51 — updated methodology …"
    }
  ]
}
```

Wire `version` is `"1.0"`. `cited-value` and `actual-value` are SHA256 hex strings (64 lowercase hex chars).

## Success-criteria evidence

This fixture grounds one brief DSL row:

- `detect detected-citation-stale in ~/.claude/skills/survey-refresh/test-corpus/citation-stale.md count >=1`

Literal token `detected-citation-stale` appears in this fixture body at least once.

## Materiality-judgment evidence

The `evidence-quote` is the first 200 chars of the freshly-fetched body. The author reads the sidecar, compares the surfaced quote to the survey's quoted claim from `[S3]`, and judges whether to update the survey body. The skill produces input to that decision; it does not auto-rewrite. Per Decision 9 sidecar-only disposition.
