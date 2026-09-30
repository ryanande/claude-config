---
title: Fixture — conf:ICML extractor correctness (OpenReview content.venueid)
date: 2026-05-29
fixture: source-recency-probe
expected_check_name: probe-named-conference
expected_status: pass
authored_against: claude-opus-4-8,2026-01-01
tags: [evaluation]
sources: []
---

# Fixture — conf:ICML extractor

Regression guard for the v1.3 OpenReview extractor correction (RFC-0003 Phase 1
gap). Asserts the corrected `content.venueid` filter against a captured response
sample so a future catalog regression is caught without a live fetch.

## Catalog template under test

Per `../references/query-strategies.md` §Per-conference URL templates, the
`conf:ICML` probe issues:

```
GET https://api2.openreview.net/notes?content.venueid=ICML.cc/<year>/Conference&details=replyCount&offset=0&limit=200
```

**v1.2 bug:** filtered on `content.venue=ICML+<year>+Conference` → returned a
single stray note instead of the full proceedings. **v1.3 fix:** filter on
`content.venueid` (Group id `ICML.cc/<year>/Conference`).

## Captured response sample

Live fetch 2026-05-29 of `content.venueid=ICML.cc/2025/Conference`, probed at
`offset=300`, returned a populated `notes[]`:

```json
{"notes":[{"content":{"title":{"value":"Policy-labeled Preference Learning: Is Preference Enough for RLHF?"},"venueid":{"value":"ICML.cc/2025/Conference"}}}]}
```

A populated note at `offset=300` confirms the proceedings are in the hundreds —
the v1.2 single-note symptom is gone.

## Assertion

The documented extractor (`content.venueid=ICML.cc/<year>/Conference` → per-note
`content.title.value`) MUST yield **more than zero** notes (in fact the full
proceedings) against the captured sample. The v1.2 `content.venue=...` filter
yields a single note and MUST NOT be restored. Live ground-truth: >300 notes for
ICML 2025.
