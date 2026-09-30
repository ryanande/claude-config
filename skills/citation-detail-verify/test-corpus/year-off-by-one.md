---
title: Fixture — year-off-by-one
date: 2026-05-18
fixture: citation-detail-verify
expected_check_name: year-match
expected_status: fail
sources:
  - {id: A1, title: "When Two LLMs Debate, Both Think They'll Win", url: "https://arxiv.org/abs/2505.19184", year: 2024, tier: 1}
---

# Fixture — year-off-by-one

This decision artifact cites [A1] as a 2024 publication. The arXiv ID `2505` decodes to May 2025 (arXiv's `YYMM` ID prefix), and the v1 metadata date is 2025. Cited year is wrong by one year.

Running `/citation-detail-verify` MUST emit one row with `check-name: year-match`, `status: fail`, `cited-value: "2024"`, `actual-value: "2025"`.

Note: arXiv v1 vs final-version year disagreement is surfaced as `pass` with `confidence: medium` per SKILL.md §Workflow 3.iv — that's NOT this fixture's pathology. This fixture is hard year drift, not v1-vs-final.
