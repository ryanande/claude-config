---
title: Fixture — wrong-title
date: 2026-05-18
fixture: citation-detail-verify
expected_check_name: title-match
expected_status: fail
sources:
  - {id: A1, title: "When Two LLMs Debate, Both Are Certain They've Won", url: "https://arxiv.org/abs/2505.19184", tier: 1}
---

# Fixture — wrong-title

This decision artifact cites [A1] with a title that diverges from the fetched arXiv `<title>`. The paper at `https://arxiv.org/abs/2505.19184` is titled "When Two LLMs Debate, Both Think They'll Win" — the cited "Are Certain They've Won" is wrong by several words.

Running `/citation-detail-verify` MUST emit one row with `check-name: title-match`, `status: fail`, `cited-value` set to the fixture's cited title, `actual-value` set to the fetched arXiv title, `evidence-quote` containing the fetched title verbatim.

This is the exact pathology observed in real survey `content/survey/llm-review-landscape.md` for A18; the fixture exercises the check that surfaces it.
