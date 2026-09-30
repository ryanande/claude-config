---
title: Fixture — conf:ACL / conf:EMNLP extractor correctness (ACL Anthology paper-card)
date: 2026-05-29
fixture: source-recency-probe
expected_check_name: probe-named-conference
expected_status: pass
authored_against: claude-opus-4-8,2026-01-01
tags: [llm-as-judge]
sources: []
---

# Fixture — conf:ACL / conf:EMNLP extractor

Regression guard for the v1.3 ACL Anthology paper-card selector correction
(RFC-0003 Phase 1 gap). Covers both `conf:ACL` and `conf:EMNLP` (identical
Anthology markup). Asserts the corrected regex against a captured markup sample
so a future catalog regression is caught without a 12 MB live fetch.

## Catalog template under test

Per `../references/query-strategies.md` §Per-conference URL templates:

```
GET https://aclanthology.org/events/acl-<year>/      (conf:ACL)
GET https://aclanthology.org/events/emnlp-<year>/    (conf:EMNLP)
```

Extractor regex (v1.3): `<strong><a class=align-middle href=/<year>\.acl-[a-z]+\.[0-9]+/>`
(substitute `emnlp` for EMNLP). Capture the anchor inner text, stripping nested
`<span class=acl-fixed-case>` casing spans, as the title.

**v1.2 bug:** the documented regex `<strong><a href="/N.NN/">` matched 0 titles
because ACL Anthology serves **unquoted** HTML attributes, the anchor carries a
`class=align-middle` attribute, and the href path is `/<year>.acl-<track>.<n>/`
(not `/N.NN/`).

## Captured markup sample

Verbatim from a live fetch of `acl-2025` on 2026-05-29:

```html
<strong><a class=align-middle href=/2025.acl-long.1/><span class=acl-fixed-case>E</span>com<span class=acl-fixed-case>S</span>cript...</a></strong>
```

Note: the `/<year>.acl-<track>.0/` anchor (paper number `0`) is the proceedings
front-matter, not a paper, and is excluded.

## Assertion

The v1.3 regex MUST yield **more than zero** paper-title anchors against the
captured sample. The v1.2 `<strong><a href="/N.NN/">` regex yields zero and MUST
NOT be restored. Live ground-truth: 1972 anchors on `acl-2025`, 1451 on
`emnlp-2024`.
