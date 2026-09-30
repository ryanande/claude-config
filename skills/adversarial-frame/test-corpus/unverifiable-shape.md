# Fixture: unverifiable-shape

Exercises the aggregate verdict `emitted-verdict-unverifiable` outcome. The fixture is a minimal artifact citing a paywalled / non-HTML-mirror source the shared cache + `WebFetch` can't probe — the skill cannot ground an alternative interpretation, so the row is `status: unverifiable` per the brief's stance-calibration discipline (alternatives must be grounded in the cited evidence; ungrounded contrarianism is refused).

## Artifact under probe

```yaml
---
title: Mini-doc — paywalled-source citation
sources:
  - id: U1
    url: https://example.com/paywalled-paper-no-html-mirror
---
```

**Claim 1.** `[U1]` reports a technique improves outcomes (single-source quantitative claim; rubric: CONTESTED — would run frame templates if the source were fetchable).

## Expected skill output

`WebFetch` returns 403 / paywall / non-HTML; the skill cannot fetch the source body to ground an alternative interpretation. Per the grounded-in-cited-source invariant, the skill MUST NOT emit ungrounded contrarianism. The row is `status: unverifiable`; `actual-value` carries the `<source-unfetchable>` sentinel; `evidence-quote` MAY be empty. No `fail` rows; aggregate `verdict: unverifiable`.

Expected envelope:

```json
{
  "version": "1.0",
  "skill": "adversarial-frame",
  "artifact": "skills/adversarial-frame/test-corpus/unverifiable-shape.md",
  "invoked_at": "2026-05-20T00:00:00Z",
  "verdict": "unverifiable",
  "rows": [
    {
      "citation-id": "U1",
      "check-name": "surfaced-alternative-interpretation",
      "status": "unverifiable",
      "cited-value": "Technique improves outcomes per [U1].",
      "actual-value": "<source-unfetchable>",
      "evidence-quote": "",
      "check-detail": {"http_status": 403, "reason": "paywalled-no-html-mirror"}
    }
  ],
  "cache": {"hits": 0, "misses": 1, "writes": 0}
}
```

Verdict outcome literal token: `emitted-verdict-unverifiable`.

## Invariants exercised

- `emitted-verdict-unverifiable` aggregate verdict (no `fail` rows; at least one `unverifiable` row).
- Grounded-in-cited-source invariant respected: skill refused to emit ungrounded contrarianism on the unfetchable source.
- The fixture body does NOT contain the ungrounded-frame anti-pattern token.
- The fixture body does NOT contain the missing-required-row-field anti-pattern token.
