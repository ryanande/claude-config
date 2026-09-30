---
title: Fixture — venue-gap (path-A listing fails at the HTTP level → venue-absent-from-sources, plus source-unresolved when path A was the only probe)
date: 2026-05-19
fixture: source-recency-probe
expected_check_name: venue-absent-from-sources
expected_status: unverifiable
authored_against: claude-opus-4-7,2025-09-01
sources:
  - id: A1
    title: "Pre-cutoff arXiv cs.SE paper"
    url: "https://arxiv.org/abs/2401.00001"
    year: 2024
  - id: A2
    title: "Very New Paper Not Yet Indexed"
    url: "https://arxiv.org/abs/2609.99998"
    year: 2026
---

# Fixture — venue-gap

Rewritten to v2.0 semantics. The v1 version of this fixture asserted the catalog branch: a `venue:blog:anthropic` entry present in the topic-tag catalog but absent from `sources[]`, emitted at `status: fail`. That branch is **deleted at v2.0** — venue selection no longer comes from a catalog, so "a venue the author should have cited" is no longer a judgement this row can carry, and the `fail` branch became unreachable.

From v2.0 `venue-absent-from-sources` is emitted **only** when a path-A arXiv-category listing fails at the HTTP level, and it is **always** `unverifiable`.

Recorded state for this fixture:

- A1 resolves on the citation graph (`resolved`) and its cited-by walk succeeds. Path A also runs for it (path A is always-on for arXiv sources) against `arxiv:cs.SE`, and that listing returns HTTP 503 twice — once, then again after the 60 s backoff and single retry.
- A2's key `10.48550/arXiv.2609.99998` returns 404 from OpenAlex but its arXiv metadata fetch succeeds with `primary_category: cs.SE` → **graph-unknown**. Path A is A2's **only** probe, and it is the same failing `arxiv:cs.SE` listing.

## Expected skill behavior

Per `references/query-strategies.md` §Source resolution §Path-A listing failure:

- One `venue-absent-from-sources` row for the failed listing:
  - `check-name`: `venue-absent-from-sources`
  - `status`: `unverifiable`
  - `citation-id`: `venue:arxiv:cs.SE` (stable venue identifier per output-schema §Required row fields)
  - `cited-value`: `""`
  - `actual-value`: `"arXiv cs.SE"`
  - `evidence-quote`: `"HTTP 503 after one 60 s backoff and one retry"`
- One `source-unresolved` row for **A2 only**, because path A was A2's only probe and it failed, so nothing probed A2 at all:
  - `citation-id`: `A2`, `cited-value`: `"Very New Paper Not Yet Indexed"`, `actual-value`: `unresolvable`, `status`: `unverifiable`
- **No** `source-unresolved` row for A1: A1 resolved and its citation walk succeeded, so its own evidence base was walked. A1 emits whatever candidate rows that walk produced, or one `probed-no-candidates` row at `pass` if it produced none.

Aggregate `verdict` SHALL be `unverifiable` when no candidate row exists, and `fail` when the A1 walk produced one — a `fail` row dominates `unverifiable` per §Verdict computation. It is never `pass`.

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect venue-absent-from-sources in ~/.claude/skills/source-recency-probe/test-corpus/venue-gap.md count >=1`.
