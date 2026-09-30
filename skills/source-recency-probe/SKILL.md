---
name: source-recency-probe
description: Probe a draft decision artifact (survey, RFC, ADR, design doc) for evidence the author should have cited but missed because of LLM training-cutoff bias. Derives the search space from the artifact's own `sources[]` — for each cited paper, the papers citing it since the cutoff date (OpenAlex citation graph, complemented for arXiv sources by an always-on arXiv-category listing because OpenAlex indexes arXiv-only citers thinly), ranked by how many of the artifact's sources they cite — and surfaces (a) new candidate papers, (b) cited sources superseded by newer same-author work, (c) sources the graph cannot resolve. Never reads `tags:` or headings. Counters failure mode #1 recency cutoff. Trigger with /source-recency-probe --artifact <path> --authored-against MODEL,DATE, "probe <artifact> for missing recent work", or "check recency on <artifact>". Runs BEFORE /citation-detail-verify and /load-bearing-fullread so the source list is final by the time those skills fire.
user-invocable: true
allowed-tools: Read, Grep, Glob, WebFetch, Bash, Write
---

# /source-recency-probe — recency-gap detection for decision artifacts

LLM-driven surveys inherit the LLM's training-data distribution; that distribution has a hard cutoff and an exponential under-representation of work near the cutoff. The result is a survey that cites textbook references reliably and silently omits post-cutoff work the LLM never saw. Per the brief at `~/dx-arch-meta/repos/research-docs/content/notes/source-recency-probe-skill-brief.md`, the skill counters failure mode **#1 recency cutoff** as a named primitive; today the discipline is ad-hoc ("the author *might* probe arXiv, or *might* not"). The skill replaces honor-system with a property the pipeline can rely on: every artifact's cited sources are mechanically walked through the citation graph (papers citing them since the cutoff) before deeper framing probes fire.

## When to invoke

- Author has a draft survey / RFC / ADR / design doc whose frontmatter declares `sources[]` with resolvable identifiers (arXiv ids, DOIs, or exact titles).
- Before `/citation-detail-verify` — adding a candidate at full-read time wastes the full-read pass; recency-probe should produce the final source list, then citation-detail-verify mechanically filters, then load-bearing-fullread verifies framing.
- At every survey refresh — the `last-refreshed:` bump is the refresh-cadence trigger (see §Invoke at refresh cadence).

**Don't invoke when:**
- Source list is still in flux. Probe-then-add forces a re-probe on every change.
- Caller has a named candidate in mind ("I think there's a paper from late 2025"). Caller-supplied candidate collapses the probe into a confirmation-search. See §Invocation discipline.
- Artifact has no `sources[]` — the skill still runs and emits exactly one `nothing-to-probe` row (`citation-id: sources:<none>`) at `unverifiable` rather than silently passing; there is no evidence base to walk. Artifacts that cite by reference to other corpus documents fall here until a transitive-resolution step exists (separate brief).

## Input

```
/source-recency-probe --artifact <path> --authored-against MODEL,DATE
```

Two required arguments. No optional flags. The skill is a fixed-behavior primitive — sibling skills depend on its universal-pass property, and flags would make that property invocation-dependent. Per Decision 2 of `openspec/changes/archive/2026-05-19-source-recency-probe-skill/design.md`.

- `--artifact <absolute-or-repo-relative-path>` — artifact file. Skill reads frontmatter `sources[]` only (per §Invocation discipline §Bloat surfaces; never `tags:`, never headings, never the body).
- Environment: no API key. The citation-graph provider is OpenAlex; every request carries `mailto=<address>` to enter the polite pool, spaced 1 s serially per `references/query-strategies.md` §Rate-limit safety rule 6. Quota is read from the live `x-ratelimit-*` response headers rather than assumed, and any truncation is reported honestly via `source-unresolved` rows.
- `--authored-against MODEL,DATE` — comma-separated `(model, cutoff-date)`. `MODEL` is an opaque label (e.g., `claude-opus-4-7`); `DATE` is ISO-8601 (`2025-09-01`). Used as the lower bound on the probe window `[cutoff_date, today]`. Per Decision 5, the alternative `(probe-last-N-months)` form is not supported.

## Workflow

1. **Resolve artifact** — Read the path. Parse frontmatter YAML; collect `sources[]` entries (id, title, url, authors when present). `tags:` and body headings are not read. If `sources[]` is absent or empty → emit exactly one `nothing-to-probe` row per `references/query-strategies.md` §Row mappings and go to step 7.
2. **Resolve each source** — per `references/query-strategies.md` §Source resolution: derive the OpenAlex lookup key in the order listed there (arXiv id → the DataCite DOI form `10.48550/arXiv.<id>`; `DOI:<doi>`; else `filter=title.search:` exact-title match), classify each source `resolved` / `graph-unknown` / `unresolvable`. Unresolvable → one `source-unresolved` row at `unverifiable`. Every arXiv source — `resolved` or `graph-unknown` — also goes to step 5. **Pre-fetch precondition:** if neither `$CLAUDE_SESSION_ID` nor `$CLAUDE_CODE_SESSION_ID` is set, the skill SHALL refuse to write cache entries and emit a refusal-record marker (hard refuse, not silent fallback). All fetches go through `../citation-detail-verify/references/cache-contract.md` §Read protocol and honour `references/query-strategies.md` §Rate-limit safety rules 6–7 (serial; 1 s spacing with `mailto=`; `Retry-After` backoff then `source-unresolved` on a second 429/503; 15 min wall-time cap).
3. **Collect citing papers** — for each resolved source, walk `works?filter=cites:<W-id>,from_publication_date:<DATE>` with `sort=publication_date:desc&per-page=200&cursor=*` per §Citation collection. The window is applied server-side, so there is no client-side early-stop or ordering guard: follow `meta.next_cursor` until it is null or the 10-page (2000-citer) cap is hit (cap → `source-unresolved`, `actual-value: pagination cap`, alongside the candidates already walked).
4. **Rank and cap** — per §Ranking and caps: collapse `sources[]` entries sharing a W-id into one canonical source, merge candidates by W-id, drop candidates already in `sources[]`, sort by (sources-cited desc, `cited_by_count` desc, `publication_date` desc, author-overlap first, W-id ascending — a total order, so the capped set is deterministic); top 10 overall if any candidate cites ≥ 2 canonical sources, else per-source cap mode (top 3 per source, deduplicated). Author overlap with a cited source → one `source-superseded-by-newer` row per (candidate, overlapping source) pair and no `new-candidate-found` row, one cap slot regardless; a candidate whose normalised title equals the anchored source's is a resubmission and is dropped, not superseded. Otherwise `new-candidate-found`.
5. **Path A — always-on for every arXiv source** — per §Probe-strategy schema `probe-arxiv-category`: list `arxiv:<primary_category>` since `DATE`, pinned title-token filter against the *cited* title, cap 3 per source. Path-A candidates join the step-4 pool with sort key 1 fixed at 0, in **both** modes. A listing that fails at the HTTP level → one `venue-absent-from-sources` row with the `venue:` id at `unverifiable`; when path A was that source's only probe (a `graph-unknown` source), the same failure ALSO emits one `source-unresolved` row for the source id with `actual-value: unresolvable`, so the source is never silently dropped.
6. **Surface findings** — one row per candidate, per unresolved source, and per resolved-but-empty source, conforming to `../citation-detail-verify/references/output-schema.md` §Row shape, field semantics per `references/query-strategies.md` §Row mappings. A resolved source that yielded no candidate surviving the caps emits exactly one `probed-no-candidates` row at `pass`. The six `check-name` values this skill emits (`new-candidate-found`, `source-superseded-by-newer`, `venue-absent-from-sources`, `source-unresolved`, `nothing-to-probe`, `probed-no-candidates`) are registered in the shared lock at frontmatter v2.0; `topic-tag-uncatalogued` is deprecated and never emitted. This skill SHALL NOT extend or shadow the vocabulary. Each `new-candidate-found` and `source-superseded-by-newer` row is also a proposed candidate: record it via `candidates.py append --stage recency-probe-candidate --source-in-context false` with `--url` = the row's `citation-id`, `--title` = the candidate title, an empty sentence, and `--published-year` / `--cited-by-count` from the OpenAlex work (`--reference-class arxiv-preprint` for an arXiv id), per `../citation-detail-verify/references/candidates-contract.md` v1.0. `--repo` is the artifact's checkout; the sidecar sits beside the artifact.
7. **Compute aggregate verdict** — per `../citation-detail-verify/references/output-schema.md` §Verdict computation: `fail` iff ≥ 1 `new-candidate-found` or `source-superseded-by-newer`; else `unverifiable` iff ≥ 1 `source-unresolved`, `venue-absent-from-sources`, or `nothing-to-probe`; else `pass` — the clean-probe case, an envelope of all-`pass` `probed-no-candidates` rows. Every entry in `sources[]` yields at least one row, so `rows` is never empty when `sources[]` is non-empty; a zero-`sources[]` artifact emits exactly one `nothing-to-probe` row. This skill therefore never emits an empty-`rows` `pass`.
8. **Emit envelope** — JSON per §Envelope, wire `version: "1.0"`, with `cache: {"hits": N, "misses": N, "writes": N}` from the fetch telemetry.

## Invoke at refresh cadence

The survey `last-refreshed:` frontmatter field is the canonical refresh trigger. When an author bumps `last-refreshed:` on a survey, the bump SHOULD be preceded by a recency probe — otherwise the refresh is a date change without source-list discovery. Per Decision 7, this refresh-cadence guidance lives in the SKILL.md (not a sibling runbook file).

Canonical copy-paste invocation line for the survey's refresh footer:

```
<!-- Last refresh probed via /source-recency-probe --artifact <this-survey-path> --authored-against <model>,<cutoff-date> -->
```

The comment is human-and-agent-readable; agents reading the survey for follow-on tasks can verify a probe ran when the refresh happened.

## Success criteria (DSL primitives quoted verbatim from brief)

The brief at `~/exocortex-data/backlog/20260905T053532.312341Z-source-recency-probe-derive-venues-from-sources.md` declares the v2 property set; the original brief's still-applicable rows are retained below it. `origin/main:<path>` in the brief resolves to the deployed `~/.claude/skills/<path>` here.

Three further rows in the brief are `absent` checks against this file and `survey-refresh/SKILL.md`; they are deliberately not reproduced here, because quoting a negated literal inside the file it targets would plant the very token the check forbids. The brief remains the authoritative list (19 rows: the 16 `detect` rows below plus those 3).

- `detect "tags-not-consulted" in ~/.claude/skills/source-recency-probe/test-corpus/source-derived-venues.md count >=1`
- `detect "openalex" in ~/.claude/skills/source-recency-probe/test-corpus/source-derived-venues.md count >=1`
- `detect "cites-2-sources-outranks" in ~/.claude/skills/source-recency-probe/test-corpus/intersection-ranking.md count >=1`
- `detect "top-3-per-source" in ~/.claude/skills/source-recency-probe/test-corpus/fallback-per-source.md count >=1`
- `detect "source-superseded-by-newer" in ~/.claude/skills/source-recency-probe/test-corpus/superseded-by-author.md count >=1`
- `detect "nothing-to-probe" in ~/.claude/skills/source-recency-probe/test-corpus/no-sources-declared.md count >=1`
- `detect "sources:<none>" in ~/.claude/skills/source-recency-probe/test-corpus/no-sources-declared.md count >=1`
- `detect "source-unresolved" in ~/.claude/skills/source-recency-probe/test-corpus/unresolved-source.md count >=1`
- `detect "source-unresolved" in ~/.claude/skills/citation-detail-verify/references/output-schema.md count >=1`
- `detect "nothing-to-probe" in ~/.claude/skills/citation-detail-verify/references/output-schema.md count >=1`
- `detect "probed-no-candidates" in ~/.claude/skills/source-recency-probe/test-corpus/probed-no-candidates.md count >=1`
- `detect "probed-no-candidates" in ~/.claude/skills/citation-detail-verify/references/output-schema.md count >=1`
- `detect "deprecated" in ~/.claude/skills/source-recency-probe/references/query-strategies.md count >=1`
- `detect "api.openalex.org" in ~/.claude/skills/source-recency-probe/references/query-strategies.md count >=1`
- `detect "filter=cites:" in ~/.claude/skills/source-recency-probe/SKILL.md count >=1`
- `detect "detected-url-added" in ~/.claude/skills/survey-refresh/SKILL.md count >=1`

Retained from the v1 brief:

- `detect new-candidate-found in ~/.claude/skills/source-recency-probe/test-corpus/new-candidate.md count >=1`
- `detect venue-absent-from-sources in ~/.claude/skills/source-recency-probe/test-corpus/venue-gap.md count >=1`
- `detect source-superseded-by-newer in ~/.claude/skills/source-recency-probe/test-corpus/superseded.md count >=1`
- `detect probe-arxiv-category in ~/.claude/skills/source-recency-probe/test-corpus/arxiv-probe.md count >=1`
- `detect probe-named-conference in ~/.claude/skills/source-recency-probe/test-corpus/conference-probe.md count >=1`
- `detect probe-research-blog in ~/.claude/skills/source-recency-probe/test-corpus/blog-probe.md count >=1`
- `detect emitted-verdict-pass in ~/.claude/skills/source-recency-probe/test-corpus/pass-shape.md count >=1`
- `detect emitted-verdict-fail in ~/.claude/skills/source-recency-probe/test-corpus/fail-shape.md count >=1`
- `detect emitted-verdict-unverifiable in ~/.claude/skills/source-recency-probe/test-corpus/unverifiable-shape.md count >=1`
- `detect output-row-with-all-required-fields in ~/.claude/skills/source-recency-probe/test-corpus/pass-shape.md count >=1`
- `absent output-row-missing-required-field in ~/.claude/skills/source-recency-probe/test-corpus/`
- `detect cache-hit-on-shared-fetch in ~/.claude/skills/source-recency-probe/test-corpus/shared-cache.md count >=1`
- `detect emitted-refusal-record in ~/.claude/skills/source-recency-probe/test-corpus/bad-invocations.md count >=5`
- `detect registered-query-strategy in ~/.claude/skills/source-recency-probe/references/query-strategies.md count >=3`

Added by the candidates-capture change (back-propagate to the brief on its next edit):

- `detect recorded-candidate-row in ~/.claude/skills/source-recency-probe/test-corpus/candidate-capture.md count >=1`

Seven of the retained fixtures encoded v1 catalog-era semantics and were refreshed to v2 in this wave, so the rows above keep holding for the right reason: `pass-shape.md` (a clean probe is now an all-`pass` envelope of `probed-no-candidates` rows over declared sources, not an empty `rows` array), `unverifiable-shape.md` (a second consecutive 429 on the citation-graph provider → `source-unresolved`, not a catalog venue failure), `venue-gap.md` (a path-A arXiv-category listing that fails at the HTTP level → both a `venue-absent-from-sources` venue row and, for a `graph-unknown` source, a `source-unresolved` source row), `arxiv-probe.md` (path A is now the always-on second signal for a resolved arXiv source's own cited-title token filter, yielding an all-`pass` `probed-no-candidates` envelope, not an empty `rows` array against a topic-tag lookup), `conference-probe.md` and `blog-probe.md` (each now documents its strategy as registered but undispatched at v2.0, with the resolved source's evidence carried entirely by the citation walk plus path A, not a topic-tag-derived venue dispatch), and `fail-shape.md` (the `new-candidate-found` surfaces from the citation walk or the always-on path-A listing pinned to the cited source's own title, not a topic-vector match against `tags:`).

Dropped at v2.0: exactly the two `topic-tag-uncatalogued` rows (their fixtures are retired). The `probe-named-conference` / `probe-research-blog` rows are **kept** — their fixtures still ship and the templates stay registered; the spec (§8) authorises deleting only the two rows above.

## Load-when table

| Step | Reference | Why load |
|------|-----------|----------|
| 1–3, 5–8 | [`../citation-detail-verify/references/output-schema.md`](../citation-detail-verify/references/output-schema.md) | Envelope + row shape, registered `check-name` vocabulary, status semantics, verdict computation. Stage 1 lock, frontmatter v2.0 (wire `"1.0"`); REUSED unchanged via relative path. |
| 2, 3, 5 (per fetch) | [`../citation-detail-verify/references/cache-contract.md`](../citation-detail-verify/references/cache-contract.md) | Cache key derivation, on-disk path, atomicity, invalidation, read protocol. Stage 1 lock, frontmatter v1.4; cross-skill rendezvous at `~/.claude/skills/citation-detail-verify/cache/<key>/`. |
| Invocation refusal | [`../citation-detail-verify/references/refusal-record.md`](../citation-detail-verify/references/refusal-record.md) | Refusal-record shape (`refusal: {category, rule, evidence}`). Stage 1 lock, frontmatter v1.4; REUSED unchanged. |
| 6 (per candidate row) | [`../citation-detail-verify/references/candidates-contract.md`](../citation-detail-verify/references/candidates-contract.md) | `candidates.jsonl` record shape, `source_meta` proxy fields, `append` refusals. Shared v1.0 lock; REUSED via relative path; helper at `~/.claude/skills/citation-detail-verify/scripts/candidates.py`. |
| 1–5 | [`references/query-strategies.md`](references/query-strategies.md) | §Source resolution, §Citation collection, §Ranking and caps, §Row mappings, §Rate-limit safety; always-on path-A arXiv template plus two registered-undispatched templates. Skill-scoped v2.0 lock. |

References load when the workflow needs them, not at skill startup. Per progressive disclosure, the SKILL.md does NOT restate row fields, cache layout, refusal shape, or probe templates — each lives in its own reference file.

## Invocation discipline

Dominant concern per brief: **bias**. The probe must derive its candidate list from the artifact's own `sources[]` and the citation graph independently; caller hints collapse the probe into a confirmation-search. **Author-declared `tags:` are not an input; the artifact's `sources[]` is the only topic signal** — this is the blind-input alignment with every sibling skill (RFC-0022 Commitment 3). Bloat secondary — the skill reads `sources[]` only. Forbidden surfaces — each bullet is the verbatim rule the skill SHALL paste into `refusal.rule` when an invocation triggers refusal per `../citation-detail-verify/references/refusal-record.md`:

- Bias — Named candidate papers caller suspects are missing.
- Bias — Venue, category, or tag hints of any kind.
- Bias — Caller's framing of why the survey is incomplete.
- Bloat — Full survey body.
- Bloat — Full text of currently-cited sources.

Rule rationale (NOT part of the verbatim rule; reference-only context for reviewers): caller-provided candidates skip the discovery step that's the skill's whole purpose (bias 1); the search space is a function of `sources[]` alone (bias 2); free-text framing has no legitimate input slot (bias 3); skill reads frontmatter `sources[]` only — neither headings nor body; body is the load-bearing-fullread surface (bloat 1); recency probes new candidates — cited set is metadata-only input (bloat 2).

Good brief: `/source-recency-probe --artifact content/survey/llm-review-landscape.md --authored-against claude-opus-4-7,2025-09-01`. Pointer + cutoff only; skill derives the search space from `sources[]` alone.

Bad brief: `/source-recency-probe "Check if we missed recent work on Star Chamber-style judging — I think there's more from late 2025."` Names candidate + caller framing — refuse with refusal record.

## Out of scope

- Auto-applying recency findings to the survey. Skill surfaces `(citation-id, candidate)`; author edits the artifact. Auto-fix would silently rewrite the author's source list without audit trail.
- Generative discovery in unknown venues. Skill walks the citation graph of the cited sources plus the always-on arXiv-category path-A listing for arXiv sources; broad-web discovery is a different primitive. One-hop transitive resolution for artifacts that cite by reference (no `sources[]`) is a separate additive brief.
- Assessing whether a candidate is readable. Candidate full text is never fetched, so accessibility (paywall, PDF-only, login wall) is not assessed and never appears in a row; the skill reasons over citation-graph and listing metadata only.
- Replacing the survey's own `last-refreshed:` discipline. Skill produces input *to* a refresh decision; the human author still owns the refresh commit.

## Cross-skill compatibility

This skill is the FIRST consumer of the Stage 1 locks via relative-path REUSE (not file copy). The three locks live under `skills/citation-detail-verify/references/`; this skill cites them via `../citation-detail-verify/references/<file>.md`. The relative-path REUSE pattern resolves under user-scope APM install (`apm install ... -g`), which is the dominant deployment per `cache-contract.md` §Deployment assumption.

Bumping the **wire** major (`"1.0"`) requires a coordinated code change across every consumer of the shared lock; the authoritative roster is that lock's own frontmatter `consumers:` list, not a count restated here. Bumping a lock document's **frontmatter** major requires no code change, but every consumer's pointer text naming that version moves in the same PR.

## Local-extractor note (dx-llm-sidecar overlay)

When `llm` is on PATH, bounded extraction sub-steps in this skill — pulling
title/author/year/quote-presence from an already-fetched source body,
clustering result rows, first-pass text matching — SHOULD run via the FREE
local sidecar (`llm --json <schema> "<extraction>" < <fetched-body>`) instead
of burning paid context on the raw text. The extraction output feeds this
skill's own mechanical checks unchanged; verdict computation, status
semantics, and row schemas are NOT delegated — the local model is an
extractor behind the contract, never a verdict author. Skip silently when
`llm` is absent.
