---
title: Fixture — unresolved-source (unresolvable source emits source-unresolved; graph-unknown arXiv source takes path A; others still probed)
date: 2026-09-05
fixture: source-recency-probe
expected_check_name: source-unresolved
expected_status: unverifiable
authored_against: claude-opus-5,2026-01-01
sources:
  - id: S1
    title: "Large Language Models Cannot Self-Correct Reasoning Yet"
    url: "https://arxiv.org/abs/2310.01798"
  - id: S2
    title: "Internal design memo on review gating"
    url: "https://intranet.example.invalid/memo/42"
  - id: S3
    title: "Very New Paper Not Yet Indexed"
    url: "https://arxiv.org/abs/2609.99999"
---

# Fixture — unresolved-source

Recorded responses: S1 resolves (see `source-derived-venues.md`). S2 has no arXiv id, no DOI; the `filter=title.search:` exact-title lookup returns a single hit titled "Review Gating in Continuous Delivery" — normalised titles differ → **unresolvable**. S3's key `10.48550/arXiv.2609.99999` returns 404 from OpenAlex but its arXiv metadata fetch succeeds with `primary_category: cs.SE` → **graph-unknown**, so path A is S3's only probe.

## Expected skill behavior

- S2 → one `source-unresolved` row: `citation-id: S2`, `cited-value: Internal design memo on review gating`, `actual-value: unresolvable`, `evidence-quote: filter=title.search:"Internal design memo on review gating" → hit "Review Gating in Continuous Delivery" (title mismatch)`, `status: unverifiable`.
- S3 → path A: `probe-arxiv-category` on `arxiv:cs.SE` since cutoff, pinned title-token filter against "Very New Paper Not Yet Indexed", cap 3; candidates join the pool with sort key 1 fixed at 0, in both modes. **No** `source-unresolved` row for S3 unless the listing itself fails — and if it does, S3 gets BOTH a `venue-absent-from-sources` row for `venue:arxiv:cs.SE` and a `source-unresolved` row for S3, because path A was S3's only probe.
- S1 → collected and ranked as usual; path A runs for S1 too (always-on for arXiv sources). If neither signal yields a surviving candidate for S1, S1 emits one `probed-no-candidates` row at `pass` rather than no row at all.
- Aggregate: `fail` if any candidate row exists, else `unverifiable` (the S2 row). Never `pass`.

## Success-criteria evidence

Grounds: `detect "source-unresolved" … unresolved-source.md count >=1`.
