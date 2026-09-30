---
title: Fixture — source-derived-venues (venue set comes from sources[], tags are not consulted)
date: 2026-09-05
fixture: source-recency-probe
expected_check_name: new-candidate-found
expected_status: fail
authored_against: claude-opus-5,2026-01-01
tags: [llm-review, code-review]   # deliberately catalog-era tags — they MUST have no effect (tags-not-consulted)
sources:
  - id: S1
    title: "Large Language Models Cannot Self-Correct Reasoning Yet"
    url: "https://arxiv.org/abs/2310.01798"
    year: 2023
  - id: S2
    title: "LLM Evaluators Recognize and Favor Their Own Generations"
    url: "https://arxiv.org/abs/2404.13076"
    year: 2024
  - id: S3
    title: "Correlated Errors in Large Language Models"
    url: "https://doi.org/10.48550/arXiv.2506.07962"
    year: 2025
---

# Fixture — source-derived-venues

Three sources: two arXiv ids, one DOI. The artifact declares `tags: [llm-review, code-review]`, which under v1.x would have resolved five venues. Under v2.0 the tags are **not read** — marker: `tags-not-consulted` — and the candidate set is whatever the citation graph of S1–S3, plus the always-on path-A arXiv-category listing, yields.

## Recorded OpenAlex responses (abridged, verified live 2026-09-05)

Resolver host: `api.openalex.org`. Every request carries `mailto=<address>`; there is no API key. An arXiv source resolves through its DataCite DOI form `10.48550/arXiv.<id>`.

`GET https://api.openalex.org/works/https://doi.org/10.48550/arXiv.2310.01798?select=id,doi,title,publication_date,cited_by_count` →

```json
{"id":"https://openalex.org/W4387355948","doi":"https://doi.org/10.48550/arxiv.2310.01798","title":"Large Language Models Cannot Self-Correct Reasoning Yet","publication_date":"2023-10-03","cited_by_count":38}
```

`GET https://api.openalex.org/works?filter=cites:W4387355948,from_publication_date:2026-01-01&sort=publication_date:desc&per-page=200&cursor=*&select=id,doi,ids,title,publication_date,cited_by_count,authorships` → `meta: {"count":6,"per_page":200,"next_cursor":null}` (a single terminal page — the walk stops because `next_cursor` is null, not because of any client-side date check), first three `results` entries:

- `{"id":"https://openalex.org/W7172133375","doi":"https://doi.org/10.1007/978-3-032-32636-2_18","title":"Enhancing Mathematical Reasoning Education with Data-Driven Fine-Tuning of Large Language Models","publication_date":"2026-08-01","cited_by_count":0}`
- `{"id":"https://openalex.org/W7172268631","doi":"https://doi.org/10.14801/jkiit.2026.24.7.81","title":"Improving SQL Generation on Industrial Time-Series Data with Structured EXPLAIN Feedback","publication_date":"2026-07-31","cited_by_count":0}`
- `{"id":"https://openalex.org/W7168155044","doi":"https://doi.org/10.1007/978-981-92-3432-5_38","title":"Think Twice Before Pairing: A Self-Corrective Reflective Chain for Zero-Shot Multimodal Reasoning","publication_date":"2026-07-13","cited_by_count":0}`

S2 (`10.48550/arXiv.2404.13076`) and S3 (`10.48550/arXiv.2506.07962`) resolve by the same key form and return the same response shape; their cited-by pages are abridged out of this fixture.

**Coverage caveat, recorded because it drives path A.** S1's `cited_by_count` is 38 on OpenAlex against 1167 on Semantic Scholar, and 6 in-window citers against hundreds. That thin indexing of arXiv-only citers is why `probe-arxiv-category` is always-on for arXiv sources rather than a fallback.

## Expected skill behavior

- Step 2 resolves S1, S2, S3 (`resolved`, `resolved`, `resolved`) — no `source-unresolved` row.
- All three are arXiv sources, so path A also runs for each; path-A candidates join the pool with sort key 1 fixed at 0.
- No candidate cites ≥ 2 of S1–S3 in the recorded pages → per-source cap mode: top 3 per source by (`cited_by_count` desc, `publication_date` desc, author-overlap, W-id ascending), deduplicated.
- Emits `new-candidate-found` rows with `citation-id` = `DOI:10.1007/978-3-032-32636-2_18` etc. (the chain is `arXiv:<id>`, else `DOI:<doi>`, else `openalex:<W-id>`), `cited-value` = `[S1]`, `actual-value` = `title · publication_date · cited_by_count`, `evidence-quote` = verbatim title; `status: fail`.
- Aggregate `verdict: fail`.
- The envelope contains **no** `topic-tag-uncatalogued` row and **no** row derived from `tags:`.

## Success-criteria evidence

Grounds: `detect "tags-not-consulted" … source-derived-venues.md count >=1` and `detect "openalex" … source-derived-venues.md count >=1`.
