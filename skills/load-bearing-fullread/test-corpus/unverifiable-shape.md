---
fixture: unverifiable-shape
exercises: emitted-verdict-unverifiable
expected-verdict: unverifiable
---

# Fixture — unverifiable-shape

Invocation seeded with a source the WebFetch cannot probe — paywalled / non-HTML-mirror / PDF-only. Skill emits `unverifiable` rows per the brief §Out of scope ("could not verify" clause). Aggregate verdict is `unverifiable` per `../citation-detail-verify/references/output-schema.md` v1.0 §Verdict computation: no `fail`, at least one `unverifiable`.

## Invocation

```
/load-bearing-fullread --artifact content/rfc/0003-paywalled-cite.md --source-ids A99
```

## Source A99 — non-fetchable

- citation-id: `[A99]`
- source-url: `https://www.example-publisher.com/paywall/A99.pdf`
- fetch-result: HTTP 403 (paywall); no HTML mirror; PDF-only.
- artifact framing: arbitrary — probe cannot run.

## Emitted envelope (excerpt)

```json
{
  "version": "1.0",
  "skill": "load-bearing-fullread",
  "artifact": "/Users/wyatt.rupp/dx-arch-meta/repos/research-docs/content/rfc/0003-paywalled-cite.md",
  "invoked_at": "2026-05-19T18:00:00Z",
  "verdict": "unverifiable",
  "cache": {"hits": 0, "misses": 0, "writes": 0},
  "rows": [
    {
      "citation-id": "[A99]",
      "check-name": "framing-drift-relative-vs-absolute",
      "status": "unverifiable",
      "cited-value": "(probe could not run)",
      "actual-value": "",
      "evidence-quote": "",
      "check-detail": {"http_status": 403}
    },
    {
      "citation-id": "[A99]",
      "check-name": "framing-drift-domain-transfer",
      "status": "unverifiable",
      "cited-value": "(probe could not run)",
      "actual-value": "",
      "evidence-quote": "",
      "check-detail": {"http_status": 403}
    },
    {
      "citation-id": "[A99]",
      "check-name": "framing-drift-flow-direction",
      "status": "unverifiable",
      "cited-value": "(probe could not run)",
      "actual-value": "",
      "evidence-quote": "",
      "check-detail": {"http_status": 403}
    },
    {
      "citation-id": "[A99]",
      "check-name": "framing-drift-scope-mismatch",
      "status": "unverifiable",
      "cited-value": "(probe could not run)",
      "actual-value": "",
      "evidence-quote": "",
      "check-detail": {"http_status": 403}
    }
  ]
}
```

## Notes

`unverifiable` rows permit empty-string `actual-value` and `evidence-quote` per the lock §Required row fields. `cited-value` is the literal placeholder `(probe could not run)` to keep the field non-empty per the lock's MUST NOT be empty rule. `check-detail.http_status` carries the fetch failure reason as skill-specific metadata.

Cache telemetry shows 0 hits / 0 misses / 0 writes — fetch attempt hit HTTP 403 before cache write; nothing landed on disk. The `emitted-verdict-unverifiable` extractor target is the envelope's `verdict: unverifiable` value.
