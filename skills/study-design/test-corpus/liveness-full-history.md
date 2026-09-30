# Fixture: liveness-full-history

Exercises Workflow Step 1a — the liveness check runs over the **full** `main`
history fetched from the publication URL, not just the current tip, so a
document removed from HEAD without a `withdrawn:` frontmatter field still
blocks a new proposal for the same OQ. This fixture's payload is an open
question rather than an artifact under probe, so the section below is named
`## Open question under design` instead of `## Artifact under probe`, per
the sibling fixtures' stated deviation. This is a refusal fixture: it
asserts the skill refuses to propose a new study while a live document for
the same OQ exists anywhere in that history.

## Open question under design

```yaml
---
id: "0002"
status: open
date: 2026-06-02
tags: [review-pipeline, staleness]
unblock-by:
  - "At what threshold does the staleness flagger's flag rate stop tracking
     real drift and start tracking noise — 60 days, 90 days, or 180 days?"
---
```

Body (excerpt): the same OQ-0002 the `d1-contrast-metric` fixture designs a
study for. This fixture exercises the case where a study for OQ-0002
already exists in the publication history, so Step 1a must catch it before
Step 2 ever reads `unblock-by` again.

## Expected skill output

**Case 1 — live document on `main`, no results yet.** `content/evals/
staleness-threshold-calibration-pass.md` was added to `main` as a single
commit; it has not been run (no `## Findings` / `### Run` subsection under
it), and it carries no `withdrawn:` frontmatter field. A companion PR (#135)
proposing a *different* framing of the same study is open but unmerged —
irrelevant to liveness, since Step 1a reads the publication remote's `main`
history, not open PRs. Running

```bash
python3 ~/.claude/skills/study-run/scripts/recheck.py liveness --repo <R>
```

over the full fetched `main` history returns:

```json
{"path": "content/evals/staleness-threshold-calibration-pass.md", "oq": "OQ-0002", "removed": false}
```

`removed: false` because the document is still present at the current tip.
Its subject-line match tolerates the real corpus's line-wrapped phrasing —
"…for\n[OQ-0002](…)" wraps across a line break, and the liveness check's
subject pattern is whitespace-tolerant by design, so the wrap does not hide
the match. Because this row names OQ-0002 and is live (no `withdrawn:`, no
`### Run` subsection), the skill refuses to propose a new study for OQ-0002
and reports this row, plus PR #135 as an open, results-less attempt against
the same OQ.

liveness-blocks-proposal-full-history

**Case 2 — a document deleted from HEAD without `withdrawn:`.** A separate
prior study for OQ-0002, `content/evals/staleness-threshold-first-pass.md`,
was deleted from `main` by a later "revert" commit that removed the file but
never added a `withdrawn:` frontmatter field to it before deleting it.
Because Step 1a's liveness check walks the full history (`git log --diff-
filter=A` back to each path's addition, then reads the last committed text
before it left HEAD when it is absent at the tip) rather than only the
current tree, this document is still evaluated: no `withdrawn:` field was
ever set, and no `### Run` subsection exists under its `## Findings`
heading, so it is still live despite being gone from HEAD:

```json
{"path": "content/evals/staleness-threshold-first-pass.md", "oq": "OQ-0002", "removed": true}
```

`removed: true` here — distinct from Case 1's `removed: false` — reports
that the document is gone from the current tree, but liveness does not turn
on presence at HEAD; it turns on whether the document was ever formally
withdrawn. A revert that deletes a file is not the same act as setting
`withdrawn:`, so this row still blocks a new proposal for OQ-0002, exactly
as Case 1's still-present row does.

Against the real corpus today, this same check reports EVAL-0003 (OQ-0002)
and EVAL-0002 (OQ-0062) as live, and EVAL-0001 (OQ-0061) as not live — the
document EVAL-0001 wrote a `### Run` subsection under `## Findings` at
commit f9ca43b, so it no longer blocks a new proposal for OQ-0061.

## Invariants exercised

- `liveness-blocks-proposal-full-history` token present, asserting Step 1a's
  refusal fired from a document found anywhere in the fetched `main`
  history, not only at the current tip.
- Case 1's `removed: false` and Case 2's `removed: true` are both reported as
  live — liveness is a function of `withdrawn:` and the presence of a
  `### Run` subsection under `## Findings`, never of presence at HEAD alone;
  a document `removed: true` without `withdrawn:` still blocks a proposal.
- The subject-line match tolerates the real corpus's line-wrapped phrasing
  ("…for\n[OQ-0002](…)") — the check is whitespace-tolerant, not a bare
  single-line substring match.
- The skill refuses to write a new study document for OQ-0002 while either
  row remains live, and reports the open, results-less PR (#135) alongside
  the two live-document rows rather than silently dropping it.
