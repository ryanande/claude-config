---
title: Fixture — conf:ICSE extractor correctness (researchr research-track sub-page)
date: 2026-05-29
fixture: source-recency-probe
expected_check_name: probe-named-conference
expected_status: pass
authored_against: claude-opus-4-8,2026-01-01
tags: [code-review]
sources: []
---

# Fixture — conf:ICSE extractor

Regression guard for the v1.3 ICSE researchr template + extractor correction
(RFC-0003 Phase 1 gap). Asserts the corrected sub-page URL and `data-event-modal`
extractor against a captured markup sample so a future catalog regression is
caught without a live fetch.

## Catalog template under test

Per `../references/query-strategies.md` §Per-conference URL templates:

```
GET https://conf.researchr.org/track/icse-<year>/icse-<year>-research-track
```

Extractor regex (v1.3): `data-event-modal="[a-f0-9-]+">([^<]{8,})` — capture
group 1 is the paper title (HTML-unescape `&quot;` etc.); dedupe by the
`data-event-modal` uuid.

**v1.2 bug:** the documented URL was the conference landing page
`https://conf.researchr.org/home/icse-<year>`, which lists **no papers** — the
accepted-paper list lives on the research-track sub-page.

## Captured markup sample

Verbatim from a live fetch of `icse-2026-research-track` on 2026-05-29:

```html
<td><strong><a href="#" data-event-modal="c2cf7556-7e19-40d0-a6dd-85e56b043458">CREME: Robustness Enhancement of Code LLMs via Layer-Aware Model Editing</a></strong></td>
```

## Assertion

The v1.3 extractor MUST yield **more than zero** paper titles against the
captured sample. The v1.2 `home/icse-<year>` URL yields zero papers and MUST NOT
be restored. Live ground-truth: 667 deduped paper titles on
`icse-2026-research-track`.
