---
title: Source-tier rubric for /survey-author
version: 1.0
status: locked
owners: [survey-author]
consumers: [survey-author]
---

# Source-tier rubric v1.0

Locked at Stage 3 of the research-pipeline skill family. `/survey-author` SHALL use this rubric to classify every `--seed-urls` entry into one of three tiers (or `unverifiable`). Skill-scoped; sibling skills do not consume this reference.

Per the brief at `~/dx-arch-meta/repos/research-docs/content/notes/survey-author-skill-brief.md` §Scope and §Skill-build deliverables, the rubric encodes the typed-source discipline so reused surveys carry the same evidence-weighting convention regardless of consumer repo.

## Tier definitions

### Tier 1 — peer-reviewed / arXiv with numbers — registered-source-tier

Authoritative external evidence. Carries quantitative measurement, methodology, and external review.

Required evidence shape (one OR more):

- Peer-reviewed venue (conference proceedings, journal). DOI present in URL or document body.
- arXiv preprint with measured results (numbers in abstract or body).
- Recognized benchmark report from an academic group.

Examples: `arxiv.org/abs/<id>`, `dl.acm.org`, `ieeexplore.ieee.org`, `aclanthology.org`, `proceedings.mlr.press`.

The `/survey-author` skill SHALL emit one `applied-tier-1-rubric` evidence trace per URL classified at tier 1.

### Tier 2 — research blog with methodology — registered-source-tier

Vendor or independent research blog that publishes measurement methodology, sample sizes, or reproduction-ready descriptions. Distinct from tier 3 by the presence of methodology.

Required evidence shape (one OR more):

- Methodology section naming sample size, dataset, evaluation criteria.
- Reproducibility appendix or linked artifact (code, dataset).
- External-comparison table with named alternatives.

Examples: `research.google`, `openai.com/research`, `anthropic.com/research`, `microsoft.com/research`, `deepmind.com/research`, `eng.uber.com/<post>`, `engineering.fb.com/<post>` — *only when the linked post itself carries methodology, not when the URL points at a hub page.*

The `/survey-author` skill SHALL emit one `applied-tier-2-rubric` evidence trace per URL classified at tier 2.

### Tier 3 — vendor / marketing without measurement — registered-source-tier

Vendor product page, marketing blog post, or thought-leadership content without measurement methodology. Default tier when no other pattern matches.

Indicators:

- Pricing or signup CTA on the page.
- Customer-quote testimonials in place of measurement.
- Product feature list without comparison or benchmark.
- "Leadership perspective" / "manifesto" tone.

The `/survey-author` skill SHALL emit one `applied-tier-3-rubric` evidence trace per URL classified at tier 3.

### Unverifiable — WebFetch could not probe

Distinct from a tier — the rubric could not run. Surfaced as tier label `unverifiable` in the scaffolded `sources:` table and as a Stage 3 driver check-row with `status: unverifiable` per `output-schema.md` §Status semantics.

Trigger conditions:

- WebFetch returns HTTP ≥4xx.
- WebFetch returns non-HTML content type the skill cannot sniff (paywalled PDF behind login, JS-only single-page app, binary blob).
- Network error / timeout.

The `unverifiable` tier label is honest: the author sees the URL is unclassified and can manually re-tier after verification.

## URL-pattern catalog

Two-pass classifier (Decision 9 of `openspec/changes/survey-author-skill/design.md`):

**Pass 1 — URL-pattern match.** Classifies a URL into a tier candidate without fetching. Patterns are stable indicators; matched candidates still require pass-2 confirmation for tier 1 / tier 2 (tier 3 is the default; no confirmation needed).

| Tier candidate | URL pattern (regex-shaped, non-exhaustive) |
|---|---|
| tier-1 | `arxiv\.org/abs/.+` |
| tier-1 | `dl\.acm\.org/doi/.+` |
| tier-1 | `ieeexplore\.ieee\.org/document/.+` |
| tier-1 | `aclanthology\.org/.+` |
| tier-1 | `proceedings\.mlr\.press/.+` |
| tier-1 | `link\.springer\.com/article/.+` |
| tier-2 | `research\.google/pubs/.+` |
| tier-2 | `openai\.com/research/.+` |
| tier-2 | `anthropic\.com/research/.+` |
| tier-2 | `microsoft\.com/.+/research/.+` |
| tier-2 | `deepmind\.com/research/.+` |
| tier-2 | `eng\.uber\.com/.+` |
| tier-2 | `engineering\.fb\.com/.+` |
| (default) | everything else → tier-3 candidate |

The pattern catalog is intentionally short at v1.0. Additions are minor-bump candidates (additive, no consumer migration).

## Content-probe sniff vocabulary

**Pass 2 — WebFetch content probe.** For tier-1 / tier-2 candidates surfaced by pass 1, fetch the URL one-shot and look for tier-specific vocabulary in the response body.

### Tier-1 confirmation vocabulary

The skill confirms tier 1 by sniffing for at least one of:

- Literal substring `Abstract` followed by a paragraph of text within the first 2000 chars.
- Literal substring `DOI:` or `doi.org/` within the first 4000 chars.
- Literal substring `Bibtex` or `@article{` or `@inproceedings{` anywhere in the body.
- Literal substring `Cited by` followed by a numeric count.

No match → re-tier to tier 3. Pass-2 disagreement with pass-1 is intentional (a blog post mirrored under `arxiv.org/abs/` would surface this way).

### Tier-2 confirmation vocabulary

The skill confirms tier 2 by sniffing for at least one of:

- Literal substring `Method` (or `Methodology`) as a section heading.
- Literal substring `sample size` or `n=` followed by a numeric value.
- Literal substring `dataset` followed by a named identifier.
- Literal substring `Reproducibility` or `Code:` followed by a URL.

No match → re-tier to tier 3.

### Tier-3 (no confirmation needed)

The default tier. Pass-2 fetch is skipped for URLs not surfaced by pass-1 as tier-1 / tier-2 candidates.

## Failure modes and dispositions

| Condition | Disposition |
|---|---|
| Pass-1 matches tier-1; pass-2 confirms | Tier 1 (`applied-tier-1-rubric` evidence trace emitted) |
| Pass-1 matches tier-1; pass-2 disagrees | Tier 3 (`applied-tier-3-rubric` evidence trace emitted; URL surfaced under tier-3 by content) |
| Pass-1 matches tier-2; pass-2 confirms | Tier 2 (`applied-tier-2-rubric` evidence trace emitted) |
| Pass-1 matches tier-2; pass-2 disagrees | Tier 3 (`applied-tier-3-rubric` evidence trace emitted) |
| Pass-1 no match | Tier 3 (default; `applied-tier-3-rubric` evidence trace emitted) |
| WebFetch fails on any pass-2 probe | Unverifiable (Stage 3 driver row `status: unverifiable`) |

## Versioning

- Major (`2.0`) — breaking change to the tier vocabulary (tier rename / split / removal). Coordinated with `output-schema.md` if the `applied-tier-*-rubric` extractor names also change.
- Minor (`1.1`) — additive only. New URL patterns in pass 1. New confirmation vocabulary substrings in pass 2. New tier slug (rare; would require an additive `applied-tier-*-rubric` extractor in `output-schema.md` minor bump as well).
- v1.0 is the locked Stage 3 contract. Skill-scoped (`owners: [survey-author]`, `consumers: [survey-author]`); sibling skills do not REUSE this reference.
