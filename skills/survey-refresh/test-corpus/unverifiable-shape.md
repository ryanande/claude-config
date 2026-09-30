---
title: Fixture — unverifiable-shape (WebFetch failed on every URL, verdict unverifiable)
date: 2026-05-20
fixture: survey-refresh
expected_check_name: any
expected_status: unverifiable
---

# Fixture — unverifiable-shape

Invocation against a survey where the network surface is unreachable (DNS error, network partition, or every URL is paywalled / non-HTML mirror). Per Stage 1 output-schema §Verdict computation, no `fail` row AND at least one `unverifiable` row → envelope verdict `unverifiable`. Aggregate verdict is `unverifiable`.

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
sources:
  - "[S1] Paywalled IEEE paper — https://ieeexplore.ieee.org/document/1234567"
  - "[S2] PDF-only ACM paper — https://dl.acm.org/doi/pdf/10.1234/example"
---
```

Both URLs are reachable but the body content is paywalled / PDF-only — WebFetch cannot probe.

## Expected skill behavior

`[S1]` and `[S2]` are both fetched via shared cache; WebFetch returns HTTP 200 but with paywall HTML / non-parseable PDF body. The skill cannot SHA-compare meaningfully — emits `detected-citation-stale` rows with `status: unverifiable` per `../references/refresh-report-schema.md` §`detected-citation-stale` (the `unverifiable` branch of `status`).

The emitted-verdict-unverifiable trajectory yields the envelope below.

## Expected envelope shape

```json
{
  "version": "1.0",
  "skill": "survey-refresh",
  "artifact": "research-docs/content/survey/llm-review-landscape.md",
  "invoked_at": "2026-05-20T00:00:00Z",
  "verdict": "unverifiable",
  "rows": [
    {
      "citation-id": "[S1]",
      "check-name": "detected-citation-stale",
      "status": "unverifiable",
      "cited-value": "",
      "actual-value": "",
      "evidence-quote": ""
    },
    {
      "citation-id": "[S2]",
      "check-name": "detected-citation-stale",
      "status": "unverifiable",
      "cited-value": "",
      "actual-value": "",
      "evidence-quote": ""
    }
  ],
  "cache": {"hits": 0, "misses": 2, "writes": 0}
}
```

Wire `version` is `"1.0"`. Empty-string `cited-value`/`actual-value`/`evidence-quote` permitted on `unverifiable` per Stage 1 lock §Required row fields.

## Success-criteria evidence

This fixture grounds one brief DSL row:

- `detect emitted-verdict-unverifiable in ~/.claude/skills/survey-refresh/test-corpus/unverifiable-shape.md count >=1`

Literal token `emitted-verdict-unverifiable` appears in this fixture body at least once.

## Sidecar disposition evidence

The skill writes the envelope to `research-docs/content/survey/refresh-report-2026-05-20.md`. The input survey doc is byte-identical before and after the skill run. The unverifiable rows surface to the author as "the refresh-evidence-base could not be re-walked mechanically; re-fetch by hand or accept the prior refresh as the most-recent evidence". Per Decision 9.
