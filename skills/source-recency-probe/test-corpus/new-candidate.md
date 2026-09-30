---
title: Fixture — new-candidate (recency-probe surfaces a missing tier-1 paper)
date: 2026-05-19
fixture: source-recency-probe
expected_check_name: new-candidate-found
expected_status: fail
authored_against: claude-opus-4-7,2025-09-01
tags: [llm-review]
sources:
  - id: A1
    title: "Constitutional AI"
    url: "https://arxiv.org/abs/2212.08073"
    year: 2022
  - id: A2
    title: "RLHF: Training language models to follow instructions with human feedback"
    url: "https://arxiv.org/abs/2203.02155"
    year: 2022
---

# Fixture — new-candidate

Survey draft on `llm-review` whose `sources[]` reliably cites pre-cutoff foundational work but is missing a tier-1 post-cutoff paper from a venue in the catalog (`arxiv:cs.SE`).

Ground-truth missing candidate (synthetic for fixture; ID + title shape only):

- `citation-id`: `arxiv:2510.12345`
- venue: `venue:arxiv:cs.SE`
- title: "Programmatic Quality Gates for LLM-Authored Code"
- date: 2025-10-04 (post-cutoff)
- abstract excerpt: "We introduce a continuous-integration substrate that mechanically gates merges by LLM-confidence calibration on test diffs…"

## Expected skill behavior

The skill SHALL emit one `new-candidate-found` row per `../references/query-strategies.md` §probe-arxiv-category extractor, with:

- `check-name`: `new-candidate-found`
- `status`: `fail`
- `citation-id`: `arxiv:2510.12345`
- `cited-value`: `""` (per `../../citation-detail-verify/references/output-schema.md` §Required row fields empty-string semantics for new-candidate rows)
- `actual-value`: `"Programmatic Quality Gates for LLM-Authored Code"`
- `evidence-quote`: the abstract excerpt above

The envelope aggregate `verdict` SHALL be `fail` because the candidate-found row is itself a `fail` row.

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect new-candidate-found in ~/.claude/skills/source-recency-probe/test-corpus/new-candidate.md count >=1`.
