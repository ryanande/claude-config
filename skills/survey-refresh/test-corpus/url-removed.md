---
title: Fixture — url-removed (HTTP 404 on a sources[] URL)
date: 2026-05-20
fixture: survey-refresh
expected_check_name: detected-url-removed
expected_status: fail
---

# Fixture — url-removed

Invocation against a survey whose `sources[]` carries a URL whose host has retired the page (HTTP 404). The skill emits a `detected-url-removed` row with `status: fail`. Per Decision 4 of `openspec/changes/survey-refresh-skill/design.md`, every fetch passes through the shared cache so the row's evidence is auditable.

## Invocation

```
/survey-refresh research-docs/content/survey/llm-review-landscape.md
```

Path only. No optional flags.

## Survey state at invocation (excerpt)

```yaml
---
title: "Landscape — LLM-based code review"
last-refreshed: 2025-11-01
sources:
  - "[S1] arXiv 2510.55555 — LLM Reviewer Effectiveness — https://arxiv.org/abs/2510.55555"
  - "[S2] Acme Corp blog — Reviewer Bot v2 — https://acme.example.com/blog/reviewer-bot-v2"
---
```

`[S2]` host retired the URL between scaffold time and this refresh — the URL now returns HTTP 404.

## Expected skill behavior

1. Read frontmatter; enumerate `sources[]` → 2 URLs.
2. WebFetch `[S1]` → HTTP 200 → clean (no row unless SHA-compare flags stale; here no prior-session entry, no row).
3. WebFetch `[S2]` → HTTP 404 → emit `detected-url-removed` row per `../references/refresh-report-schema.md` §`detected-url-removed`.
4. `## Refresh log` table verification continues independently; out of scope for this fixture.
5. Aggregate verdict per Stage 1 output-schema §Verdict computation: at least one `fail` row present → envelope verdict `fail`.

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
      "citation-id": "[S2]",
      "check-name": "detected-url-removed",
      "status": "fail",
      "cited-value": "live",
      "actual-value": "404",
      "evidence-quote": "Not Found — the requested resource was not found on this server."
    }
  ]
}
```

Wire `version` is `"1.0"` per the Stage 1 lock §Envelope. Wire `skill` is `"survey-refresh"`.

## Success-criteria evidence

This fixture grounds one brief DSL row:

- `detect detected-url-removed in ~/.claude/skills/survey-refresh/test-corpus/url-removed.md count >=1`

Literal token `detected-url-removed` appears in this fixture body at least once, satisfying the author-time literal-token grep gate.

## Sidecar disposition evidence

The skill writes the envelope (plus markdown summary) to `research-docs/content/survey/refresh-report-2026-05-20.md`. The survey body at `research-docs/content/survey/llm-review-landscape.md` is byte-identical before and after the skill run — per Decision 9, no body mutation occurs. Brief invariant on body-mutation is honored corpus-wide.
