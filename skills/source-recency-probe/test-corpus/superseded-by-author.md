---
title: Fixture — superseded-by-author (author overlap with the cited source emits source-superseded-by-newer)
date: 2026-09-05
fixture: source-recency-probe
expected_check_name: source-superseded-by-newer
expected_status: fail
authored_against: claude-opus-5,2026-01-01
sources:
  - id: S1
    title: "Paper Alpha"
    url: "https://arxiv.org/abs/2401.00001"
    authors: [Huang, J., Chen, X.]
---

# Fixture — superseded-by-author

Synthetic recorded response: candidate C1 (`arXiv:2605.00001`, `publicationDate: 2026-05-10`) cites S1 and lists `authors: [{"name":"Jie Huang"}, {"name":"Zhou, D."}]`.

## Expected skill behavior

Normalised author keys: S1 → `{huang j, chen x}`; C1 → `{huang j, zhou d}`. Overlap on `huang j` → row kind **`source-superseded-by-newer`**, anchored on the existing source: `citation-id: S1`, `cited-value: Paper Alpha`, `actual-value: <C1 title> · 2026-05-10 · arXiv:2605.00001`, `evidence-quote: <C1 title>`, `status: fail`. Not `new-candidate-found`.

## Success-criteria evidence

Grounds: `detect "source-superseded-by-newer" … superseded-by-author.md count >=1`.
