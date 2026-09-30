---
title: Fixture — superseded (recency-probe surfaces same-author post-cutoff supersession)
date: 2026-05-19
fixture: source-recency-probe
expected_check_name: source-superseded-by-newer
expected_status: fail
authored_against: claude-opus-4-7,2025-09-01
tags: [llm-review]
sources:
  - id: A1
    title: "Older Result on Reviewer Calibration (v1)"
    authors: [Doe, Roe]
    url: "https://arxiv.org/abs/2403.99999"
    year: 2024
---

# Fixture — superseded

Survey cites paper A1 (Doe, Roe — 2024). Ground-truth: the same authors landed a strictly stronger follow-up post-cutoff (synthetic for fixture):

- superseding `citation-id`: `arxiv:2511.00001`
- title: "Reviewer Calibration: A Refined Analysis with Larger Cohorts (v2)"
- authors: [Doe, Roe, Poe]
- date: 2025-11-04 (post-cutoff)
- abstract excerpt: "We extend our 2024 analysis to a 10× larger cohort and show the earlier confidence-interval estimate was too narrow by a factor of 2…"

## Expected skill behavior

The skill SHALL emit one `source-superseded-by-newer` row per `../references/query-strategies.md` §probe-arxiv-category extractor, with:

- `check-name`: `source-superseded-by-newer`
- `status`: `fail`
- `citation-id`: `A1` (the existing citation's identifier per output-schema §Check-name vocabulary for source-superseded-by-newer)
- `cited-value`: `"Older Result on Reviewer Calibration (v1)"`
- `actual-value`: `"Reviewer Calibration: A Refined Analysis with Larger Cohorts (v2)"`
- `evidence-quote`: the abstract excerpt above

Aggregate `verdict` SHALL be `fail`.

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect source-superseded-by-newer in ~/.claude/skills/source-recency-probe/test-corpus/superseded.md count >=1`.
