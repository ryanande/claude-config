---
title: Fixture — conf:NeurIPS extractor correctness (OpenReview content.venueid)
date: 2026-05-29
fixture: source-recency-probe
expected_check_name: probe-named-conference
expected_status: pass
authored_against: claude-opus-4-8,2026-01-01
tags: [llm-review]
sources: []
---

# Fixture — conf:NeurIPS extractor

Regression guard for the v1.3 OpenReview extractor correction (RFC-0003 Phase 1
gap). Asserts the corrected `content.venueid` filter against a captured response
sample so a future catalog regression is caught without a live fetch.

## Catalog template under test

Per `../references/query-strategies.md` §Per-conference URL templates, the
`conf:NeurIPS` probe issues:

```
GET https://api2.openreview.net/notes?content.venueid=NeurIPS.cc/<year>/Conference&details=replyCount&offset=0&limit=200
```

**v1.2 bug:** the template filtered on `content.venue=NeurIPS+<year>+Conference`
(the display string), which returned `{"notes":[],"count":0}` — a 0-match result
indistinguishable from a clean "no new candidates" pass. **v1.3 fix:** filter on
`content.venueid` (the Group id `NeurIPS.cc/<year>/Conference`), resolved via the
venue-id discovery sub-step.

## Captured response sample

Live fetch 2026-05-29 of `content.venueid=NeurIPS.cc/2025/Conference` (shape
elided to one note):

```json
{"notes":[{"content":{"title":{"value":"Time-o1: Time-Series Forecasting Needs Transformed Label Alignment"},"venueid":{"value":"NeurIPS.cc/2025/Conference"}}}]}
```

A probe at `offset=300` against the same `content.venueid` still returns a
populated `notes[]` (title `Complete Structure Guided Point Cloud Completion via
Cluster- and Instance-Level Contrastive Learning`), confirming the proceedings
are in the hundreds, not a single stray note.

## Assertion

The documented extractor (`content.venueid=NeurIPS.cc/<year>/Conference` →
per-note `content.title.value`) MUST yield **more than zero** notes against the
captured sample. The v1.2 `content.venue=...` filter yields zero and MUST NOT be
restored. Live ground-truth: >300 notes for NeurIPS 2025.
