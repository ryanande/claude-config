---
title: Fixture — probed-no-candidates (a resolved source that yielded nothing emits a pass row, never an absent row)
date: 2026-09-05
fixture: source-recency-probe
expected_check_name: probed-no-candidates
expected_status: pass
authored_against: claude-opus-5,2026-01-01
sources:
  - id: S1
    title: "Large Language Models Cannot Self-Correct Reasoning Yet"
    url: "https://arxiv.org/abs/2310.01798"
    year: 2023
---

# Fixture — probed-no-candidates

The clean-probe path. One source, resolved and fully walked, whose cited-by window is empty and whose path-A listing returns nothing that clears the two-token title filter. Under v1 semantics this produced zero rows and a `pass` verdict — an empty-`rows` `pass` that the shared lock forbids and that collapses *"probed, found nothing"* into *"never probed"*. From v2.0 the source emits one `probed-no-candidates` row instead.

## Recorded responses (abridged)

`GET https://api.openalex.org/works/https://doi.org/10.48550/arXiv.2310.01798?select=id,doi,title,publication_date,cited_by_count` → `{"id":"https://openalex.org/W4387355948", …}` → **resolved**.

`GET https://api.openalex.org/works?filter=cites:W4387355948,from_publication_date:2026-01-01&sort=publication_date:desc&per-page=200&cursor=*&select=id,doi,ids,title,publication_date,cited_by_count,authorships` → `meta: {"count":0,"per_page":200,"next_cursor":null}`, `results: []` (synthetic for this fixture: the same query returned 6 in-window citers on 2026-09-05; the fixture pins the empty-window branch).

Path A on `arxiv:cs.CL` since the cutoff returns entries, none sharing ≥ 2 non-stop-word tokens with the cited title → no path-A candidate survives.

## Expected skill behavior

- S1 is `resolved`; the walk terminates on `next_cursor: null` after one page.
- No candidate survives §Ranking and caps for S1 → exactly one row:

```json
{
  "citation-id": "S1",
  "check-name": "probed-no-candidates",
  "status": "pass",
  "cited-value": "Large Language Models Cannot Self-Correct Reasoning Yet",
  "actual-value": "0 candidates in window",
  "evidence-quote": "https://api.openalex.org/works?filter=cites:W4387355948,from_publication_date:2026-01-01&sort=publication_date:desc&per-page=200&cursor=*"
}
```

- Aggregate `verdict: pass` per `../../citation-detail-verify/references/output-schema.md` §Verdict computation (every row is `pass`).
- The envelope's `rows` array MUST NOT be empty. `sources[]` is non-empty, and every entry in `sources[]` yields at least one row — a candidate row, `probed-no-candidates`, or `source-unresolved`.
- `probed-no-candidates` MUST NOT be confused with `source-unresolved` (never probed, `unverifiable`) or `nothing-to-probe` (no evidence base at all, `unverifiable`). This row asserts the strictly stronger fact that the source WAS walked and is clear.

## Success-criteria evidence

Grounds: `detect "probed-no-candidates" … probed-no-candidates.md count >=1`.
