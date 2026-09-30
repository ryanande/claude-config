---
title: Fixture — arxiv-probe (path-A probe-emission trace for an arXiv source, all-pass envelope)
date: 2026-05-19
fixture: source-recency-probe
expected_check_name: probe-arxiv-category
expected_status: pass
authored_against: claude-opus-4-7,2025-09-01
sources:
  - id: A1
    title: "Agentic Code-Review Loops at Scale"
    url: "https://arxiv.org/abs/2401.00001"
    year: 2024
---

# Fixture — arxiv-probe

Refreshed to v2.0 semantics. Path A (`probe-arxiv-category`) is **always-on for every arXiv source** — `resolved` sources get it as a second signal alongside the citation walk, `graph-unknown` sources get it as their only probe. There is no topic-tag catalog; the venue is the cited source's own `primary_category`, and the title-token filter is pinned against the *cited* source's title, never the artifact's `tags:` or headings.

A1 resolves on the citation graph (`resolved`) with `primary_category: cs.SE`. Its citation walk completes with no surviving candidate. Path A also runs for A1 against `arxiv:cs.SE`:

```
GET https://export.arxiv.org/api/query?search_query=cat:cs.SE+AND+submittedDate:[202509010000+TO+202605192359]&sortBy=submittedDate&sortOrder=descending&max_results=50
```

Cache key: `sha256(normalized_url).hexdigest()` per `../../citation-detail-verify/references/cache-contract.md` §Cache key derivation.

Expected response-shape extractor (Atom feed `<entry>` elements) yields candidates; per §Probe-strategy schema `probe-arxiv-category`, each candidate title is filtered against ≥2 non-stop-word tokens shared with A1's own cited title ("Agentic Code-Review Loops at Scale") — never the artifact's `tags:` or headings. For this fixture, ground-truth is that no returned candidate clears the title-token filter.

## Expected skill behavior

The skill SHALL emit exactly one probe of strategy kind `probe-arxiv-category` for A1, against `arxiv:cs.SE`, pinned to A1's own cited title. Per the success_criteria DSL, at least one `probe-arxiv-category` emission MUST be detectable in this fixture's expected trajectory.

Both the citation walk and path A yield no surviving candidate for A1, so the skill emits exactly one `probed-no-candidates` row for A1 at `status: pass` — the "probed, found nothing" carrier, never an empty `rows` array. Every row is `pass` → aggregate `verdict: pass`.

Envelope `cache` field SHALL reflect the WebFetch attempts: `{"hits": 0, "misses": 2, "writes": 2}` for a cold-cache resolve + path-A cs.SE probe.

Expected envelope shape:

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
      "cited-value": "Agentic Code-Review Loops at Scale",
      "actual-value": "0 candidates in window",
      "evidence-quote": "https://api.openalex.org/works?filter=cites:W4387355948,from_publication_date:2025-09-01&sort=publication_date:desc&per-page=200&cursor=*"
    }
  ],
  "cache": {"hits": 0, "misses": 2, "writes": 2}
}
```

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect probe-arxiv-category in ~/.claude/skills/source-recency-probe/test-corpus/arxiv-probe.md count >=1`.
