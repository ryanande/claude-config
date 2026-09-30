---
fixture: candidate-disposition
exercises: framing-drift-relative-vs-absolute, corrected-at-fullread
expected-verdict: fail
---

# Fixture — candidate-disposition

A source whose probe surfaces framing drift also dispositions its proposal-time
record per `../../citation-detail-verify/references/candidates-contract.md`.

## Invocation

```
/load-bearing-fullread --artifact content/rfc/0031-review-judges.md --source-ids A7
```

## Source A7 — drift detected

- citation-id: `[A7]`
- `framing-drift-relative-vs-absolute`: `fail` — the artifact reports "a 40%
  reduction in judge error"; the paper's Table 3 shows 0.15 → 0.09 absolute
  (evidence-quote carries the table row verbatim).
- other three probes: `pass`.

Envelope `verdict: fail`.

## Disposition (Workflow step 8)

```
python3 ~/.claude/skills/citation-detail-verify/scripts/candidates.py list --repo "$R" --artifact content/rfc/0031-review-judges.md
python3 ~/.claude/skills/citation-detail-verify/scripts/candidates.py append-disposition --repo "$R" --artifact content/rfc/0031-review-judges.md --record-id 3f9a1c2b7d0e --disposition corrected-at-fullread --stage load-bearing-fullread --label Minor
```

The record's four disposition fields become
`corrected-at-fullread` / `load-bearing-fullread` / `Minor` / `<UTC now>`;
every other line of the sidecar is byte-identical.

## Invariants exercised

- `corrected-at-fullread` is written only for a source with ≥ 1 `fail` row;
  `unverifiable` rows do not disposition anything.
- The record was still `proposed` — `citation-detail-verify` had passed it —
  which is exactly the stage-of-catch EVAL-0002 wants distinguished from a
  detail-level drop.
- Had `citation-detail-verify` already dispositioned it, `append-disposition`
  refuses (`already dispositioned`) and this skill writes nothing; a
  disposition is written once.
- No matching `proposed` record → nothing written; the skill never fabricates
  a proposal.
