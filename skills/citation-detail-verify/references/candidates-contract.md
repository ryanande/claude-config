---
title: Proposal-time citation-candidate record (candidates.jsonl) for the research-pipeline skills
version: 1.0
status: locked
owners: [citation-detail-verify]
consumers: [survey-author, oq-resolver, source-recency-probe, citation-detail-verify, load-bearing-fullread, study-run]
---

# Candidates contract v1.0

Locked in the candidates-capture change. Two pre-registered studies in
`research-docs` — EVAL-0001 (`content/evals/citation-confidence-phrasing-vs-source-density.md`,
OQ-0061) and EVAL-0002 (`content/evals/per-candidate-citation-hallucination-rate.md`,
OQ-0062) — sample from a record "written at proposal time, before any
WebFetch" that no stage wrote before this contract; EVAL-0001's first run
(2026-09-06) returned 0 sessions / 0 candidates for that reason. This document
is the record's shape, where it lives, who writes what, and how `study-run`
finds it. The executable form is `../scripts/candidates.py`; its invariants
are `../scripts/test_candidates.py`.

Three writer roles. **Proposing** stages (`survey-author` gather / gap-find,
`oq-resolver` Step 5, `source-recency-probe` Step 6) call `append`.
**Verifying** stages (`citation-detail-verify`, `load-bearing-fullread`, and
the WebFetch re-read inside the two authoring skills) call `append-disposition`.
**Reading** is `study-run` Step 5 via `list`. `study-design` neither writes nor
reads it.

## Sidecar location

```
<research-docs-root>/<artifact-path>.candidates.jsonl
```

`<artifact-path>` is the repo-relative path of the document whose `sources[]`
the candidate is proposed for — `content/survey/foo.md` yields
`content/survey/foo.md.candidates.jsonl`. The sidecar is committed with the
artifact, in the same PR, so the denominator lands beside the source list it
produced and a reviewer sees both. An absolute `--artifact`, or one that
escapes the root, is refused.

Why alongside the artifact, and not a per-session directory:

- `study-run` already resolves the research-docs root (`DX_ARCH_META_ROOT` →
  `<root>/repos/research-docs`, or `--repo`) and treats git as the record
  (its tamper guard is `git ls-files` / `git status` / `git log`). One git
  command over that root is the whole discovery rule (below).
- Both studies accumulate ≥ 3 sessions across months and cluster "by session
  and by artifact". A committed file survives session teardown, machine
  changes, and the worktree removal `oq-resolver` performs on every exit path.
- A per-session directory under `~/.claude/` is machine-local, unreviewed,
  invisible to a run on another machine, and makes "which artifact" a lookup.

`oq-resolver` fixes its draft disposition artifact's path at the start of
Step 5, before discovery, so its records have a stable anchor.

### Spool (safety net, not the record)

Every write is mirrored to a machine-local per-session spool:

```
~/.claude/skills/citation-detail-verify/candidates/<session_id>.jsonl   ($CANDIDATES_SPOOL overrides the directory)
```

The spool exists for one reason: a run that aborts after proposing (an
`oq-resolver` `evidence-unverified` abort, a refusal, a crash) never commits,
and its worktree is removed — without the spool exactly the sessions that
produced weak or fabricated candidates would vanish from EVAL-0002's
denominator (survivorship bias). The spool directory is gitignored in this
repo and excluded from the deployer's delete-sync, the same treatment as
`cache/`. It is never the primary record: `list` tags spool-only rows
`source: spool` and `study-run` reports them as their own stratum.

## Record shape

One JSON object per line, keys sorted, `ensure_ascii=False`, `\n`-terminated.
No line is ever rewritten except by `append-disposition`, which rewrites the
four disposition fields of exactly one record.

```json
{"version": "1.0",
 "record_id": "<12 lowercase hex: sha256(session_id|artifact|stage|candidate.id|candidate.url_or_identifier|proposed_at)>",
 "session_id": "<$CLAUDE_SESSION_ID, else $CLAUDE_CODE_SESSION_ID>",
 "artifact": "<repo-relative path>",
 "stage": "gather | gap-find | recency-probe-candidate | other",
 "proposed_at": "<ISO-8601 UTC, second precision>",
 "candidate": {"id": "<as proposed, e.g. A12; may be empty>",
               "title": "<as proposed>",
               "url_or_identifier": "<as proposed; may be empty>"},
 "sentence": "<verbatim citing sentence as proposed; empty for id-only proposals>",
 "source_in_context": false,
 "source_meta": {"published_year": null, "openalex_cited_by_count": null, "reference_class": null},
 "disposition": "proposed",
 "disposition_stage": null,
 "label": null,
 "dispositioned_at": null}
```

### Field semantics

| Field | Written by | Meaning |
|---|---|---|
| `session_id` | `append` | Same read order as `cache-contract.md` §meta.json shape: `$CLAUDE_SESSION_ID`, then `$CLAUDE_CODE_SESSION_ID`. Neither set, or empty → refuse; nothing is written. Never fabricated. |
| `stage` | `append` | Which proposing step: survey gather subagent → `gather`; survey gap-find subagent → `gap-find`; `oq-resolver` Step 5 discovery → `gather`; `source-recency-probe` `new-candidate-found` / `source-superseded-by-newer` rows → `recency-probe-candidate`; anything else → `other`. `--seed-urls` handed to `survey-author` are caller-supplied, not proposed, and are NOT recorded. |
| `candidate` | `append` | Exactly as proposed, before any fetch. At least one of `id` / `url_or_identifier` MUST be non-empty. |
| `sentence` | `append` | The citing sentence verbatim as the proposing model wrote it — EVAL-0001's unit of analysis. Empty when the proposal carried no prose (recency-probe rows; a search hit selected for fetching). |
| `source_in_context` | `append` | `true` iff the source's text was in the drafting model's context when the sentence / candidate was proposed. A gather or gap-find subagent proposing from memory → `false`. A hit selected from search results before it is fetched → `false`. A sentence written after a WebFetch → `true`. Metadata alone (an OpenAlex row) is not source text → `false`. EVAL-0001's primary population is the `false` stratum. No writer in v1.0 emits `true` — every call site records before its fetch; the value is reserved for a future post-fetch writer and stays in the schema so the stratum flag is never implicit. |
| `source_meta` | `append` | EVAL-0001's arm proxy inputs when the proposing stage knows them: `published_year`, `openalex_cited_by_count` (at capture time), `reference_class` ∈ `standard-reference` / `arxiv-preprint` / `other`. `source-recency-probe` always has the first two from OpenAlex; a subagent proposing from memory usually has none, and `null` is the honest value. |
| `disposition` | `append-disposition` | `proposed` until a stage decides. Then exactly one of: `dropped-at-reread` (the WebFetch re-read found no such source or a wrong detail — EVAL-0002 "dropped at WebFetch re-read"), `dropped-at-citation-detail-verify`, `corrected-at-fullread`, `landed` (in the committed `sources[]`, clean), `withdrawn` (not adopted for a non-veracity reason: scope, duplicate, superseded). `withdrawn` exists so a relevance drop is never filed as a hallucination catch; it carries no stage-of-catch. |
| `disposition_stage` | `append-disposition` | Who wrote the disposition: `survey-author`, `oq-resolver`, `citation-detail-verify`, `load-bearing-fullread`. |
| `label` | `append-disposition` | The stage's own detail label at disposition time — `Exact` (real source, all details correct), `Minor` (real source, one detail wrong), `Major` (no such source, or ≥ 2 details wrong): the CiteCheck partition EVAL-0002 borrows as a labelling scheme. It is an observed value, NOT the study's adjudication: `study-run` re-derives labels cold and never shows this field to a labeler. |
| `dispositioned_at` | `append-disposition` | ISO-8601 UTC. |

A record still `proposed` when a study runs is an unresolved denominator row.
`study-run` reports it as such, never drops it.

## Operations

```
candidates.py append --repo <root> --artifact <path> --stage <s> --title <t> [--id <id>] [--url <u>]
                     [--sentence <s>] --source-in-context true|false
                     [--published-year N] [--cited-by-count N] [--reference-class <c>]
candidates.py append --repo <root> --artifact <path> --from-json <file>     # JSON array of the same fields
candidates.py append-disposition --repo <root> --artifact <path>
                     (--record-id <id> | --candidate-id <id> [--url <u>])
                     --disposition <d> --stage <who> [--label Exact|Minor|Major]
candidates.py list --repo <root> [--artifact <path>] [--tracked-only]
```

`--repo` is the research-docs checkout the stage is writing into — normally a
worktree, never the canonical checkout. Skills run the DEPLOYED copy:
`python3 ~/.claude/skills/citation-detail-verify/scripts/candidates.py …`.

### `append`

Appends exactly one line per candidate (`--from-json` loops the same rule
over a batch — the shape a gather subagent's returned list already has).
Prints the `record_id`. Refuses, writing nothing to either file, when:

- no session id (above);
- `stage` is not in the vocabulary, or both `id` and `url_or_identifier` are empty;
- the same `(session_id, stage, id, url_or_identifier)` is already recorded —
  a duplicate would double-count the denominator; the same candidate at a
  different stage is not a duplicate;
- the existing sidecar has a malformed, blank, or non-record line, or lacks a
  trailing newline — the record is not silently repaired.

Existing bytes are never touched: the write is an `O_APPEND` of the new line,
flushed and fsynced.

### `append-disposition`

Rewrites the four disposition fields of exactly one record, atomically
(temp file + `rename`), leaving every other line byte-identical, then mirrors
the same record in its session spool (a missing spool entry is tolerated —
the sidecar is the record). Prints the `record_id`. Refuses when:

- the sidecar does not exist, or no still-`proposed` record matches — a
  disposition is never fabricated for a candidate nobody recorded;
- `--candidate-id` / `--url` match more than one still-`proposed` record (the
  same paper proposed in two sessions): the refusal names the `record_id`s;
  resolve with `list --artifact <path>` and pass `--record-id`;
- the record is already dispositioned — a disposition is written once, never
  overwritten;
- `disposition`, `stage`, or `label` is outside its vocabulary.

Verify stages that run in a later session than the proposal MUST resolve the
record through `list --artifact <path>` and pass `--record-id`; the
`--candidate-id` shortcut is for the single-session case.

### `list` — the discovery rule

```bash
git -C "$R" ls-files -- '*.candidates.jsonl'
```

Sidecars **tracked at HEAD** of the research-docs checkout are the sample
(`source: tracked`). An untracked or uncommitted sidecar is not — the same
stance as `study-run`'s tamper guard: a record only in a working tree can be
edited after the fact. Spool rows whose `record_id` is not in any tracked
sidecar are appended with `source: spool` and the spool file as `sidecar`;
`--tracked-only` omits them. Each row carries `source` and `sidecar` in
addition to the record fields. Output is a JSON array, keys sorted.

Named limitation: a proposing run whose PR never merges leaves its rows
spool-only on one machine. `study-run` reports the spool stratum separately
and never pools it into the tracked count silently.

## Who writes what, in pipeline order

| Point | Call | Fields |
|---|---|---|
| `survey-author` — author receives a gather / gap-find subagent's proposal list | `append` (or `--from-json`) BEFORE the Stage 1c WebFetch | stage `gather` / `gap-find`, `sentence` verbatim, `source_in_context: false` |
| `survey-author` / `oq-resolver` — WebFetch re-read rejects a candidate | `append-disposition` | `dropped-at-reread`; label `Major` when no such source resolves, `Minor` when the source exists but a proposed detail was wrong |
| `oq-resolver` Step 5 — a search hit is selected for fetching | `append` BEFORE the fetch | stage `gather`, `sentence` empty, `source_in_context: false` |
| `source-recency-probe` Step 6 — each `new-candidate-found` / `source-superseded-by-newer` row | `append` | stage `recency-probe-candidate`, `sentence` empty, `source_in_context: false`, `source_meta` from the OpenAlex row |
| `citation-detail-verify` Step 5 — a citation's six checks aggregate to `fail` | `append-disposition` when a `proposed` record matches | `dropped-at-citation-detail-verify`; `Minor` for one failing detail check, `Major` for `url-liveness` fail or ≥ 2 |
| `load-bearing-fullread` Step 8 — a source has ≥ 1 `fail` row | `append-disposition` when a `proposed` record matches | `corrected-at-fullread`, `Minor` |
| authoring stage at commit — landing sweep | `append-disposition` per still-`proposed` record | `landed` + `Exact` if in the committed `sources[]`; else `withdrawn` |

A verify stage that finds no matching `proposed` record writes nothing — the
denominator is what was proposed, not what was verified.

## Versioning

- Major (`2.0`) — a change to the sidecar path, the discovery rule, a required
  field's meaning, or a vocabulary removal. Readers MUST fail closed on an
  unknown `version` (`parse_lines` refuses).
- Minor (`1.x`) — additive only: new optional `source_meta` keys, new
  vocabulary values appended to an enum, new `list` output columns. Older
  readers ignore unknown optional fields.
- Every consumer's pointer text naming this version moves in the same PR as
  a bump; the `consumers:` roster above is authoritative.

This lock shares nothing with `output-schema.md` (it is not an envelope) and
depends on `cache-contract.md` only for the session-id read order.
