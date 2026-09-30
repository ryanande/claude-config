---
title: Fixture — intersection-ranking (a candidate citing two sources outranks a better-cited candidate citing one)
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

# Fixture — intersection-ranking

Synthetic recorded responses:

- Candidate **C1** (`arXiv:2603.00001`, `citationCount: 0`, `publicationDate: 2026-03-01`) appears in the citations of **both** S1 and S2.
- Candidate **C2** (`arXiv:2602.00002`, `citationCount: 40`, `publicationDate: 2026-02-01`) appears only in S1's citations.

## Expected skill behavior

Sort key is (sources-cited desc, citationCount desc, publicationDate desc). C1 scores (2, 0, 2026-03-01); C2 scores (1, 40, 2026-02-01). **C1 ranks first** — marker: `cites-2-sources-outranks`. Because a candidate cites ≥ 2 sources, the emit mode is top-10-overall, not per-source cap mode. Rows: C1 with `cited-value: [S1, S2]`, then C2 with `cited-value: [S1]`. Both `new-candidate-found`, `status: fail`.

## Success-criteria evidence

Grounds: `detect "cites-2-sources-outranks" … intersection-ranking.md count >=1`.
