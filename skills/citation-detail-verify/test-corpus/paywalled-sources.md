---
title: Fixture — paywalled-sources
date: 2026-05-18
fixture: citation-detail-verify
expected_check_name: title-match
expected_status: unverifiable
sources:
  - {id: A1, title: "A Paper Behind A Paywall", url: "https://dl.acm.org/doi/10.1145/0000000.0000000", tier: 1}
  - {id: A2, title: "A Paper Whose Source Is PDF-Only With No HTML Mirror", url: "https://example.com/papers/no-html-mirror.pdf", tier: 1}
---

# Fixture — paywalled-sources

This decision artifact cites [A1] (paywalled DOI) and [A2] (PDF-only).

For both citations the mechanical checks (`title-match`, `author-match`, `year-match`, `verbatim-quote-match`, `anchor-resolution`) cannot run because the source format prevents WebFetch-based extraction:
- A1: paywall returns metadata stub, not full text; title may match but quote / anchor checks fail to reach the body.
- A2: PDF-only; HTML scraping is unavailable; PDF text extraction is out of scope for v1 per brief §Open questions.

Running `/citation-detail-verify` MUST emit rows with `status: unverifiable` — NOT `fail`. The fail-vs-unverifiable distinction is load-bearing per `references/output-schema.md` §Status semantics. The brief's `absent`-primitive row over this fixture asserts that the FAIL-pathology compound token never appears here — keep the fixture free of that literal.

This fixture is a paywalled-source-finding case.
