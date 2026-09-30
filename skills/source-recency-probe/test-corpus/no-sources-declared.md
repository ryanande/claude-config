---
title: Fixture — no-sources-declared (artifact has no sources[]; exactly one nothing-to-probe row)
date: 2026-09-05
fixture: source-recency-probe
expected_check_name: nothing-to-probe
expected_status: unverifiable
authored_against: claude-opus-5,2026-01-01
tags: [controlled-natural-language, method]
---

# Fixture — no-sources-declared

An RFC-shaped artifact that cites by reference to other corpus documents and declares no `sources[]` (the RFC-0021 case, 2026-09-04). Its `tags:` are irrelevant and not read.

## Expected skill behavior

Exactly one row: `check-name: nothing-to-probe`, `citation-id: sources:<none>`, `cited-value: ""`, `actual-value: ""`, `evidence-quote: ""`, `status: unverifiable`. Aggregate `verdict: unverifiable`. No network request is made. No `topic-tag-uncatalogued` row.

## Success-criteria evidence

Grounds: `detect "nothing-to-probe" … no-sources-declared.md count >=1` and `detect "sources:<none>" … no-sources-declared.md count >=1`.
