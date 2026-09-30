# Fixture: the sample is the tracked `candidates.jsonl` sidecars, strata kept apart

## Study document under execution

`content/evals/per-candidate-citation-hallucination-rate.md` (EVAL-0002),
tamper guard passed. Its frozen `sample:` reads "Every candidate citation
proposed by a gather or gap-find subagent, recorded verbatim at proposal time
(before any WebFetch) …". Workflow Step 5 therefore collects per
`references/sample-collection.md`:

```
python3 ~/.claude/skills/citation-detail-verify/scripts/candidates.py list --repo "$R"
```

## What `list` returned

- `git -C "$R" ls-files -- '*.candidates.jsonl'` → 3 tracked sidecars:
  `content/survey/llm-review-landscape.md.candidates.jsonl` (2 sessions, 41 rows),
  `content/notes/oq-0062-per-candidate-citation-hallucination-findings.md.candidates.jsonl`
  (1 session, 14 rows), `content/rfc/0031-review-judges.md.candidates.jsonl`
  (1 session, 9 rows) — 64 rows, 4 distinct `session_id`, all `source: tracked`.
- An untracked `content/survey/draft-in-progress.md.candidates.jsonl` exists
  in the working tree: NOT listed — not tracked at HEAD, not sample.
- The spool holds 6 rows from an `oq-resolver` run that aborted
  `evidence-unverified` and never committed: listed with `source: spool`.

## Expected skill output

```
sessions: 4 tracked (+1 spool-only)
denominator: 64 tracked rows (+6 spool-only rows, reported separately, not pooled)
still proposed at run time: 5 of 64 → unresolved, kept in the denominator
disposition trail (observed covariate, tracked rows): dropped-at-reread 7, dropped-at-citation-detail-verify 1,
  corrected-at-fullread 2, landed 47, withdrawn 2 (no catching stage; outside the covariate), proposed 5
stopping rule (>= 3 sessions, >= 60 candidates): met on tracked rows alone
```

Token for this trajectory: `candidates-sidecar-discovery`.

## Invariants exercised

- Discovery is one git command over the research-docs root Step 1 resolved;
  an untracked or uncommitted sidecar is never sample — the same stance as
  the Step 2 tamper guard.
- `source: tracked` and `source: spool` are counted and reported separately;
  the stopping rule is evaluated on each and the result says which one met it.
- Rows still `proposed` stay in the denominator as unresolved (`unresolved-counted-in-denominator`).
- The recorded `disposition` / `label` are reported as the observed trail and
  compared with adjudication's re-derived stage; they are never handed to a
  labeling spawn (`references/sample-collection.md` §Provenance stripping).
- `study-run` wrote nothing to any sidecar.
