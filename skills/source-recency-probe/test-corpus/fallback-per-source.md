---
title: Fixture — fallback-per-source (no cross-source citer → per-source cap mode, top 3 each)
date: 2026-09-05
fixture: source-recency-probe
expected_check_name: new-candidate-found
expected_status: fail
authored_against: claude-opus-5,2026-01-01
sources:
  - id: S1
    title: "Paper Alpha"
    url: "https://arxiv.org/abs/2401.00001"
  - id: S2
    title: "Paper Beta"
    url: "https://arxiv.org/abs/2401.00002"
---

# Fixture — fallback-per-source

Synthetic recorded responses: S1 has five post-cutoff citers (A1…A5), S2 has four (B1…B4), no overlap, all `citationCount: 0`, distinct `publicationDate`s.

## Expected skill behavior

No candidate cites ≥ 2 sources → **per-source cap mode** — marker: `top-3-per-source`. Emit S1's three most recent citers and S2's three most recent citers: 6 `new-candidate-found` rows, `cited-value` `[S1]` or `[S2]`, `status: fail`. A4, A5, B4 are not emitted. Aggregate `verdict: fail`.

## Success-criteria evidence

Grounds: `detect "top-3-per-source" … fallback-per-source.md count >=1`.
