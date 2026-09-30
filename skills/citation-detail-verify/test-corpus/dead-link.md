---
title: Fixture — dead-link
date: 2026-05-18
fixture: citation-detail-verify
expected_check_name: url-liveness
expected_status: fail
sources:
  - {id: A1, title: "A Paper That Definitely Exists Somewhere", url: "https://arxiv.org/abs/9999.99999", tier: 1}
---

# Fixture — dead-link

This decision artifact cites [A1], whose URL `https://arxiv.org/abs/9999.99999` resolves to a 404 page on arXiv. Running `/citation-detail-verify --artifact <this-file>` MUST emit one row with `check-name: url-liveness`, `status: fail`, `citation-id: [A1]`.

The 9999.99999 form is intentionally past the arXiv numbering sequence so the URL is stable-dead, not transient-dead.
