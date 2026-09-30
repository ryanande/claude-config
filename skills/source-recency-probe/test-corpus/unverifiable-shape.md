---
title: Fixture — unverifiable-shape (second consecutive 429 on the citation graph → source-unresolved, verdict unverifiable)
date: 2026-05-19
fixture: source-recency-probe
expected_check_name: source-unresolved
expected_status: unverifiable
authored_against: claude-opus-4-7,2025-09-01
sources:
  - id: A1
    title: "Pre-cutoff foundational paper"
    url: "https://arxiv.org/abs/2401.00001"
    year: 2024
---

# Fixture — unverifiable-shape

Refreshed to v2.0 semantics. The v1 version of this fixture asserted a catalog-driven venue probe failing against `venue:arxiv:cs.SE`. There is no catalog at v2.0, so the fixture now pins the equivalent v2 failure: the citation-graph resolve for A1 returns HTTP 429, the skill waits per `Retry-After` and retries **once**, and the retry returns 429 again.

Per `references/query-strategies.md` §Rate-limit safety rule 6, a second consecutive 429/503 emits `source-unresolved` for that source and the walk continues with the next source. Per `../../citation-detail-verify/references/output-schema.md` §Status semantics, the skill cannot distinguish "this source has no post-cutoff citers" from "the provider refused the request," so the row status SHALL be `unverifiable` (NOT `pass`, NOT `fail`).

## Expected skill behavior

Per `../../citation-detail-verify/references/output-schema.md` §Verdict computation, no `fail` rows + at least one `unverifiable` row → aggregate `verdict: unverifiable`.

Expected envelope shape:

```json
{
  "version": "1.0",
  "skill": "source-recency-probe",
  "artifact": "<this-fixture-path>",
  "invoked_at": "<ISO-8601 UTC>",
  "verdict": "unverifiable",
  "rows": [
    {
      "citation-id": "A1",
      "check-name": "source-unresolved",
      "status": "unverifiable",
      "cited-value": "Pre-cutoff foundational paper",
      "actual-value": "unresolvable",
      "evidence-quote": "HTTP 429 on https://api.openalex.org/works/https://doi.org/10.48550/arXiv.2401.00001 after one Retry-After backoff and one retry"
    }
  ],
  "cache": {"hits": 0, "misses": 2, "writes": 0}
}
```

The emitted-verdict-unverifiable trajectory MUST be detectable. Status MUST NOT collapse to `pass` (which would silently hide the failure, and would falsely claim the strictly stronger `probed-no-candidates` fact that the source was walked and cleared) or to `fail` (which would mis-attribute the failure to a finding).

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect emitted-verdict-unverifiable in ~/.claude/skills/source-recency-probe/test-corpus/unverifiable-shape.md count >=1`.
