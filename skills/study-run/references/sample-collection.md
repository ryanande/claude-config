# study-run — sample collection from the candidates sidecar

Loaded at Workflow Step 5 when the frozen `sample:` field names proposal-time
candidate citations (EVAL-0001, EVAL-0002, and any later study over the same
instrument). The record contract is
[`../../citation-detail-verify/references/candidates-contract.md`](../../citation-detail-verify/references/candidates-contract.md)
v1.0; this leaf is how `study-run` reads it without re-deciding anything the
pre-registration block already fixed.

## Discovery

```bash
R=<research-docs-root>   # resolved in Step 1, never the CWD
python3 ~/.claude/skills/citation-detail-verify/scripts/candidates.py list --repo "$R" > <run-dir>/sample.json
```

The rule behind that command is `git -C "$R" ls-files -- '*.candidates.jsonl'`:
sidecars tracked at HEAD are the sample (`source: tracked`). Rows from the
machine-local spool that no tracked sidecar holds arrive tagged
`source: spool`. Report the two strata separately — session count, row count,
and the metric each way — and never pool spool rows into the tracked count
silently. A study whose stopping rule is met only when spool rows are counted
states that in the appended result.

Named limitation the result must carry: a proposing run whose PR never merged
is visible only as spool rows on the machine that ran it. `list` on another
machine cannot see them.

## Field mapping per design

- **Session count** (both stopping rules): distinct `session_id` over the
  rows in scope, per stratum.
- **EVAL-0001 (D3).** In scope: rows with a non-empty `sentence`. Stratum:
  `source_in_context` — `false` is the primary (unfetched) population the
  block's ≥ 20-per-arm target counts; `true` is the secondary contrast, never
  pooled into the primary — and, at contract v1.0, empty by construction (no
  writer records after a fetch), which the appended result states rather
  than reporting a silent zero. Arm assignment uses the block's own proxy over
  `source_meta.published_year`, `source_meta.openalex_cited_by_count`, and
  `source_meta.reference_class`. Where a row's proxy inputs are `null`,
  complete them in ONE lookup pass before any sentence is graded, write that
  snapshot (record_id → inputs → arm) under `assets/evals/<id>/`, and state
  in the appended result that the count was taken at that pass rather than
  at capture time — the block says "at capture time", and the deviation is
  reported, not hidden. A row whose source fits neither arm definition is
  recorded and excluded from both arms, per the block.
- **EVAL-0002 (D1).** In scope: every row. The precision denominator is every
  row; `disposition: proposed` at run time is an unresolved row that stays in
  the denominator. The stage-of-catch covariate reads the recorded
  `disposition` (`dropped-at-reread` / `dropped-at-citation-detail-verify` /
  `corrected-at-fullread` / `landed`); `withdrawn` rows have no catching stage
  and are reported as their own count, outside the covariate distribution but
  inside the precision denominator.

## Recorded trail vs "running the stages"

EVAL-0002's protocol answers stage attribution "by running the stages, not by
recalling what happened in the session." The sidecar's `disposition` /
`disposition_stage` / `label` are the pipeline's OBSERVED trail, written by
the stage that fired at the time — not a recollection, but not an independent
re-run either. Treat them as a covariate to compare against, not as the
answer: adjudication re-reads each candidate against its fetched source and
records the first stage that would have flagged it, then reports agreement
between the re-derived stage / label and the recorded ones. Disagreement is a
finding about the pipeline, not a reason to edit the sidecar — `study-run`
never writes to it.

## Provenance stripping for labelers

Per `adjudication-mechanics.md`, a labeler sees one item and no expected-label
slot. Before a row reaches a spawn, strip: `record_id`, `session_id`,
`proposed_at`, `dispositioned_at`, `disposition`, `disposition_stage`,
`label`, `source_meta`, `source`, `sidecar`, and — for EVAL-0001, per its
grading protocol — `candidate.id`, `candidate.title`, `candidate.url_or_identifier`,
and the arm. EVAL-0001 hands the labeler `sentence` alone; EVAL-0002 hands the
labeler `candidate` and the fetched source. Anything in that list lets a
labeler correlate items across the batch or read the pipeline's own verdict.
