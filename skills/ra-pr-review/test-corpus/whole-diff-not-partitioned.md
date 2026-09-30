# Fixture: whole-diff-not-partitioned

Exercises RFC-0018 rule 2 as tightened for PR review: every critic receives the WHOLE diff, not a
file-group partition — a deliberate change from ra-pr-review's prior "split reviewers by area/file
group for large PRs" behavior.

Marker token: `whole-diff-to-every-critic`.

## Scenario

A PR touches `api/auth.py`, `api/session.py`, and `web/login.tsx` across a combined change that
moves a security check from the API layer into the frontend. k=2 run.

- **Before this refactor:** reviewers would have been split by file group (one over `api/*`, one
  over `web/*`), and the cross-cutting defect — the security check moved to a layer the client
  controls — would only be visible to whichever reviewer happened to notice both halves, since
  neither reviewer's file group contains the whole story.
- **After this refactor:** both `correctness` and `security-and-data-safety` critics receive the
  full diff across all three files. `whole-diff-to-every-critic` holds for both lenses, so the
  security-and-data-safety critic can trace the check's removal from `api/auth.py` all the way to
  its (missing) enforcement in `web/login.tsx` within a single critic's context.

## Documented residual

Every critic reads the same diff file, and returns its sha256 as `DIFF-READ` so the orchestrator
can check it opened the right one. For a long diff the critic reads that file in chunks (Read
offset/limit) rather than the orchestrator pre-splitting review responsibility across critics;
over ~3,000 lines the orchestrator warns the user first. Extra file context (the full function
around a hunk, its callers, existing tests) is pulled by the critic from the PR-head worktree.
The sha256 proves the right file was opened, not that every line was read — that part remains an
instruction.

## Invariants exercised

- `whole-diff-to-every-critic` — no per-critic file-group partition, for any lens, at any diff
  size.
- A cross-cutting defect spanning multiple files is visible to any single critic reviewing the
  whole diff.
