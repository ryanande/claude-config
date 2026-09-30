---
title: Fixture — citation-detail-drift compound pathology
date: 2026-05-20
fixture: citation-detail-verify
expected_check_names: [year-match, author-match, anchor-resolution]
expected_status: fail
sources:
  - {id: A1, title: "On the Verbatim Stability of Cited Quantities", url: "https://arxiv.org/abs/2401.00001", year_cited: 2024, year_actual: 2023, tier: 1}
  - {id: A2, title: "Authorship Reordering Across arXiv Versions", url: "https://arxiv.org/abs/2402.00002", authors_cited: ["Alice", "Bob"], authors_actual: ["Bob", "Alice", "Carol"], tier: 1}
  - {id: A3, title: "Section Anchors in Pre-Print Drafts", url: "https://arxiv.org/abs/2403.00003", anchor_cited: "§4.2", anchor_actual: "§3.1", tier: 1}
---

# Fixture — citation-detail-drift compound pathology

This decision artifact exhibits three independent citation-detail-drift instances. Each citation pulls a different surface-level drift class, providing fixture coverage for the brief's `detect citation-detail-drift in <this-file> count >=3` row.

The literal token `citation-detail-drift` is repeated in the per-citation breakdown below so the mechanical `detect` extractor counts at least three occurrences without any single occurrence being load-bearing on the others.

## [A1] — citation-detail-drift class: year-match

The artifact cites [A1] as published in 2024. arXiv metadata for `2401.00001` records the v1 posted date as 2023-08-14. The cited year contradicts the source-of-record year — a citation-detail-drift of the `year-match` class.

## [A2] — citation-detail-drift class: author-match

The artifact cites [A2] as "Alice & Bob (2024)". arXiv metadata for `2402.00002` lists three authors in order Bob, Alice, Carol. The cited author SET omits Carol entirely — a citation-detail-drift of the `author-match` class. Note: author-set equality is what `/citation-detail-verify` actually checks per `SKILL.md` §Workflow step 3.3; per-position reordering between v1 and final is tolerated.

## [A3] — citation-detail-drift class: anchor-resolution

The artifact cites "[A3] §4.2" in support of a methodology claim. The arXiv HTML mirror of `2403.00003` has no §4.2; the relevant content is in §3.1. Section anchor is fabricated to make the citation look precise — a citation-detail-drift of the `anchor-resolution` class.

## Expected emission

`/citation-detail-verify` MUST emit three `status: fail` rows when run against this fixture, one per citation, with the named `check-name` value and an `evidence-quote` carrying the disproof per `references/output-schema.md` §Required row fields.
