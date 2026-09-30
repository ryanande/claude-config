---
title: Fixture — pass-shape (clean probe, no findings, verdict pass)
date: 2026-05-19
fixture: source-recency-probe
expected_check_name: probed-no-candidates
expected_status: pass
authored_against: claude-opus-4-7,2025-09-01
sources:
  - id: A1
    title: "Already-cited tier-1 paper covering the topic"
    url: "https://arxiv.org/abs/2510.55555"
    year: 2025
  - id: A2
    title: "Second already-cited paper covering the topic"
    url: "https://doi.org/10.1145/3597503.3639125"
    year: 2024
---

# Fixture — pass-shape

Refreshed to v2.0 semantics. Two declared sources, both resolved on the citation graph and both fully walked; every citer in the window is either already present in `sources[]` (dropped by the dedupe step) or falls outside it. Path A runs for the arXiv source A1 and yields nothing clearing the two-token title filter. No findings; no probe failures.

Under v1 this fixture asserted an empty `rows` array with `verdict: pass`. That shape is now **forbidden** for an artifact with a non-empty `sources[]`: it collapses *"probed, found nothing"* into *"never probed"*. A clean probe is an all-`pass` envelope of `probed-no-candidates` rows.

## Expected skill behavior

Per `../../citation-detail-verify/references/output-schema.md` §Verdict computation and §Status semantics:

- Every entry in `sources[]` yields at least one row, so `rows` is never empty here.
- Each resolved source that yielded no surviving candidate emits exactly one `probed-no-candidates` row at `status: pass`.
- Every row is `pass` → aggregate `verdict: pass`.

The expected emitted-verdict-pass trajectory yields an envelope shape:

```json
{
  "version": "1.0",
  "skill": "source-recency-probe",
  "artifact": "<this-fixture-path>",
  "invoked_at": "<ISO-8601 UTC>",
  "verdict": "pass",
  "rows": [
    {
      "citation-id": "A1",
      "check-name": "probed-no-candidates",
      "status": "pass",
      "cited-value": "Already-cited tier-1 paper covering the topic",
      "actual-value": "0 candidates in window",
      "evidence-quote": "https://api.openalex.org/works?filter=cites:W<id-a1>,from_publication_date:2025-09-01&sort=publication_date:desc&per-page=200&cursor=*"
    },
    {
      "citation-id": "A2",
      "check-name": "probed-no-candidates",
      "status": "pass",
      "cited-value": "Second already-cited paper covering the topic",
      "actual-value": "0 candidates in window",
      "evidence-quote": "https://api.openalex.org/works?filter=cites:W<id-a2>,from_publication_date:2025-09-01&sort=publication_date:desc&per-page=200&cursor=*"
    }
  ],
  "cache": {"hits": 0, "misses": 5, "writes": 5}
}
```

Each row MUST be output-row-with-all-required-fields per `../../citation-detail-verify/references/output-schema.md` §Required row fields:

- `citation-id`: non-empty (the artifact's own source id on this row kind).
- `check-name`: non-empty (one registered for source-recency-probe).
- `status`: `pass`.
- `cited-value`: the cited title (non-empty on this row kind).
- `actual-value`: the literal `0 candidates in window`.
- `evidence-quote`: the cited-by query URL that was walked.

The output-row-with-all-required-fields property MUST hold: every emitted row carries ALL six required fields.

## Success-criteria evidence

This fixture grounds two brief DSL rows:
- `detect emitted-verdict-pass in ~/.claude/skills/source-recency-probe/test-corpus/pass-shape.md count >=1`
- `detect output-row-with-all-required-fields in ~/.claude/skills/source-recency-probe/test-corpus/pass-shape.md count >=1`
