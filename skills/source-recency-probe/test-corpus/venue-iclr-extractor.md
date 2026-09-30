---
title: Fixture — conf:ICLR extractor correctness (OpenReview content.venueid)
date: 2026-05-29
fixture: source-recency-probe
expected_check_name: probe-named-conference
expected_status: pass
authored_against: claude-opus-4-8,2026-01-01
tags: [evaluation]
sources: []
---

# Fixture — conf:ICLR extractor

Regression guard for the v1.3 OpenReview extractor correction (RFC-0003 Phase 1
gap). Asserts the corrected `content.venueid` filter against a captured response
sample so a future catalog regression is caught without a live fetch.

## Catalog template under test

Per `../references/query-strategies.md` §Per-conference URL templates, the
`conf:ICLR` probe issues:

```
GET https://api2.openreview.net/notes?content.venueid=ICLR.cc/<year>/Conference&details=replyCount&offset=0&limit=200
```

**v1.2 bug:** filtered on `content.venue=ICLR+<year>+Conference` → empty
response. **v1.3 fix:** filter on `content.venueid` (Group id
`ICLR.cc/<year>/Conference`).

## Captured response sample

Live fetch 2026-05-29 of `content.venueid=ICLR.cc/2025/Conference`, probed at
`offset=300`, returned a populated `notes[]`:

```json
{"notes":[{"content":{"title":{"value":"No Need to Talk: Asynchronous Mixture of Language Models"},"venueid":{"value":"ICLR.cc/2025/Conference"}}}]}
```

## Assertion

The documented extractor (`content.venueid=ICLR.cc/<year>/Conference` → per-note
`content.title.value`) MUST yield **more than zero** notes against the captured
sample. The v1.2 `content.venue=...` filter yields zero and MUST NOT be restored.
Live ground-truth: >300 notes for ICLR 2025.
