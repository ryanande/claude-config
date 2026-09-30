---
title: Fixture — author-reorder
date: 2026-05-18
fixture: citation-detail-verify
expected_check_name: author-match
expected_status: fail
sources:
  - {id: A1, title: "When Two LLMs Debate, Both Think They'll Win", url: "https://arxiv.org/abs/2505.19184", authors: ["Pradyumna Shyama Prasad", "Jane Q. Fabricated"], tier: 1}
---

# Fixture — author-reorder

This decision artifact cites [A1] with an author list whose SET differs from the fetched arXiv metadata. The cited list adds a fabricated author ("Jane Q. Fabricated") that does not appear in arXiv 2505.19184. The real second author ("Minh Nhat Nguyen") is dropped.

Running `/citation-detail-verify` MUST emit one row with `check-name: author-match`, `status: fail`: cited set `{Pradyumna Shyama Prasad, Jane Q. Fabricated}` ≠ fetched set `{Pradyumna Shyama Prasad, Minh Nhat Nguyen}`.

This exercises the author-drift extractor named in the brief's success_criteria row 3 (`detect author-drift in author-reorder.md count >=1`).
