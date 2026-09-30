---
title: Fixture — orphan-citation
date: 2026-05-18
fixture: citation-detail-verify
expected_check_name: frontmatter-body-citation-mismatch
expected_status: fail
sources:
  - {id: A1, title: "When Two LLMs Debate, Both Think They'll Win", url: "https://arxiv.org/abs/2505.19184", tier: 1}
  - {id: A2, title: "A Citation That Appears In Frontmatter But Not Inline", url: "https://arxiv.org/abs/2406.07791", tier: 1}
---

# Fixture — orphan-citation

This decision artifact cites [A1] in the body. The frontmatter `sources[]` declares both A1 and A2 — A2 never appears in the body. Conversely, this paragraph cites [A3] which is NOT listed in frontmatter.

Two distinct pathologies in one fixture:
1. **A2 orphan in frontmatter** — declared as a source but never cited.
2. **A3 orphan in body** — cited inline without being declared as a source.

Running `/citation-detail-verify` MUST emit at least two `frontmatter-body-citation-mismatch` rows (one per orphan), each with `status: fail`, `citation-id` = the orphan ID (A2 or A3), `cited-value` = the side it appears on (`frontmatter` or `body`), `actual-value` = `""` (the side it is missing from).

This exercises brief success_criteria row 7 (`detect frontmatter-body-citation-mismatch ... count >=1`); cardinality is per the spec's open design call (one row per mismatched ID).
