---
title: Fixture — fake-section-ref
date: 2026-05-18
fixture: citation-detail-verify
expected_check_name: anchor-resolution
expected_status: fail
sources:
  - {id: A1, title: "When Two LLMs Debate, Both Think They'll Win", url: "https://arxiv.org/abs/2505.19184", tier: 1}
---

# Fixture — fake-section-ref

[A1] §99.99 reports a finding about ensemble overconfidence. The paper has no §99.99 — it is a fabricated section reference designed to look precise.

Running `/citation-detail-verify` MUST emit one row with `check-name: anchor-resolution`, `status: fail` — the cited paper is HTML-mirrored on arXiv and contains no §99.99, so the anchor resolves negatively.

This exercises the anchor-fabrication extractor named in brief success_criteria row 6.
