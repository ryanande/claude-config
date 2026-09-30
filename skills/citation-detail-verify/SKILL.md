---
name: citation-detail-verify
description: Mechanically verify every citation in a decision artifact (survey, RFC, ADR, design doc) for surface-level integrity — URL liveness, title match, author / year drift, verbatim-quote presence, anchor resolution, frontmatter↔body coherence. Cheap pre-filter; runs after /source-recency-probe, before /load-bearing-fullread and /adversarial-frame. Trigger with /citation-detail-verify --artifact <path>, "verify the citations in <artifact>", or "check citation integrity on <draft>". Mechanical only — does NOT probe framing (that's /load-bearing-fullread) or generate alternatives (/adversarial-frame).
user-invocable: true
allowed-tools: Read, Grep, Glob, WebFetch, Bash, Write
---

> **Standalone divergence (this config):** the citation-ID pattern is generalized
> to also recognize `(S<n>)` — the citation style `survey-author`'s own scaffold
> produces in this environment — alongside Wyatt's original `[Axx]`/`[Bxx]`
> research-docs convention. Both patterns remain live; this is additive, not a
> replacement. See `docs/superpowers/specs/2026-07-14-research-skill-suite-port-design.md`
> for the rest of this port's divergences and
> `docs/superpowers/specs/2026-07-13-retroactive-verify-chain-application-design.md`
> (in `research_docs`) for why this one was added.

# /citation-detail-verify — citation surface-level integrity

Cheap mechanical filter on a draft decision artifact's citation set. Per the research-pipeline-skill-brief at `~/dx-arch-meta/repos/research-docs/content/notes/citation-detail-verify-skill-brief.md`, the skill counters failure mode **#5 citation hallucination** as a named primitive; today the discipline is honor-system `WebFetch` per citation. The skill replaces honor-system with a property the pipeline can rely on: every citation passes the mechanical bar before expensive framing probes spend WebFetch cost on it.

## When to invoke

- Author has a draft survey / RFC / ADR / design doc whose `sources[]` frontmatter list and inline `[Axx]` / `[Bxx]` / `(S<n>)` body references are stable.
- `/source-recency-probe` has finalized the source list (no more additions pending).
- Before `/load-bearing-fullread` and `/adversarial-frame` run — those skills assume citation metadata is verified.
- At every survey refresh (the `last-refreshed:` bump is a re-verify trigger).

**Don't invoke when:**
- Source list is still in flux. Verify-then-add forces a re-verify on every change.
- Caller pre-filtered the citation set ("only check these 3") — partial-pass leaves unchecked citations indistinguishable from passed ones. See §Invocation discipline.
- Artifact has zero citations. Skill emits `verdict: "pass"` with an empty `rows` array; nothing useful happens.

## Input

```
/citation-detail-verify --artifact <path>
```

One required argument: `--artifact <absolute-or-repo-relative-path>`. The skill auto-extracts the citation set from BOTH surfaces: frontmatter `sources[]` AND inline body `[Axx]` / `[Bxx]` / `(S<n>)` refs. Disagreement between the two is itself a finding.

No optional flags. The skill is a fixed-behavior primitive — sibling skills depend on its universal-pass property, and flags would make that property invocation-dependent. Per-check semantics are pinned:

- Citation-ID pattern: `\[[AB]\d+\]` (research-docs corpus convention).
- Title match: strict equality after normalizing whitespace + punctuation.
- Author match: cited and fetched author SETS must be equal (order ignored; accommodates arXiv v1-vs-final reorderings).
- Report mode: every citation is checked; one row per `(citation, check)` is always emitted.

## Workflow

1. **Resolve artifact** — Read the path. Parse frontmatter via YAML; collect `sources[]` IDs and URLs. Grep the body for the citation-ID pattern; collect inline references with ±2 lines of context (anchor for the verbatim-quote check).
2. **Surface frontmatter↔body mismatch** — Symmetric set difference between frontmatter `sources[]` IDs and inline body IDs. Each mismatch emits one row with `check-name: "frontmatter-body-citation-mismatch"` per `references/output-schema.md`.
3. **Per citation, run six mechanical checks** in this order (each emits one row regardless of pass / fail / unverifiable):
   1. `url-liveness` — fetch the URL via the cache contract's miss-path, which applies the `references/cache-contract.md` §Liveness fetch fallback ladder (default fetch → browser-`User-Agent` retry on `403`/`429`/`503`/empty-body → alternate authoritative host / structured API). After the ladder: 2xx → pass; a 4xx/5xx that persists across every ladder route → fail; network / DNS failure with no route reachable → unverifiable. A first-attempt `403`/`429`/empty-body is a ladder TRIGGER, never a standalone verdict — emitting `fail` or `unverifiable` on it before the ladder is exhausted misclassifies a live, bot-gated or throttled source (see `references/output-schema.md` §Status semantics). Cache hit / write per `references/cache-contract.md`.
   2. `title-match` — fetched `<title>` (HTML) or arXiv metadata title vs cited title; strict equality after normalizing whitespace + punctuation (no fuzzy mode).
   3. `author-match` — fetched author SET vs cited author SET; order ignored.
   4. `year-match` — cited year vs fetched arXiv `v1` posted-date year (or DOI metadata year for non-arXiv sources); exact equality. No v1-vs-final hedging — v1 year is canonical; surveys that need final-version year cite it explicitly.
   5. `verbatim-quote-match` — every numeric value or quoted phrase in the cited context (citation-ID ±2 lines) tested against the source text loaded from cache per `references/cache-contract.md` v1.4 §Read protocol text-read rule, branched by which file the rule selects (pre-warmed by `/load-bearing-fullread` if it ran first; cold fetch otherwise):
      - `body.txt` read (PDF source) — `norm-v1` token-boundary match on both sides via `scripts/pdf_extract.py quote-present`. Presence → pass and record its printed raw offset for check 6; absence → fail; a quote whose ends match but whose middle is interrupted → unverifiable with `check-detail.reason: "quote-spans-page-break"`.
      - `body` read (HTML / plain-text source) — literal substring match, as before v1.4.
      - Source format prevents either branch (PDF body with no `body.txt`) → unverifiable with `check-detail.route: "pdf-extract"` and `check-detail.reason` from `extracted_text.status`.
   6. `anchor-resolution` — every `§N.M`, `Table N`, `Figure N`, `page N` reference in the cited context resolves in source. arXiv HTML mirror enables all four forms. On an extracted PDF body (`body.txt`): `page N` resolves from the raw offset check 5's `quote-present` printed on its hit, via `pdf_extract.py page-of` — it is never re-derived from the key string. If the quote itself is absent (check 5 `fail` or `unverifiable`), `page N` is unverifiable too — there is no offset to resolve from. `Table N`, `Figure N` and sub-section `§N.M` resolve by `norm-v1` substring; top-level `§N` → unverifiable with `check-detail.reason: "unsectioned-body"`. PDF body with no `body.txt` → unverifiable with `check-detail.reason` from `extracted_text.status`.
4. **Distinguish `fail` from `unverifiable`** — `fail` = cited value contradicts source; author MUST fix. `unverifiable` = source format prevents the mechanical check; escalation surface, not a free pass. The two MUST NOT collapse — `references/output-schema.md` §Status semantics is load-bearing.
5. **Compute aggregate verdict** mechanically from rows per `references/output-schema.md` §Verdict computation: `fail` dominates `unverifiable` dominates `pass`. Then, for every citation whose own six rows include a `fail`, disposition its proposal-time record when one exists: `python3 ~/.claude/skills/citation-detail-verify/scripts/candidates.py append-disposition --repo <root> --artifact <path> --record-id <id> --disposition dropped-at-citation-detail-verify --stage citation-detail-verify --label <Minor or Major>` — `Minor` for one failing detail check, `Major` for a `url-liveness` fail or ≥ 2. Resolve `<id>` via `candidates.py list --repo <root> --artifact <path>`; no matching `proposed` record → write nothing. Per `references/candidates-contract.md` v1.0.
6. **Emit envelope** — JSON object per `references/output-schema.md` §Envelope, with `cache: {"hits": N, "misses": N, "writes": N}` populated from telemetry collected during the WebFetch calls.

## Success criteria (DSL primitives quoted verbatim from brief)

The brief at `~/dx-arch-meta/repos/research-docs/content/notes/citation-detail-verify-skill-brief.md` declares the property set the skill MUST exhibit. Quoting the relevant DSL rows verbatim:

- `detect url-liveness in ~/.claude/skills/citation-detail-verify/test-corpus/dead-link.md count >=1`
- `detect title-match in ~/.claude/skills/citation-detail-verify/test-corpus/wrong-title.md count >=1`
- `detect author-drift in ~/.claude/skills/citation-detail-verify/test-corpus/author-reorder.md count >=1`
- `detect year-match in ~/.claude/skills/citation-detail-verify/test-corpus/year-off-by-one.md count >=1`
- `detect verbatim-quote-mismatch in ~/.claude/skills/citation-detail-verify/test-corpus/quote-paraphrased.md count >=1`
- `detect anchor-fabrication in ~/.claude/skills/citation-detail-verify/test-corpus/fake-section-ref.md count >=1`
- `detect frontmatter-body-citation-mismatch in ~/.claude/skills/citation-detail-verify/test-corpus/orphan-citation.md count >=1`
- `detect paywalled-source-finding in ~/.claude/skills/citation-detail-verify/test-corpus/paywalled-sources.md count >=1`
- `absent status=fail-on-source-format-prevented-check in ~/.claude/skills/citation-detail-verify/test-corpus/paywalled-sources.md`
- `detect refusal-category-bias in ~/.claude/skills/citation-detail-verify/test-corpus/bad-invocations-output-sample.md count >=2`
- `absent missing-evidence-quote-when-status=fail in ~/.claude/skills/citation-detail-verify/test-corpus/`
- `detect citation-detail-drift in ~/.claude/skills/citation-detail-verify/test-corpus/citation-detail-drift-fixture.md count >=3`

Added by the v1.3 fetch-liveness fallback ladder change (back-propagate to the brief on its next edit):

- `detect liveness-ladder-recovery in ~/.claude/skills/citation-detail-verify/test-corpus/ua-gated-liveness.md count >=1`
- `absent premature-unverifiable in ~/.claude/skills/citation-detail-verify/test-corpus/ua-gated-liveness.md`

Added by the candidates-capture change (back-propagate to the brief on its next edit):

- `detect dropped-at-citation-detail-verify in ~/.claude/skills/citation-detail-verify/test-corpus/candidate-disposition.md count >=1`

The `test-corpus/` fixtures these DSL rows resolve against are Stage-1-follow-on work. Stage 1 ships the SKILL.md + the two v1.0 lock artifacts (`references/output-schema.md`, `references/cache-contract.md`); fixtures and the `criteria-validate` runner that turns these DSL rows into pass / fail verdicts ship later in the family build.

## Load-when table

| Step | Reference | Why load |
|------|-----------|----------|
| 3, 6 | [`references/output-schema.md`](references/output-schema.md) | Row + envelope shape, check-name vocabulary, status semantics, verdict computation. Frontmatter 2.0 (wire `"1.0"`); REUSED by sibling skills. |
| 3 (per fetch) | [`references/cache-contract.md`](references/cache-contract.md) | Cache key derivation, on-disk path, atomicity, invalidation. v1.4 lock; sibling skills cross-read the same path; PDF bodies carry `body.txt` per §Read protocol. |
| Invocation refusal | [`references/refusal-record.md`](references/refusal-record.md) | Refusal-record shape (`refusal: {category, rule, evidence}`). v1.0 lock; REUSED by sibling skills. |
| 5 (per failing citation) | [`references/candidates-contract.md`](references/candidates-contract.md) | `candidates.jsonl` record shape, sidecar location, `append-disposition` refusals, who-writes-what. v1.0 lock owned here; REUSED by `survey-author`, `oq-resolver`, `source-recency-probe`, `load-bearing-fullread`, `study-run`. Helper: `scripts/candidates.py` (run, don't read). |

The references are loaded when the workflow needs them, not at skill startup. Each reference is self-contained per progressive disclosure — the SKILL.md does not restate row fields or cache layout.

## Invocation discipline

Dominant concern per brief: **bloat** (mechanical primitive, narrow LLM surface). Bias risk is flag-fishing only. Forbidden surfaces (skill refuses with a refusal record per `references/refusal-record.md`):

- Per-citation "focus here" hints (e.g., `--focus [A18]`). Skill scans every citation; caller-directed focus invalidates the universal-pass guarantee downstream skills rely on.
- Caller's belief about the correct value (e.g., `--expected-year 2023`). Caller-supplied "actual" short-circuits the mechanical fetch.
- Pre-filtered citation list (e.g., `--citations [A1],[A5]`). Whole-artifact-pass is load-bearing for downstream skills.
- Attached source full-texts. Skill fetches via `WebFetch`; caller-attached body bypasses URL-liveness verification as a side effect.
- Full artifact body when only citation surfaces are verified. Skill reads frontmatter + inline citation contexts (±2 lines for verbatim-quote anchor resolution).

Good brief: `/citation-detail-verify --artifact content/survey/llm-review-landscape.md`. Pointer only; skill derives the citation list mechanically from the artifact's two surfaces.

Bad brief: `/citation-detail-verify --artifact content/survey/llm-review-landscape.md --focus A18 --expected-year 2023`. Pre-filtered + caller-supplied actual; refuse with refusal record.

## Out of scope

- Auto-fixing citation drift. Skill surfaces `cited: 2024, actual: 2023`; author edits the artifact. Auto-fix would silently rewrite the author's claim without audit trail.
- Verifying the *framing* of cited evidence. That's `/load-bearing-fullread`.
- Discovering missing citations. That's `/source-recency-probe`.
- Generating alternative interpretations. That's `/adversarial-frame`.
- Sources behind paywalls or in formats `WebFetch` can't handle. Skill surfaces `unverifiable` with reason; never fabricates a pass.

## Cross-skill compatibility

`references/output-schema.md`, `references/cache-contract.md`, and `references/refusal-record.md` are locked. Their lock-document frontmatter versions are output-schema `2.0`, cache-contract `1.4`, refusal-record `1.4`; the **wire** `version` every envelope carries is `"1.0"` and has not moved. A fourth lock, `references/candidates-contract.md` v1.0, is owned here too — the proposal-time candidate record and its `scripts/candidates.py` helper; it is not an envelope and its consumers roster (`survey-author`, `oq-resolver`, `source-recency-probe`, `load-bearing-fullread`, `study-run`) is in its frontmatter. A second helper, `scripts/pdf_extract.py`, is the executable form of `cache-contract.md` v1.4 §Extracted text match key and its miss-path extraction; its invariants are `scripts/test_pdf_extract.py`. Sibling research-pipeline skills REUSE the three envelope-side locks unchanged:

- `/load-bearing-fullread` — uses the same envelope shape and registers its own `framing-drift-*` check-name values; reads from / writes to the same cache.
- `/adversarial-frame` — same envelope; registers `surfaced-alternative-*` check-name values; same cache.
- `/source-recency-probe` — same envelope; registers `new-candidate-found`, `source-superseded-by-newer`, `venue-absent-from-sources`, `source-unresolved`, `nothing-to-probe`, and `probed-no-candidates` (six names as of output-schema frontmatter v2.0; the seventh, `topic-tag-uncatalogued`, is deprecated — kept registered so older envelopes parse, never emitted); same cache.
- `/survey-refresh` and `/invocation-discipline-lint` — same envelope; each registers its own check-names. The frontmatter `consumers:` list in each lock is the authoritative roster.

Bumping the **wire** major (`"1.0"` → `"2.0"`) requires a coordinated code change across every consumer. Bumping a lock document's **frontmatter** major requires no code change, but every consumer's pointer text naming that lock's version must move in the same PR.

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
