---
title: Fixture — quote-paraphrased
date: 2026-05-18
fixture: citation-detail-verify
expected_check_name: verbatim-quote-match
expected_status: fail
sources:
  - {id: A1, title: "When Two LLMs Debate, Both Think They'll Win", url: "https://arxiv.org/abs/2505.19184", tier: 1}
---

# Fixture — quote-paraphrased

[A1] reports that debating models begin debates at "approximately seventy-three percent average confidence" and escalate to "approximately eighty-three percent." The arXiv abstract reports these numbers numerically as 72.9% and 83%; the words "seventy-three" and "eighty-three" do NOT appear in the source text.

Running `/citation-detail-verify` MUST emit at least one row with `check-name: verbatim-quote-match`, `status: fail`, `cited-value` containing the spelled-out phrase, `actual-value` containing the verbatim numeric form found in the source.

This exercises the verbatim-quote-mismatch extractor named in brief success_criteria row 5.
