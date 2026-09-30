---
title: Source URL resolution and full-text availability for /load-bearing-fullread
version: 1.0
status: unlocked
owners: [load-bearing-fullread]
consumers: [load-bearing-fullread]
---

# Source resolution and full-text availability v1.0

Skill-scoped. Defines how `/load-bearing-fullread` turns a `--source-ids` entry into a URL,
how it classifies the fetched body's full-text availability, and which probe templates can run
against each availability class.

This file is `status: unlocked` on purpose. It records venue-specific fetch behaviour measured
against live hosts, and venues change their hosting. Nothing here alters the row shape, the
`check-name` vocabulary, the status semantics, or the cache key derivation — those live in the
locked contracts under `../../citation-detail-verify/references/` and in
`probe-templates.md`, and this file is subordinate to all of them.

## Why this file exists — the defect it replaces

Decision 8 of
`openspec/changes/archive/2026-05-20-load-bearing-fullread-skill/design.md` shipped a
resolution rule keyed on the *shape of the identifier*:

> Derive the candidate URL: `https://arxiv.org/html/<id>v1` (arXiv HTML mirror) if the ID
> matches the arXiv shape (digits + optional letter suffix); otherwise the caller MUST register
> the URL via a sibling skill that has already fetched it (cache lookup).

Two things are wrong with that rule, and both are load-bearing:

1. **The arXiv branch cannot fire for the documented identifier form.** `--source-ids` takes the
   artifact's local citation labels — the skill's own good-brief example is
   `--source-ids A8,A10,A17,A18,A28`, and
   `../../citation-detail-verify/references/output-schema.md` §Required row fields defines
   `citation-id` as "`[Axx]` / `[Bxx]` form by default; configurable per skill". This skill does
   not configure it otherwise: nothing in its SKILL.md, its founding brief, the archived
   `design.md`, `openspec/specs/load-bearing-fullread/spec.md`, or any `test-corpus/` fixture
   documents a raw-arXiv-id input form — `test-corpus/pass-shape.md` pairs `--source-ids A1,A2`
   with an `arxiv.org/html/…v1` `source-url`, which is exactly the output the ID-shape rule
   could not produce from those identifiers. The string `A8` does not match an arXiv shape, so
   for any artifact using `[Axx]` labels no identifier reaches the arXiv branch.
2. **The non-arXiv branch is unkeyable.** A cache lookup is keyed by
   `sha256(normalized_url)` per `../../citation-detail-verify/references/cache-contract.md`
   §Cache key derivation. There is no key derivable from `A8`, so "register the URL via a
   sibling skill (cache lookup)" cannot be performed by an identifier at all.

The consequence is that the written rule resolves no URL for the skill's own documented input
form. That is a property of the rule read against that identifier form, not an observed runtime
trace — the skill is prose, and research-docs RFC-0019 records that the framing chain was never
run over its source set for exactly this reason. Non-arXiv sources were the visible symptom;
arXiv sources fail the same way for the same reason.

The artifact already carries the answer. Where a `sources[]` block exists in the research-docs
corpus, every entry declares both `id:` and `url:` — 482 entries across 27 files, none missing a
`url`. Resolution therefore reads the declared URL and does not derive one.

**Coverage limit.** Not every `[Axx]`-using artifact declares a `sources[]` block at all. Six in
research-docs do not, including `content/rfc/0001-llm-review-strategy.md` — the artifact this
skill's §Invocation discipline good brief and several `test-corpus/` fixtures name — and only 10
of 21 RFCs carry one. Declared-URL resolution does not rescue those: they take the
no-`sources[]`-entry branch and emit `unverifiable` rows, as they did under ID-shape derivation.
The remedy for such an artifact is to declare its sources, which `/citation-detail-verify`
already requires of anything it can check.

This **amends** Decision 8's resolution rule; the rest of Decision 8 (arXiv HTML-mirror
*preference*) is preserved; its rejection of PDF text extraction is reversed at cache-contract
v1.4 — see §Delivered. It is not the "caller-supplied URL
list" alternative Decision 8 rejected — the URL comes from the artifact under probe, not from
the caller, so no new invocation surface is added and no bias surface is opened. No OpenSpec spec
delta is required: `openspec/specs/load-bearing-fullread/spec.md` constrains resolution only by
"the cache key MUST be derived per the lock's §Cache key derivation", which is unchanged. The
archived change folder is immutable history and is not edited — this file is where the amendment
is recorded, and the PR body carries it too.

## Resolution rule

For each `--source-ids` entry, in order:

1. **Match the artifact's declared source.** Parse the artifact's frontmatter `sources:` array
   (or a `## Sources` section enumerating ID → URL pairs, the same two forms
   `../../adversarial-frame/SKILL.md` accepts) and select the entry whose `id` equals the
   requested identifier, with or without surrounding brackets (`A9` matches `A9` and `[A9]`).
2. **No matching entry** → emit one `unverifiable` row per registered probe template, with
   `check-detail: {"resolution": "no-sources-entry"}`.
3. **Matching entry with no `url`** → emit one `unverifiable` row per registered probe template,
   with `check-detail: {"resolution": "sources-entry-has-no-url"}`.
4. **Apply the arXiv HTML-mirror upgrade** (below) to the declared URL.
5. **Record the URL actually fetched** in each row's optional `source-url` field — the field
   `output-schema.md` §Optional row fields already provides for exactly this ("Source URL the
   check ran against. Useful when the citation list resolves to multiple URLs per ID").

Steps 2 and 3 are the only resolution-time terminal states. Everything else proceeds to fetch.

## arXiv HTML-mirror upgrade

Decision 8's preference for `arxiv.org/html` over the abstract page is sound and is kept — but
as an *upgrade applied to the declared URL*, not as a derivation from an identifier, and
without Decision 8's hard-pinned `v1`:

- A declared `https://arxiv.org/abs/<id>` (the form the corpus actually uses) is rewritten to
  `https://arxiv.org/html/<id>`, preserving any version suffix the artifact itself declared.
  `v1` is NOT synthesized: pinning `v1` would silently probe a different revision than the one
  the artifact cites.
- If the `/html/` route returns 404 — the HTML mirror exists only for submissions whose source
  is LaTeX, so a subset of papers have none — fall back to the declared URL unchanged.
- Both the upgraded attempt and the fallback are ordinary fetches through the shared cache per
  `cache-contract.md` §Read protocol: each is cached under its own key, and each is eligible
  for the §Liveness fetch fallback ladder on failure. This is a resolution-layer choice of
  *which* URL to fetch, made before the shared fetch primitive runs; it does not modify the
  primitive or its failure-path-only ladder.

A declared `/abs/` URL whose `/html/` upgrade 404s therefore lands in the `abstract-only`
availability class below. That class is not venue-specific — it is any source whose readable
body carries an abstract but no paper body.

## Full-text availability classification

After a successful fetch, classify the body before running probes. Classification is decided
**by route first, then by content**: `pdftotext` output carries the paper's heading words
unnumbered (`1` / blank / `Introduction`), so an extracted body would otherwise be ambiguous
against the `full-text` heading test.

| Class | Detection (in order) | Meaning |
|-------|----------------------|---------|
| `full-text-unsectioned` | The body being read is `<key>/body.txt` (route `pdf-extract`, per `../../citation-detail-verify/references/cache-contract.md` v1.4 §Read protocol) and its word count is > 1,500. | All four probe templates run over the entire body; `check-detail` carries `{"section": "unsectioned", "route": "pdf-extract"}`. |
| `full-text` | The body being read is `<key>/body` and contains paper body sections — numbered top-level headings such as `Introduction`, `Method(s)`, `Experimental Setup`, `Results`, `Related Work`, `Conclusion`. | All four probe templates run, section-anchored. |
| `abstract-only` | Neither of the above: a title and an abstract but no paper body sections, or an extracted body under the word floor. | Only the probes whose locked evidence shape admits abstract-level grounding can run (see §Per-probe availability). |

A body read via `body.txt` is never `full-text`, whatever heading words it contains. The
1,500-word floor guards against a one-page abstract or cover sheet served as PDF; every full
paper measured 2026-09-14 is at least 3,370 words. It is a design intuition and revisable here
in place.

Classification is a property of the body actually fetched — and, from v1.4, of which file of the
cache entry is being read — not of the venue. A venue that starts serving HTML full text is
picked up with no change to this file.

## Per-probe availability

`probe-templates.md` v1.0 states, per template, the paper section its expected evidence lives
in. What decides whether a probe can run against an `abstract-only` body is where that template
locates the paper-side evidence that would *disprove* the artifact's framing — the skill does
not invent a status floor of its own:

| Probe template | Locked section holding the disproving evidence | Runs on `abstract-only`? |
|----------------|-----------------------------------------------|--------------------------|
| `framing-drift-relative-vs-absolute` | "Paper's Methods or Results section reports the absolute baseline … and the absolute final value" | No — the template's first bullet does name the abstract ("Abstract reports `+X%` improvement or `Nx` lift on a metric"), but that is the *cited*-side signal; the absolute baseline that reframes it is in Methods or Results, and is by construction absent from an abstract. |
| `framing-drift-domain-transfer` | "Paper's Abstract, Introduction, or Methods explicitly names the measurement domain" | **Yes** — the abstract is a listed location for the disproving evidence itself. |
| `framing-drift-flow-direction` | "Paper's Methods or System Design section explicitly names the direction of measurement" | No. |
| `framing-drift-scope-mismatch` | "Paper's Methods or Experimental Setup section explicitly names the input scope" | No. |

On a `full-text-unsectioned` body every template runs: the disproving evidence each template
locates in Methods / Results / Experimental Setup / System Design is present in the body but not
labelled, so it is sought in the whole body. `check-detail` records
`{"section": "unsectioned", "route": "pdf-extract"}` in place of a named section.
`evidence-quote` on a `fail` remains verbatim primary-source text, matched under
`cache-contract.md` v1.4 §Extracted text match key.

Consequences, which follow from the locked semantics rather than adding to them:

- On an `abstract-only` source, `framing-drift-domain-transfer` **runs**, and takes `pass` or
  `fail` per `output-schema.md` §Status semantics with no modification. A `fail` quotes the
  abstract sentence naming the measured domain in `evidence-quote`; the lock requires the quote
  be verbatim primary-source text, and an abstract is primary-source text.
- The other three probes **could not run**, which is precisely the condition `output-schema.md`
  §Status semantics assigns `unverifiable` to: "check could not run because the source format /
  availability prevents mechanical verification (paywall, PDF without HTML mirror, venue API
  failure)". Each emits `unverifiable` with `check-detail` naming the availability class and the
  routes attempted, as `cache-contract.md` §Liveness fetch fallback requires of any row that
  reaches ladder step 4.
- Three of four rows per `abstract-only` source are therefore structurally `unverifiable`. They
  are emitted anyway, and that is the point: an emitted `unverifiable` row naming its attempted
  routes is auditable evidence that the probe was attempted and floored, which is the
  "probed, found nothing" versus "never probed" distinction `output-schema.md` §Verdict
  computation requires a consumer to be able to make. It is not a `pass`.

An artifact whose sources are all `abstract-only` will therefore produce an aggregate
`verdict: unverifiable` on every run unless a `framing-drift-domain-transfer` row fails. That
is an accepted, recorded outcome, not a defect to be papered over — see §Delivered.

## Full-text mirror hop for abstract-only venues

An abstract-serving landing page can still resolve to a full-text mirror elsewhere, so a source
is not classified `abstract-only` until that has been tried. This hop is a **skill-scoped
requirement of this file**, modeled on `cache-contract.md` §Liveness fetch fallback step 3 —
which names "a structured bibliographic API (dblp, Semantic Scholar Graph API …)" as a canonical
alternate authoritative route — but it is NOT that ladder firing, and the lock does not mandate
it here. The lock's ladder is explicitly "**Failure-path only.** The ladder fires only when step
1 fails; the common `200`-first case is unchanged", and an abstract-only landing page returns a
perfectly good `200`. What triggers this hop is a *content* gap, not a fetch failure, and the
cost it adds is additive to the lock's stated worst case rather than covered by it.

The hop runs only for a body that classified `abstract-only`. A `full-text` body never needs it.

1. Obtain the DOI. Where the venue's DOI pattern is known, derive it from the identifier rather
   than spending a request — ACL Anthology's is `10.18653/v1/<anthology-id>`, verified against
   the landing page's own `citation_doi` value. For an unknown venue, read `citation_doi` from a
   raw fetch of the landing page (`WebFetch` cannot supply it — see §Venue note).
2. Query the Semantic Scholar Graph API for that DOI, e.g.
   `https://api.semanticscholar.org/graph/v1/paper/DOI:<doi>?fields=title,externalIds,openAccessPdf`.
   Prefer the `paper/batch` POST endpoint when several sources are being resolved in one run:
   one request for up to hundreds of DOIs instead of one per source.
3. If the response's `externalIds.ArXiv` is present, fetch `https://arxiv.org/html/<arxiv-id>`.
   A 200 with body sections reclassifies the source `full-text`, and all four probes run.
4. If the DOI is not indexed, the arXiv id is absent, or its `/html/` route 404s, proceed to
   step 5.
5. **PDF extraction route.** Locate the PDF: the `citation_pdf_url` meta tag from a raw fetch of
   the landing page (not visible through `WebFetch`; match on the tag *name*, see §Venue note),
   or the venue rule where known — ACL Anthology is `https://aclanthology.org/<id>.pdf`. Fetch it
   through the shared cache. "Raw fetch" here and in §Venue note is the same byte-preserving
   `curl` download `cache-contract.md` v1.4 §Read protocol defines for a PDF response — not
   `WebFetch`, which cannot return binary bytes or a page's `<head>` metadata. The miss-path
   write extracts `body.txt` per that §Read protocol, but only when the extraction's word count
   is `> 0`; a text-less PDF is `status: "ok", words: 0` with no `body.txt` written at all. If
   `body.txt` is present and non-empty with > 1,500 words → `full-text-unsectioned`. Otherwise
   the source is `abstract-only`, and every floored row's `check-detail` carries
   `route: "pdf-extract"` and `reason` from `meta.json.extracted_text.status`
   (`pdftotext-not-on-PATH`, `pdftotext-failed`, or `not-extracted`).

The arXiv HTML mirror stays ahead of the PDF because it is sectioned; the PDF is the fallback
that catches the arXiv-404 case (`2026.acl-long.406` → `2510.18619` returns 404).

**Request budget.** Per `abstract-only` source this adds at most one Semantic Scholar query
(amortized to a fraction of one when batched) plus one arXiv fetch, and one raw landing-page
fetch only for a venue whose DOI pattern is unknown, plus one PDF fetch per source that reaches
step 5. For a 13-source artifact that is one batch query plus one arXiv fetch per source that
has an arXiv id — 3 in the ACL case measured below, not 13.

**Backoff.** The unauthenticated Semantic Scholar API is rate-limited and returns
`{"message": "Too Many Requests. Please wait and try again or apply for a key for higher rate
limits. …", "code": "429"}` under modest use — observed once while measuring the ACL set, and
recovered after roughly 75 seconds. A 429 is a retry trigger, not a verdict: back off once
before treating the hop as failed, and record the routes attempted in `check-detail` either way.

## Venue note — ACL Anthology (`aclanthology.org`)

Measured 2026-09-04 against live hosts, serial requests, ≥3 s spacing, naming `User-Agent`, over
the 13 Anthology sources cited by RFC-0019 as it stands on the research-docs branch
`survey/self-correction-loop-conditions` at commit `75eab6c` —
`content/rfc/0019-ground-agentic-loops-in-external-verification.md`, which is not on
research-docs `main` and shares its number with an unrelated unmerged RFC-0019, so cite the
commit when re-deriving these numbers:

- **Landing page `https://aclanthology.org/<id>/`** — 13/13 HTTP 200. Serves title, authors,
  **abstract**, the Anthology metadata block, and the "Correct Metadata" GitHub-issue form
  boilerplate. No paper body prose. `WebFetch` against one returned the title and the complete
  abstract, and reported that no body section headings were present. This is the
  `abstract-only` class.
- **PDF `https://aclanthology.org/<id>.pdf`** — 13/13 HTTP 200 `application/pdf`, and it holds
  the full text. `WebFetch` against it reports that it cannot read the document body, the
  content being a binary PDF with FlateDecode-compressed streams: `WebFetch` cannot read it, but
  from cache-contract v1.4 the miss-path write extracts `body.txt` with `pdftotext` when poppler
  is present. Re-measured 2026-09-14: 13 of 13 extract, 3,370–28,791 words each (A20, A18),
  abstract intact, one form feed per page. With poppler present all 13 reach
  `full-text-unsectioned`; the 2 with arXiv HTML mirrors (`2026.acl-long.96`,
  `2026.acl-demo.3`) still take the sectioned route first.
- **Full-text mirror hop** — 3 of the 13 DOIs carry an `externalIds.ArXiv` in Semantic Scholar
  (4 of the 13 are not indexed there at all, and 6 are indexed with no arXiv id), and 2 of those
  3 arXiv ids have a live `arxiv.org/html` mirror: `2026.acl-long.96` → `2509.00930` (200, 8
  sections) and `2026.acl-demo.3` → `2605.18032` (200, 6 sections), while
  `2026.acl-long.406` → `2510.18619` returns 404. So §Full-text mirror hop reclassifies **2 of
  13** sources `full-text`; the remaining 11 are genuinely `abstract-only`.
- **Meta tags** — the landing page authoritatively declares the PDF and the DOI:
  `citation_pdf_url`, `citation_doi`, `citation_title`, `citation_author`. Match on the tag
  *name*; do NOT write an attribute-order-sensitive pattern. The page is minifier-generated and
  emits attributes in reversed order with the name unquoted —
  `<meta content="https://aclanthology.org/2026.acl-long.96.pdf" name=citation_pdf_url>` —
  which has already broken naive regexes elsewhere in this repo, and which a minifier change
  could reverse again. Separately, these meta tags are **not visible through `WebFetch`**: its
  markdown conversion drops `<head>` metadata, so the DOI needed for the §Full-text mirror hop
  must come from a raw fetch of the landing page.

## Delivered — PDF text extraction (cache-contract v1.4)

Until 2026-09-14 this section was titled "Not yet deliverable" and recorded four objections to
extracting text from a PDF body. Decision 8 of the founding change had rejected the route
outright ("*Accept PDF mirrors and OCR them.* Rejected: out of scope per brief §Out of scope").
That rejection is **reversed** by
`docs/superpowers/specs/2026-09-14-pdf-text-extraction-design.md` (D1–D7) and OpenSpec change
`pdf-text-extraction`; the archived change folder is immutable history and is not edited.

What the objections became:

- `WebFetch` cannot read PDF bodies; `Read` renders page images — true and irrelevant: the cache
  holds the raw bytes and `pdf_extract.py` extracts on disk.
- `pdftotext` output is not verbatim-clean — two parts. Hyphen and page-break damage is handled
  by matching on the `norm-v1` key (`cache-contract.md` v1.4 §Extracted text match key), not by
  repairing the text; 41 of 80 measured line-final hyphens are interrupted by page furniture and
  stay unmatchable, reported `unverifiable` with `reason: "quote-spans-page-break"`. Heading
  reassembly is not attempted; the body is classified `full-text-unsectioned` and probed whole
  (§Full-text availability classification).
- Poppler is not provisioned — still true; absence degrades to the pre-v1.4 terminal state with
  a named cause (`cache-contract.md` §Deployment assumption).

An artifact whose sources are all PDF-only therefore produces a full four-row probe set per
source on a machine with poppler, and the same `unverifiable`-floored rows as before on a
machine without it, each naming the missing route.

## Note on the pre-existing fixtures

Six `test-corpus/` fixtures predating this file show `source-url` values pinned at
`https://arxiv.org/html/<id>v1`. Under §arXiv HTML-mirror upgrade those are read as *declared*
versions — an artifact that cites `arxiv.org/abs/<id>v1` upgrades to `.../html/<id>v1`, which is
exactly what those fixtures show. What no longer happens is `v1` being *synthesized* for a
declared URL that carries no version suffix. The fixtures are therefore consistent with the new
rule without being rewritten, and are deliberately left untouched by this change.

## Versioning

- This file is unlocked; venue notes and route measurements are expected to be revised in place
  with the measurement date updated.
- Changes to the row shape, `check-name` vocabulary, status semantics, verdict computation, or
  cache key derivation are NOT made here. They belong to the locked contracts and follow their
  own versioning rules.
