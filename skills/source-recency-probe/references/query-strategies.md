---
title: Source resolution, citation collection, and always-on path-A / registered-undispatched probe-strategy templates for /source-recency-probe
version: 2.0
status: locked
owners: [source-recency-probe]
consumers: [source-recency-probe]
---

# Query strategies v2.0

Skill-scoped lock for `/source-recency-probe`. Defines (a) how a `sources[]` entry is resolved to a citation-graph node, (b) how citing papers since the cutoff are collected and capped, and (c) the three legacy probe-strategy kinds, of which `probe-arxiv-category` is now the always-on path-A signal for arXiv sources and the other two are registered but undispatched. From v2.0 the venue set is derived from the artifact's own sources; there is no topic-tag catalog. Sibling research-pipeline skills do NOT REUSE this file (`/survey-refresh` read the v1.x catalog and was changed in the same PR to stop).

The citation-graph provider is **OpenAlex** (`https://api.openalex.org`). Semantic Scholar was the provider in the approved design and was ruled out on 2026-09-05: its API key is not licensable for this org. See `docs/superpowers/specs/2026-09-05-source-recency-probe-citation-graph-design.md` §5 for the superseded provider facts.

## Source resolution

Every OpenAlex request carries `mailto=wyatt.rupp@prepass.com` (the polite pool). There is no API key and none is required.

For each entry in the artifact's frontmatter `sources[]`, derive an OpenAlex lookup key from the URL. **Check the key forms in the order listed; the first match wins.**

1. `arxiv.org/abs/<id>` or `arxiv.org/pdf/<id>` (version suffix stripped) → the DataCite DOI form `10.48550/arXiv.<id>`, fetched as
   `GET https://api.openalex.org/works/https://doi.org/10.48550/arXiv.<id>?select=id,doi,title,publication_date,cited_by_count,authorships&mailto=<address>`.
   Verified live 2026-09-05: `2310.01798` → `W4387355948`, `2402.08115` → `W4391833261`.
2. `doi.org/<doi>` or a `doi:` field → `GET https://api.openalex.org/works/https://doi.org/<doi>?select=id,doi,title,publication_date,cited_by_count,authorships&mailto=<address>`.
3. Otherwise, exact-title search:
   `GET https://api.openalex.org/works?filter=title.search:<url-encoded title>&per-page=2&select=id,title,doi&mailto=<address>`.
   Accept the hit **only** when `meta.count` is 1 and its title equals the cited title after the normalisation below. Use `filter=title.search:` — never the bare `search=` parameter, which is full-text and returned 233k hits for a known title.

**Title normalisation.** The comparison uses the normalisation `../citation-detail-verify/SKILL.md` applies for `title-match` (whitespace and punctuation collapsed), **plus one additional step this skill owns: case-folding.** Case-folding is not part of `citation-detail-verify`'s `title-match`; it is added here because OpenAlex title casing is not stable across records.

Outcomes per source:

| Outcome | Condition | Consequence |
|---|---|---|
| **resolved** | 200 for the key, or an exact-title search hit with `meta.count` 1 | proceed to §Citation collection. If the source is an arXiv source, path A (§Probe-strategy schema) **also** runs for it — path A is always-on for arXiv sources, not a fallback |
| **graph-unknown** | a key was derived but OpenAlex returned 404 (work not indexed yet) | if the key is an arXiv id and the arXiv metadata fetch (already made for liveness by sibling skills, via the shared cache) succeeded → path A is that source's only probe; else treat as unresolvable |
| **unresolvable** | no key and no exact-title match, OR a non-arXiv key OpenAlex returned 404 for, OR an arXiv key whose arXiv metadata fetch also failed | emit one `source-unresolved` row, `status: unverifiable`, `citation-id` = the artifact's source id, `evidence-quote` = the lookup that failed |

**Path-A listing failure.** When a path-A arXiv-category listing fails at the HTTP level (network, 5xx, second consecutive 429/503), the skill emits one `venue-absent-from-sources` row at `unverifiable` carrying the `venue:` id. **Additionally**, when path A was that source's only probe — a `graph-unknown` source — the same failure emits one `source-unresolved` row at `unverifiable` for the source id with `actual-value: unresolvable`, because nothing probed that source at all. A `resolved` source whose citation walk succeeded gets the venue row only; its own evidence base was walked.

Author-declared `tags:` and body headings are **not** inputs to this step or any other. The artifact's `sources[]` is the only topic signal.

## Citation collection

For each **resolved** source:

```
GET https://api.openalex.org/works?filter=cites:<W-id>,from_publication_date:<DATE>&sort=publication_date:desc&per-page=200&cursor=*&select=id,doi,ids,title,publication_date,cited_by_count,authorships&mailto=<address>
```

- `sort=publication_date:desc` is **REQUIRED**. OpenAlex's default result order is not by date (observed unsorted on 2026-09-05: first entry `2025-01-14`, last `2026-07-31`).
- `from_publication_date:<DATE>` applies the probe window **server-side**. Every returned entry is therefore already in-window, and no client-side early-stop rule or cross-page ordering guard is needed for correctness — both are removed at v2.0.
- **Walk rule:** start at `cursor=*` and follow `meta.next_cursor` until it is null or the 10-page cap is reached. An empty page with a non-null `next_cursor` continues the walk and counts toward the cap.
- `per-page` maximum is 200 (`per-page=201` → HTTP 400), so the 10-page cap is 2000 citers per source.
- Entries lacking `publication_date` are kept only if `publication_year > year(DATE)`.

Each page is cached under `../citation-detail-verify/references/cache-contract.md` with the normalised URL (including `cursor`) as the key.

A source that hits the pagination cap contributes the candidates already walked **and** one `source-unresolved` row with `actual-value: pagination cap`.

## Ranking and caps

**Dedupe, in this order.**

1. Collapse `sources[]` entries that resolved to the **same OpenAlex W-id** into one canonical source id (the first by document order). Only distinct W-ids count toward the "cites ≥ 2 sources" test, so a paper cited twice under two URLs cannot manufacture a cross-source signal on its own.
2. Merge candidates by OpenAlex W-id.
3. Drop any candidate whose W-id **or** DOI matches a resolved source.

**Sort keys**, applied in order, each descending unless stated:

1. number of the artifact's (canonical) sources the candidate cites;
2. `cited_by_count`;
3. `publication_date`;
4. author overlap with a cited source — a candidate that overlaps sorts before one that does not;
5. OpenAlex W-id, **lexicographic ascending** — a total order, so the capped set is a deterministic function of the candidate set.

If any candidate cites ≥ 2 canonical sources → emit the top **10** overall. Otherwise → **per-source cap mode**: for each source, its top **3** citers; deduplicate across sources.

**Path-A candidates** (see §Probe-strategy schema) carry no cross-source citation signal, so they enter the overall pool with sort key 1 fixed at **0**. A 0 can never outrank a candidate citing ≥ 2 sources, so top-10 mode's composition is unaffected — but path-A candidates are never silently discarded: they compete in **both** modes on the remaining keys.

**Row kind.** Author normalisation is surname + first initial, case-folded, over `authorships[].author.display_name` (falling back to `raw_author_name`).

- A candidate sharing at least one normalised author with N ≥ 1 of the sources it cites emits exactly one `source-superseded-by-newer` row **per (candidate, overlapping source) pair** and **no** `new-candidate-found` row. It consumes exactly **one** cap slot regardless of N.
- **Duplicate guard:** skip supersession classification when the candidate's normalised title equals the anchored source's normalised title. That is a resubmission of the same work, not a superseding paper — drop the candidate rather than emit a row.
- Otherwise the candidate emits `new-candidate-found`.

**Clean sources.** A resolved source that yielded no candidate surviving the caps emits exactly one `probed-no-candidates` row at `status: pass`. Every entry in `sources[]` therefore yields at least one row — a candidate row, `probed-no-candidates`, or `source-unresolved` — so `rows` is never empty when `sources[]` is non-empty.

Note on the second key: post-cutoff citers usually have `cited_by_count` 0, so in per-source cap mode the effective order is recency, with author overlap and the W-id tie-break making it total. This is a bounded, mechanical, author-blind candidate list — not a relevance ranking.

## Probe-strategy schema

Three probe-strategy kinds are registered. Only `probe-arxiv-category` is dispatched at v2.0, and it is **always-on for every arXiv source** — both `resolved` sources (as a second signal alongside the citation walk) and `graph-unknown` sources (as their only probe). The reason is measured, not precautionary: OpenAlex indexes arXiv-only citers thinly, so the citation walk alone under-recalls arXiv-native work (see §Provider coverage note). `probe-arxiv-category` lists `arxiv:<primary_category>` since the cutoff and filters candidates whose title shares at least two non-stop-word tokens with the cited title (the *cited paper's* title, never the artifact's tags or headings); cap top 3 per source, joining §Ranking and caps with sort key 1 fixed at 0 in both modes. `probe-named-conference` and `probe-research-blog` remain registered so the URL templates below stay valid, but v2.0 has no path that dispatches them; they are candidates for removal at a later major, and their "topic-vector filter" clauses are dead text kept verbatim alongside the templates — no v2.0 path computes a topic vector. Each strategy registers a venue class, a query template, and a response-shape extractor.

### Provider coverage note

OpenAlex's coverage of arXiv-only citers is materially thinner than Semantic Scholar's. Measured 2026-09-05 on S1 (`arXiv:2310.01798` → `W4387355948`): `cited_by_count` 38 on OpenAlex against 1167 on Semantic Scholar, and 6 citers after 2026-01 against hundreds. Path A being always-on for arXiv sources is the compensation for that gap.

### registered-query-strategy: probe-arxiv-category

- **Venue class:** arXiv categories (`cs.SE`, `cs.LG`, `cs.AI`, `cs.CL`, …).
- **Query template:** `https://export.arxiv.org/api/query?search_query=cat:<category>+AND+submittedDate:[<cutoff_yyyymmdd>0000+TO+<today_yyyymmdd>2359]&sortBy=submittedDate&sortOrder=descending&max_results=50`.
- **Response-shape extractor:** Atom feed (`<entry>` elements). Per entry: `<id>` → arXiv ID (citation-id); `<title>` → candidate title; `<summary>` → abstract excerpt; `<published>` → date.
- **Title-token filter:** retain candidates whose title shares ≥ 2 non-stop-word tokens with the cited source's title. No per-candidate LLM rerank. **Tokenisation is pinned:** apply the §Source resolution title normalisation (the `citation-detail-verify` `title-match` normalisation plus this skill's case-folding), split on whitespace, then remove exactly these stop-words — `a`, `an`, `the`, `of`, `for`, `and`, `or`, `in`, `on`, `to`, `with`, `by`, `from`, `at`, `is`, `are`, `via`, `using`, `towards`, `toward`. No stemming.
- **Cache key derivation:** `sha256(normalized_url)` per `../citation-detail-verify/references/cache-contract.md` §Cache key derivation. The query URL is the cache key input; cross-skill hits accrue when sibling skills fetch the same arXiv-category listing in the same session.

### registered-query-strategy: probe-named-conference

- **Venue class:** named conferences (NeurIPS, ICSE, FSE, ICML, ACL, EMNLP, ICLR, …).
- **Query template:** conference-specific. Per-conference URL templates are catalogued in §Per-conference URL templates below (v1.2 additive — earlier v1.0/v1.1 callers using the abstract schema slot continue unchanged when no concrete template is registered). Skills MUST resolve to the registered template when one exists; fall back to `unverifiable` row emission when no template is registered for the conference.
- **Response-shape extractor:** conference-specific; defined alongside each registered URL template in §Per-conference URL templates.
- **Topic-vector filter:** title or session-track token intersection with topic vector.
- **Cache key derivation:** same `sha256(normalized_url)` rule.

### registered-query-strategy: probe-research-blog

- **Venue class:** named research blogs (lab blogs, individual researcher blogs).
- **Query template (resolution order):**
  1. `<blog-base-url>/feed.xml` (the v1.0 default — preserved for callers).
  2. `<blog-base-url>/<topic-tag>/feed.xml` when the blog supports tag-scoped feeds.
  3. `<blog-base-url>/news/rss.xml` or `<blog-base-url>/rss` (v1.2 additive — common alternates).
  4. `<blog-base-url>/sitemap.xml` (v1.2 additive — HTML-only blogs without RSS; sitemap-loc entries are filtered by topic-vector against `<loc>` URL paths and `<lastmod>` ≥ cutoff_date).
  Resolve in order; first 200 OK wins. If all four return 4xx/5xx, emit one `venue-absent-from-sources` row with `status: unverifiable`.
- **Response-shape extractor:**
  - For options 1-3 (RSS/Atom): per `<item>` / `<entry>`: `<link>` → blog post URL (citation-id); `<title>`; `<description>` or `<summary>` → excerpt; `<pubDate>` or `<published>`.
  - For option 4 (sitemap): per `<url>`: `<loc>` → blog post URL (citation-id); URL path tail → title proxy (sitemap entries lack title metadata); empty string → excerpt; `<lastmod>` → date.
- **Topic-vector filter:** title or post-tag intersection with topic vector (sitemap-mode: URL path token intersection).
- **Cache key derivation:** same `sha256(normalized_url)` rule.

## Migration note (v1.x → v2.0)

The v1.x §Topic-tag catalog (11 topic-tag → venue rows) is removed. Venue selection is derived from `sources[]` (§Source resolution); the catalog's recall on venues the author cited nothing from is deliberately given up — its history shows it was extended only after an artifact outside its coverage had already failed (v1.1 after RFC-0003, v1.5 after the first survey to declare `agent-loops`, and the RFC-0020/0021 family that triggered this change). `topic-tag-uncatalogued` is deprecated in the shared lock and never emitted. `/survey-refresh` step 5, the one external reader of the catalog, was changed in the same PR to a single advisory row.

The v2.0 citation-graph provider is OpenAlex, not Semantic Scholar. The design was approved against Semantic Scholar; on 2026-09-05 the user ruled that its API key is not licensable for this org, and the provider changed before any code was written. The Semantic Scholar facts are kept as history in the design's §5, and `scripts/spike_s2.py` survives as provenance only.

## Row mappings

Per-row-kind field mappings for the six `check-name` values this skill emits (plus the deprecated seventh). Conforms to `../citation-detail-verify/references/output-schema.md` §Row shape and §Required row fields; this section names which row field carries which semantic per row kind.

### new-candidate-found

- `citation-id` — candidate identifier, resolved by this fallback chain, first available wins: `arXiv:<id>`, else `DOI:<doi>`, else `openalex:<W-id>`. MUST NOT be empty.
- `cited-value` — the list of the artifact's source ids the candidate cites, e.g. `[S1, S4]`.
- `actual-value` — `title · publication_date · cited_by_count`.
- `evidence-quote` — verbatim candidate title.
- `status` — `fail` (the survey missed a candidate the venue produced).

### venue-absent-from-sources

- `citation-id` — stable venue identifier per §Venue identifier convention below (e.g., `venue:arxiv:cs.SE`). MUST NOT be empty.
- `cited-value` — literal empty string `""`.
- `actual-value` — venue display name (e.g., `arXiv cs.SE`).
- `evidence-quote` — the HTTP status code or network error text for the failed listing.
- `status` — always `unverifiable`. The v1.x `fail` branch (venue produced in-scope work and is absent from `sources[]`) is **deleted at v2.0**: venue selection no longer comes from a catalog, so there is no "venue the author should have cited" judgement left for this row to carry, and the `fail` branch is unreachable. Per Decision 6 of `openspec/changes/archive/2026-05-19-source-recency-probe-skill/design.md` a probe that could not run is `unverifiable`, never `pass` or `fail`.

From v2.0 this row is emitted **only** when a path-A arXiv-category listing fails at the HTTP level (network, 5xx, second consecutive 429/503). It is never used for an unresolved paper — that is `source-unresolved`. When path A was the source's only probe (a `graph-unknown` source), the same listing failure ALSO emits a `source-unresolved` row for that source id per §Source resolution §Path-A listing failure; when the source resolved and its citation walk succeeded, only this venue row is emitted.

### source-unresolved

- `citation-id` — the artifact's own source id (e.g., `S3`, `A12`). MUST NOT be empty.
- `cited-value` — the cited title, or the URL when no title is declared.
- `actual-value` — one of the literal strings `unresolvable`, `wall-time cap`, `pagination cap`.
- `evidence-quote` — the lookup that failed (key tried and HTTP status, or the search query and the mismatching top title) or the cap name.
- `status` — always `unverifiable`.

### probed-no-candidates

- `citation-id` — the artifact's own source id (e.g., `S3`, `A12`). MUST NOT be empty.
- `cited-value` — the cited title.
- `actual-value` — the literal string `0 candidates in window`.
- `evidence-quote` — the cited-by query URL that was walked.
- `status` — always `pass`. One row per resolved source that yielded no candidate surviving §Ranking and caps. This is the "probed, found nothing" carrier: it is what keeps a clean probe from collapsing into an empty-`rows` `pass`, which the shared lock forbids.

### nothing-to-probe

- `citation-id` — the literal `sources:<none>`.
- `cited-value`, `actual-value`, `evidence-quote` — literal empty strings `""`.
- `status` — always `unverifiable`. Exactly one row per invocation; the envelope contains no other rows.

### topic-tag-uncatalogued (deprecated)

Not emitted from v2.0. Registered in the shared lock for backward parsing only.

### source-superseded-by-newer

- `citation-id` — the existing citation's identifier from the survey's `sources[]` (NOT the new candidate's identifier; supersession is anchored to what's already cited).
- `cited-value` — existing source title.
- `actual-value` — superseding candidate `title · publication_date · arXiv/DOI id`.
- `evidence-quote` — verbatim superseding candidate title (required non-empty; this is a `fail` row).
- `status` — `fail` (the cited source is no longer the dominant evidence).

## Venue identifier convention

Stable identifiers used as `citation-id` for `venue-absent-from-sources` rows per `../citation-detail-verify/references/output-schema.md` §Required row fields:

- `venue:arxiv:<category>` — e.g., `venue:arxiv:cs.SE`.
- `venue:conf:<name>` — e.g., `venue:conf:NeurIPS`.
- `venue:blog:<short-name>` — e.g., `venue:blog:anthropic`.

The `venue:` prefix is the namespace marker that distinguishes a venue-id from a paper-id in row-level parsing. Sibling skills consuming output rows can detect venue-rows by the `citation-id` prefix.

## Per-conference URL templates (v1.2)

Concrete URL templates for the conferences registered below. Adding a new conference is a v1.x minor-additive change. Templates use `<year>` as a placeholder substituted at probe time (default: current calendar year; range probes substitute multiple years).

| Venue | URL template | Response shape | Notes |
|-------|--------------|----------------|-------|
| `conf:NeurIPS` | OpenReview JSON API: `https://api2.openreview.net/notes?content.venueid=NeurIPS.cc/<year>/Conference&details=replyCount&offset=0&limit=200` (paginate `offset` by 200). | JSON `{"notes":[...]}`; per note: `content.title.value` → title, `content.abstract.value` → abstract, `content.authors.value` → authors, `pdate` → publication date (epoch ms). | **v1.3 fix.** The filter key is `content.venueid` (the OpenReview Group id), NOT `content.venue` (the display string `NeurIPS 2025 Conference`); the v1.2 `content.venue=...+Conference` query returned `{"notes":[],"count":0}`. Venue-id discovery: the active venue id equals the Group page id, resolvable from `https://openreview.net/group?id=NeurIPS.cc/<year>/Conference` (the `id=` query param). Verified 2026-05-29: `content.venueid=NeurIPS.cc/2025/Conference` returns >300 notes. |
| `conf:ICLR` | OpenReview JSON API: `https://api2.openreview.net/notes?content.venueid=ICLR.cc/<year>/Conference&details=replyCount&offset=0&limit=200` (paginate `offset`). | Same OpenReview JSON shape as NeurIPS. | **v1.3 fix** — same `content.venueid` (not `content.venue`) correction + venue-id discovery from `https://openreview.net/group?id=ICLR.cc/<year>/Conference`. Verified 2026-05-29: `content.venueid=ICLR.cc/2025/Conference` returns >300 notes. |
| `conf:ICML` | OpenReview JSON API: `https://api2.openreview.net/notes?content.venueid=ICML.cc/<year>/Conference&details=replyCount&offset=0&limit=200` (paginate `offset`). | Same OpenReview JSON shape. | **v1.3 fix** — the v1.2 `content.venue=ICML+<year>+Conference` query returned a single note; `content.venueid=ICML.cc/<year>/Conference` returns the full proceedings. Venue-id discovery from `https://openreview.net/group?id=ICML.cc/<year>/Conference`. Verified 2026-05-29: returns >300 notes. |
| `conf:ACL` | `https://aclanthology.org/events/acl-<year>/` | HTML; per paper, the title anchor is `<strong><a class=align-middle href=/<year>.acl-<track>.<n>/>` where `<track>` ∈ {`long`,`short`,`findings`,`demo`,…} and `<n>` is the paper number. Extractor regex: `<strong><a class=align-middle href=/<year>\.acl-[a-z]+\.[0-9]+/>` — capture the anchor inner text (strip nested `<span class=acl-fixed-case>` casing spans) as the title. | **v1.3 fix.** The v1.2 regex `<strong><a href="/N.NN/">` matched 0 titles: ACL Anthology serves **unquoted** HTML attributes, the anchor carries `class=align-middle`, and the href path is `/<year>.acl-<track>.<n>/` (not `/N.NN/`). No JSON API. The `/<year>.acl-<track>.0/` anchor (paper number `0`) is the proceedings front-matter, not a paper — exclude it. Page is ~12 MB; fetch via streaming/curl, not an in-memory cap. Verified 2026-05-29: regex matches 1972 anchors on `acl-2025`. |
| `conf:EMNLP` | `https://aclanthology.org/events/emnlp-<year>/` | Same ACL Anthology HTML pattern; extractor regex `<strong><a class=align-middle href=/<year>\.emnlp-[a-z]+\.[0-9]+/>`. | **v1.3 fix** — same unquoted-attr / `class=align-middle` / `/<year>.emnlp-<track>.<n>/` correction as ACL. Verified 2026-05-29: 1451 anchors on `emnlp-2024`. |
| `conf:ICSE` | Research-track sub-page: `https://conf.researchr.org/track/icse-<year>/icse-<year>-research-track` (NOT the `home/icse-<year>` landing page, which lists no papers). | HTML; per accepted paper a table-cell anchor `<a href="#" data-event-modal="<uuid>">TITLE</a>`. Extractor regex: `data-event-modal="[a-f0-9-]+">([^<]{8,})` — capture group 1 is the title (HTML-unescape `&quot;` etc.); dedupe by `data-event-modal` uuid. | **v1.3 fix.** The v1.2 `home/icse-<year>` URL lists no papers — the paper list lives on the research-track sub-page. Track slug is `icse-<year>-research-track` (other tracks substitute their own slug). Verified 2026-05-29: 667 deduped paper titles on `icse-2026-research-track`. |
| `conf:FSE` | Research-track sub-page: `https://conf.researchr.org/track/fse-<year>/fse-<year>-research-papers` (track slug varies by year; resolve from the `home/fse-<year>` track menu). Same researchr `data-event-modal` extractor as ICSE. | Same researchr HTML pattern as ICSE. | Track slug discovery: the `home/fse-<year>` page's navigation menu links each track's sub-page; pick the research/papers track. |

Conferences not in this table fall back to `unverifiable` row emission per probe-named-conference §Query template. Additional conferences are v1.x minor-additive.

### OpenReview venue-id discovery sub-step (NeurIPS / ICLR / ICML)

Before issuing the notes query for any OpenReview-hosted conference, resolve the active **venue id**:

1. The venue id for the accepted-papers set equals the conference Group id — `<Venue>.cc/<year>/Conference` (e.g. `NeurIPS.cc/2025/Conference`). This is the `id=` query param on the Group page `https://openreview.net/group?id=<Venue>.cc/<year>/Conference`.
2. Issue the notes query filtering on `content.venueid=<resolved-id>` (the Group id), NOT `content.venue` (the human-readable display string). The display-string filter returns zero or a stray single note.
3. Confirm `notes[]` is non-empty for the most recent completed year before treating an empty result as "no candidates"; an empty `notes[]` for a completed conference indicates a venue-id resolution failure, not a clean pass.

## Per-blog URL templates (v1.2)

Concrete URL templates for the blogs registered below. Resolved via the §probe-research-blog §Query template (resolution order) — first 200 OK wins.

| Venue | Preferred URL | Fallback | Notes |
|-------|---------------|----------|-------|
| `blog:anthropic` | `https://www.anthropic.com/sitemap.xml` | (none — anthropic.com does not serve RSS or Atom as of v1.2) | Sitemap-mode probe: filter `<url>` entries by `<loc>` URL path containing topic-vector tokens; `<lastmod>` ≥ cutoff_date. |
| `blog:openai` | `https://openai.com/news/rss.xml` | `https://openai.com/sitemap.xml` (if RSS goes 4xx/5xx) | RSS works as of v1.2; sitemap is fallback for resilience. |

Additional blogs are v1.x minor-additive.

## Rate-limit safety (v1.2)

Skills implementing the probe-strategy workflow MUST enforce these rate-limit-safety properties to avoid IP-level throttle / ban on shared listing endpoints (arXiv API in particular has rate-limited IP-level shadow throttles that outlast their official guidance):

1. **Serial probe execution.** The skill SHALL emit venue probes serially, NOT in parallel. Even when running in a Claude harness that exposes parallel WebFetch, the skill's per-venue probe loop SHALL be a sequential `for venue in venues:` shape with each probe completing before the next is issued.
2. **Minimum inter-request spacing.** Between two consecutive venue probes against any one host, the skill SHALL wait at least 3 seconds. For arXiv (`*.arxiv.org`) specifically, the minimum is 4 seconds — a margin over arXiv's published guidance of one request per 3 seconds.
3. **Backoff on 429 / 503.** When a probe returns HTTP 429 or 503, the skill SHALL wait 60 seconds before any retry against that host (single retry per probe; on second consecutive 429/503, emit `venue-absent-from-sources status: unverifiable` and continue with the next venue), and, when path A was that source's only probe, the `source-unresolved` row per §Source resolution §Path-A listing failure.
4. **User-Agent identification.** Probes SHALL set a `User-Agent` header naming the skill and version (e.g., `source-recency-probe/2.0 (claude-config)`). Anonymous fetches without UA are explicitly prohibited.
5. **Wall-time budget surfacing.** Callers SHOULD expect a worst-case wall-time of `N_sources × (1 resolve + ≤ 10 citation pages) × spacing`, plus p99 fetch latency per request. The skill SHALL NOT tighten inter-request spacing or parallelise requests in order to stay under a latency budget; rate-limit safety wins over latency. The **only** sanctioned truncation is rule 7's wall-time cap, and it is always surfaced as a `source-unresolved` row — never as a silently shortened walk.
6. **OpenAlex (`api.openalex.org`).** Requests are serial, spaced 1 s. Every request carries `mailto=<address>` (the polite pool); there is no API key. The response headers `x-ratelimit-limit` (observed `1000`), `x-ratelimit-remaining` and `x-ratelimit-reset` (seconds; observed 18124 ≈ 5 h) carry the live quota — the skill reads them rather than assuming a documented figure. On HTTP 429: read `Retry-After` (falling back to `x-ratelimit-reset`), wait, retry **once**; on a second consecutive 429/503 emit `source-unresolved` (`actual-value: unresolvable`, `evidence-quote: HTTP <code>`) for that source and continue. On 5xx / network error: same row, no retry.
7. **Wall-time cap.** 15 minutes per invocation. Past it, each remaining source emits `source-unresolved` with `actual-value: wall-time cap`. Budget: OpenAlex allows 1000 requests per ~5 h window, and a source costs 1 resolve + at most 10 citation pages = 11 requests; at 1 s spacing the 15-minute cap buys ~900 requests, so it binds first at roughly 80 sources per invocation. Surveys in this corpus run 15–30 sources, so neither limit binds on real inputs.

Rules 1–5 are part of the v1.2 contract and rules 6–7 of the v2.0 contract; consumer skills SHALL implement them. Test-corpus fixtures exercising rate-limit-safety properties are v1.x minor-additive.

## Versioning

- Major — a breaking change to any of: §Source resolution key derivation or its outcome set, the §Citation collection walk rules (endpoint, required sort, window filter, cursor/cap semantics), §Ranking and caps sort keys or cap sizes, the §Row mappings for a registered `check-name`, the venue identifier convention, or the response-shape extractors.
- Minor — additive change only. New probe-strategy kinds (a fourth class beyond arXiv/conference/blog). A newly registered probe kind or row-mapping entry that changes no existing one. New test-corpus fixtures. Per-conference and per-blog URL templates fleshing out an existing schema slot.
- v1.0 is the locked Stage 2 contract; the three registered probe-strategy kinds satisfy the brief's `success_criteria` row `detect registered-query-strategy in ~/.claude/skills/source-recency-probe/references/query-strategies.md count >=3`.
- v1.1 — added topic-tag rows for `llm-as-judge`, `rubric`, `evaluation`, `code-review`, `reliability`, `waf` (surfaced by Stage 1 of RFC-0003).
- v1.2 — added per-conference URL templates, per-blog URL templates, an extended `probe-research-blog` sitemap.xml fallback, and §Rate-limit safety (serial execution, inter-request spacing, 429/503 backoff).
- v1.3 — corrected the response-shape extractors for 6 venues (NeurIPS/ICLR/ICML `content.venueid`; ACL/EMNLP unquoted-attr anchor; ICSE research-track sub-page + `data-event-modal`) so each extracts >0 records on a live fetch; minor-additive, no schema or venue-set change.
- v1.4 — added the `topic-tag-uncatalogued` row kind, scoped to frontmatter-declared `tags:` only, including the `tag:<none>` sentinel; additive, no venue or existing row changed.
- v1.5 — added the `agent-loops`, `self-correction` and `verification-feedback` topic-tag rows; corrected §Rate-limit safety rule 2's arXiv-spacing attribution (4s is a local safety margin, not arXiv's published 3s guidance); dropped a stale entry-count from §Row mappings §Scope.
- v2.0 (current) — **major**: §Topic-tag catalog removed; §Source resolution, §Citation collection, §Ranking and caps added; the citation-graph provider is OpenAlex (Semantic Scholar ruled out 2026-09-05 — API key not licensable for this org); `probe-arxiv-category` is always-on for arXiv sources with its topic-vector filter replaced by a pinned cited-title token filter, and the other two probe kinds are registered but undispatched; §Row mappings gains `source-unresolved`, `nothing-to-probe` and `probed-no-candidates`, drops the unreachable `venue-absent-from-sources` `fail` branch, and deprecates `topic-tag-uncatalogued`; §Rate-limit safety gains rules 6–7. Design: `docs/superpowers/specs/2026-09-05-source-recency-probe-citation-graph-design.md`.
