---
title: Output schema for /citation-detail-verify and sibling research-pipeline skills
version: 2.0
status: locked
owners: [citation-detail-verify]
consumers: [citation-detail-verify, load-bearing-fullread, adversarial-frame, source-recency-probe, survey-refresh, invocation-discipline-lint]
---

# Output schema — wire v1.0 (lock document v2.0)

Locked at Stage 1 (citation-detail-verify) of the research-pipeline skill family. Two version numbers move independently and must not be conflated: the **wire** `version` field every envelope carries (`"1.0"`, unchanged since Stage 1) and this **lock document's** frontmatter `version` (`2.0`, this file's own metadata). The schema is REUSED unchanged by all six consumers named in the frontmatter `consumers:` list — `citation-detail-verify`, `load-bearing-fullread`, `adversarial-frame`, `source-recency-probe`, `survey-refresh`, `invocation-discipline-lint`. Downstream skills SHALL NOT extend or shadow row fields; check-name vocabulary is skill-scoped (each skill registers its own enum values) but row shape is fixed.

## Envelope

Top-level JSON object emitted per invocation:

```json
{
  "version": "1.0",
  "skill": "<skill-slug>",
  "artifact": "<absolute-path-or-uri>",
  "invoked_at": "<ISO-8601 UTC>",
  "verdict": "pass | fail | unverifiable",
  "rows": [ /* one or more row objects, see below */ ]
}
```

### Envelope required fields

| Field | Type | Notes |
|-------|------|-------|
| `version` | string | MUST equal `"1.0"`. Breaking changes bump the major; minor additions to optional row fields bump the minor. Consumers MUST fail closed on unknown major. |
| `skill` | string | Producing skill slug, e.g. `citation-detail-verify`, `load-bearing-fullread`, `adversarial-frame`, `source-recency-probe`. |
| `artifact` | string | Decision artifact path (or URI) the skill ran against. Absolute when local; URL otherwise. |
| `invoked_at` | string | ISO-8601 UTC timestamp, second precision. |
| `verdict` | string | Aggregate verdict over all rows. Computation rules below. |
| `rows` | array | One element per (citation, check). Empty array when artifact has zero citations AND skill ran cleanly. |

### Envelope optional fields

| Field | Type | Notes |
|-------|------|-------|
| `cache` | object | Cache telemetry: `{"hits": N, "misses": N, "writes": N}`. REQUIRED for skills that consume `references/cache-contract.md`; OPTIONAL for skills that do not fetch. |
| `notes` | string | Free-text. Suppressed when empty. Never load-bearing. |

## Row shape

```json
{
  "citation-id": "<string>",
  "check-name": "<string>",
  "status": "pass | fail | unverifiable",
  "cited-value": "<string>",
  "actual-value": "<string>",
  "evidence-quote": "<string>"
}
```

### Required row fields

| Field | Type | Empty-string semantics |
|-------|------|------------------------|
| `citation-id` | string | The artifact's local identifier for the citation: `[Axx]` / `[Bxx]` form by default; configurable per skill. For `source-recency-probe` `new-candidate-found` rows where no prior citation is being compared, `citation-id` holds the candidate's identifier (e.g., arXiv ID of the missing paper). For `source-recency-probe` `venue-absent-from-sources` rows where no per-citation identifier exists, `citation-id` holds a stable venue identifier (e.g., `venue:arxiv:cs.SE`). MUST NOT be empty; `source-recency-probe` also uses the artifact's own source id (e.g. `S3`) on `source-unresolved` and on `probed-no-candidates`, and the literal `sources:<none>` on `nothing-to-probe`. |
| `check-name` | string | Skill-scoped enum value. MUST NOT be empty. See §Check-name vocabulary. |
| `status` | string | Enum: `pass` \| `fail` \| `unverifiable`. MUST NOT be empty. Semantics in §Status semantics. |
| `cited-value` | string | The value as it appears in the artifact (cited year, cited title, current framing, current weighting, etc.). Empty string PERMITTED when no prior cited value exists — `source-recency-probe` `nothing-to-probe` rows (where all three value fields are empty), `citation-detail-verify` url-liveness pass with no in-artifact assertion to compare against. Empty string MUST be the literal empty string `""`, never `null` or omitted. |
| `actual-value` | string | The value the skill derived from the source (fetched title, publication year, alternative framing, candidate paper title, etc.). Empty string PERMITTED on `unverifiable` rows where derivation could not run. Same null-rule as `cited-value`. |
| `evidence-quote` | string | Verbatim quote grounding the row in primary evidence. Semantics depend on skill class: for verification skills (citation-detail-verify, load-bearing-fullread) the quote carries the disproof of the cited value on `fail`; for generative skills (adversarial-frame) the quote carries the source-evidence-grounding of the alternative; for `source-recency-probe` the quote carries the verbatim candidate title on `new-candidate-found` / `source-superseded-by-newer`, the failed lookup or cap name on `source-unresolved`, the cited-by query URL that was walked on `probed-no-candidates`, and is empty on `nothing-to-probe`. For `fail` rows the quote MUST be non-empty regardless of skill class. For `pass` rows the quote MAY be empty (mechanical check, no quotable evidence). For `unverifiable` rows the quote MAY be empty. |

### Optional row fields

| Field | Type | Notes |
|-------|------|-------|
| `check-detail` | object | Skill-specific structured metadata. Examples: `{"http_status": 404}` for citation-detail-verify url-liveness; `{"venue": "arXiv cs.SE", "date": "2026-03-04"}` for source-recency-probe candidates. Never overrides required-field meaning. |
| `confidence` | string | Enum: `high` \| `medium` \| `low`. Populated only by skills whose check is LLM-driven (adversarial-frame, source-recency-probe extractor stage). Absent on purely mechanical rows. |
| `source-url` | string | Source URL the check ran against. Useful when the citation list resolves to multiple URLs per ID. |

## Check-name vocabulary

Each skill registers its own enum of `check-name` values. This lock enumerates the vocabulary contributed by the six consumers named in the frontmatter `consumers:` list; future skills register additions via PR against this file. Additions are additive; a registered name may be DEPRECATED (kept registered so older envelopes still parse, never emitted again) only at a major bump of this lock document — never removed.

### citation-detail-verify

- `url-liveness` — `WebFetch` returned a usable response (2xx, or 3xx to a live target).
- `title-match` — fetched title matches cited title.
- `author-match` — fetched author list matches cited author list per skill rules.
- `year-match` — fetched publication year matches cited year.
- `verbatim-quote-match` — cited verbatim quote / number appears verbatim in source full text.
- `anchor-resolution` — cited section / page / figure / table reference resolves in source.
- `frontmatter-body-citation-mismatch` — citation appears in frontmatter `sources[]` XOR inline `[Axx]` refs.

### load-bearing-fullread

- `framing-drift-relative-vs-absolute`
- `framing-drift-domain-transfer`
- `framing-drift-flow-direction`
- `framing-drift-scope-mismatch`

### adversarial-frame

- `surfaced-alternative-interpretation` — `cited-value` holds the artifact's current interpretation; `actual-value` holds the alternative.
- `surfaced-alternative-weighting` — `cited-value` holds the current weighting; `actual-value` holds the alternative weighting.
- `surfaced-alternative-composition` — `cited-value` holds the current composition story; `actual-value` holds the alternative.

### source-recency-probe

- `new-candidate-found` — `citation-id` holds the candidate's identifier (`arXiv:<id>`, else `DOI:<doi>`, else `openalex:<W-id>`); `cited-value` holds the list of the artifact's source ids the candidate cites (e.g. `[S1, S4]`); `actual-value` holds `title · publication_date · cited_by_count`; `evidence-quote` holds the verbatim candidate title. Always `status: fail`.
- `venue-absent-from-sources` — venue-id rows only (`citation-id` carries the `venue:` prefix per `query-strategies.md` §Venue identifier convention). From source-recency-probe v2.0 this row is emitted only by the path-A arXiv-category listing when that listing fails at the HTTP level, and is then always `status: unverifiable` with the HTTP status or error text in `evidence-quote`. It is never used for an unresolved paper.
- `source-superseded-by-newer` — `citation-id` holds the **existing** source's id from `sources[]`; `cited-value` the existing title; `actual-value` the superseding candidate's `title · publication_date · arXiv/DOI id`; `evidence-quote` the verbatim candidate title. Always `status: fail`.
- `source-unresolved` — an entry in `sources[]` that the probe could not resolve to a citation-graph node (no arXiv id, no DOI, no exact-title match) or could not finish walking (wall-time or pagination cap). `citation-id` holds the artifact's own source id (e.g. `S3`); `cited-value` holds the cited title or URL; `actual-value` holds `unresolvable`, `wall-time cap`, or `pagination cap`; `evidence-quote` holds the lookup that failed or the cap name. Always `status: unverifiable` — the source was neither probed nor cleared. Registered at frontmatter v2.0.
- `probed-no-candidates` — a source the probe DID resolve and walk that yielded no candidate surviving §Ranking and caps. One row per such source: `citation-id` holds the artifact's own source id (e.g. `S3`); `cited-value` holds the cited title; `actual-value` holds the literal `0 candidates in window`; `evidence-quote` holds the cited-by query URL that was walked. Always `status: pass` — the source was probed and cleared, which is a different fact from `source-unresolved` (never probed) and from `nothing-to-probe` (no evidence base at all). Registered at frontmatter v2.0.
- `nothing-to-probe` — the artifact declares no `sources[]` (absent or empty), so the probe has no evidence base to walk. Exactly one row per invocation: `citation-id` holds the literal `sources:<none>`; `cited-value`, `actual-value`, `evidence-quote` are empty strings. Always `status: unverifiable`. Registered at frontmatter v2.0.
- `topic-tag-uncatalogued` — **deprecated at frontmatter v2.0; never emitted by source-recency-probe ≥ v2.0.** Kept registered so envelopes produced by earlier versions still parse. Its former obligation in §Status semantics is superseded by the `nothing-to-probe` / `source-unresolved` obligation below.

### survey-refresh

- `detected-url-removed` — `citation-id` holds the `[Sxx]` source identifier from the survey's `sources[]`; `cited-value` holds the string `"live"`; `actual-value` holds the HTTP status code (e.g., `"404"`); `evidence-quote` holds the first 200 chars of the response body (empty on network error).
- `detected-url-added` — one advisory row per invocation from survey-refresh as of this shared lock's frontmatter v2.0: `citation-id` holds `advisory:source-recency-probe`; `cited-value` empty; `actual-value` holds the advisory text; `evidence-quote` holds the verbatim instruction to run `/source-recency-probe`. (Pre-v2.0 envelopes may carry `venue:`-prefixed ids from the retired catalog inference.)
- `detected-citation-stale` — `citation-id` holds the `[Sxx]` source identifier; `cited-value` holds the SHA256 hex of the normalized prior-session cached body; `actual-value` holds the SHA256 hex of the normalized freshly-fetched body; `evidence-quote` holds the first 200 chars of the freshly-fetched body showing the divergence.
- `detected-last-refreshed-bumped` — `citation-id` holds the literal string `last-refreshed`; `cited-value` holds the frontmatter `last-refreshed:` value; `actual-value` holds the most-recent `## Refresh log` table row's date; `evidence-quote` holds the most-recent refresh-log row's text.

### invocation-discipline-lint

`/invocation-discipline-lint` emits one row per checked OUT-bias / OUT-bloat rule declared in the spec's §"Invocation discipline" section. The per-violation tuple `(violation_class, in_contract_rule_violated, evidence_in_call, suggested_correction)` maps onto the locked row shape as follows. `check-name` here is spec-derived (the verbatim declared bullet), not a fixed enum; the stable enum lives at the `citation-id` level (`bias.*` / `bloat.*`).

- `citation-id` holds the `violation_class` tag from the fixed namespace `bias.*` / `bloat.*` (e.g., `bias.caller-verdict`, `bias.pre-filtered-category`, `bias.caller-intent`, `bloat.attached-spec-body`, `bloat.full-call-signature`).
- `check-name` holds the `in_contract_rule_violated` — the verbatim OUT-bias / OUT-bloat bullet text the spec declared.
- `status` is `fail` for a surfaced violation, `pass` for a clean-on-this-rule row, `unverifiable` when the spec's §"Invocation discipline" section is unparseable / absent.
- `cited-value` holds the spec's declared rule string (the contract the invocation should have honored).
- `actual-value` holds the `evidence_in_call` — the offending substring or structural marker observed in the call signature.
- `evidence-quote` holds the `suggested_correction` — the spec-grounded fix proposed for the caller.

## Status semantics

The fail vs. unverifiable distinction is load-bearing and MUST NOT collapse:

- **`pass`** — check ran and the cited value matches actual. `pass` is also the carrier for *"probed, found nothing"*: `/source-recency-probe`'s `probed-no-candidates` row is the registered name for a source that WAS resolved and walked and yielded no candidate. A skill with nothing to report about a probed input emits that row, never an absent row.
- **`fail`** — check ran and the cited value contradicts actual. Author MUST resolve before the artifact lands.
- **`unverifiable`** — check could not run because the source format / availability prevents mechanical verification (paywall, PDF without HTML mirror, venue API failure). Escalation surface — not a pass; not a fail.

For any check whose verdict depends on *fetch reachability* (e.g. `url-liveness`, and the venue/source fetches behind `title-match`, `author-match`, `year-match`, the framing-drift probes, and the recency probes), `unverifiable` is legitimate ONLY after the cache contract's §Liveness fetch fallback ladder has been exhausted (default fetch → browser-`User-Agent` retry → alternate authoritative host / structured API). A first-attempt HTTP `403` / `429` / `503` / empty-or-client-render-only body is a ladder TRIGGER, not a verdict — emitting `unverifiable` on it alone misclassifies a live, bot-gated or throttled source as unreachable. See `cache-contract.md` §Liveness fetch fallback.

## Verdict computation

Aggregate verdict over `rows`:

- `pass` iff every row is `pass`.
- `fail` iff at least one row is `fail`. Dominates `unverifiable`.
- `unverifiable` iff no `fail` row exists AND at least one row is `unverifiable`.

Empty `rows` MUST emit `verdict: "pass"` only when the skill ran successfully against an artifact with zero citations. Empty `rows` from a skill that aborted (e.g., invocation-discipline refusal) MUST instead surface as a refusal record outside this schema.

A skill that ran but had **nothing to check** is neither of those cases, and MUST NOT emit an empty-`rows` `pass`. Concretely, for `/source-recency-probe`, every entry in `sources[]` SHALL yield at least one row:

- an artifact with no `sources[]` at all SHALL emit exactly one `nothing-to-probe` row at `unverifiable`;
- a source that could not be resolved to a citation-graph node SHALL emit one `source-unresolved` row at `unverifiable`;
- a source that WAS resolved and walked but yielded no candidate surviving the caps SHALL emit one `probed-no-candidates` row at `pass`.

So `rows` is never empty when `sources[]` is non-empty, and a clean probe surfaces as an all-`pass` envelope of `probed-no-candidates` rows rather than as an empty array. The distinction a consumer needs is between *"probed, found nothing"* (`probed-no-candidates`, `pass`) and *"never probed"* (`source-unresolved` / `nothing-to-probe`, `unverifiable`); an empty-`rows` `pass` collapses them. (Frontmatter v1.4 keyed this obligation to frontmatter `tags:` via `topic-tag-uncatalogued`; v2.0 re-keys it to `sources[]`, because the probe no longer reads tags.)

## Refusal records

Refusal records (emitted when a skill refuses an invocation that violates its §Invocation discipline) have their own v1.0 lock at [`refusal-record.md`](refusal-record.md). They share the WIRE major-version namespace with this file — a wire-major break here coordinates with a wire-major break there — but minor bumps, and the two lock documents' own frontmatter versions, move independently. Consumers distinguish the two message kinds by top-level shape: presence of `rows` indicates an envelope; presence of `refusal` indicates a refusal record. Both-present or neither-present is malformed.

## Versioning

- Major — a breaking change to envelope / row required fields. That is a **wire** major: it bumps the envelope `version` field, and consumers fail closed on an unknown wire major.
- Major also — a change that RE-KEYS or REMOVES an existing obligation, or DEPRECATES a registered check-name, even when envelope / row required fields and the wire `version` are unchanged. That is a **frontmatter** major on this lock document only: consumers need no code change, but they MUST update the pointer text that names this lock's version.
- Frontmatter v2.0 (current) registers `source-unresolved`, `nothing-to-probe` and `probed-no-candidates` for `/source-recency-probe`, deprecates `topic-tag-uncatalogued` (kept registered, never emitted), and **re-keys the §Status semantics "nothing to check" obligation from frontmatter `tags:` to `sources[]`**. The re-keying and the deprecation are what make this a major frontmatter bump under the second rule above. `probed-no-candidates` and the second §Versioning rule bullet itself were added later within v2.0 — an additive check-name registration and a codification of the rule the bump already relied on, neither of which re-keys or removes anything, so both land inside v2.0 rather than forcing a 3.0. Row shape, status vocabulary, and the wire `version` field (`"1.0"`) are unchanged. Coordinated in one PR across all six consumers.
- Minor — additive change to optional fields, additive check-name registrations, and clarifications to §Status semantics that tighten (never loosen) when a status is legitimate. Consumers ignore unknown optional fields and inherit clarified semantics gracefully.
- v1.0 is the locked Stage 1 contract; downstream Stage 2+ skills depend on this exact shape. The wire `version` field consumers emit stays `"1.0"` (frontmatter `version` is lock-document metadata). Bumping the wire major requires a coordinated PR across every consumer.
- Frontmatter v1.4 registers the `topic-tag-uncatalogued` check-name for `/source-recency-probe` (scoped to frontmatter-declared `tags:` only, including the `tag:<none>` sentinel for an artifact declaring no tags) and adds the §Status semantics paragraph forbidding an empty-`rows` `pass` when a skill ran with nothing to check. Additive check-name registration plus a status clarification that tightens; no row-shape change; wire `version` unchanged.
- Frontmatter v1.3 clarifies §Status semantics: fetch-reachability `unverifiable` is legitimate only after the `cache-contract.md` §Liveness fetch fallback ladder is exhausted. Additive clarification — no row-shape or check-name change; wire `version` unchanged.
