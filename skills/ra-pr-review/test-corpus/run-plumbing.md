# Fixture: run-plumbing

Exercises the run-time guarantees that sit under the critic ensemble for `/ra-pr-review`: which
agent type the critics are, how "every critic read the whole diff" is checked, which checkout
adjudication reads, and how the comment is posted.

Markers: `critic-type-explicit-tool-grant`, `diff-read-mismatch-yields-unverifiable`,
`adjudicate-at-pr-head-worktree`, `post-never-edit-last`.

## Critic agent type

`critic-type-explicit-tool-grant` — every critic is spawned with `subagent_type: pr-review-critic`,
whose frontmatter lists `tools: Read, Grep, Glob, Bash`. That list has no `SendMessage`,
`ListAgents` or `Agent`, which is what RFC-0018 rule 5's no-cross-talk claim rests on. A spawn of
`general-purpose` (grant `*`) would break the claim, so preflight aborts when the type is not
installed instead of falling back.

## Diff-read check

`diff-read-mismatch-yields-unverifiable` — PR #42, k=2. The orchestrator writes the diff to
`<scratch>/pr-42.diff` and records its sha256 (not shown to critics).

| critic | lens | DIFF-READ returned | outcome |
|---|---|---|---|
| 1 | correctness | matches | findings adjudicated normally |
| 2 | security-and-data-safety | missing | findings discarded; one synthetic `unverifiable` row, `check-name: lens-finding-minor` |

With no `fail` rows from critic 1 the verdict is `unverifiable`, never `pass` — the same rule as
a dead critic.

## Adjudication checkout

`adjudicate-at-pr-head-worktree` — the session is on `main`; PR #42's head is `abc1234`. The
orchestrator fetches `pull/42/head`, checks that `FETCH_HEAD` equals `headRefOid`, and adds a
detached worktree at `abc1234`. Critic context reads and every adjudication read happen in that
worktree. A finding about `loadUser` is checked against `loadUser` as it exists at `abc1234`, not
as it exists on `main`, where the diff has not landed.

The session is a fork clone (`origin` = the user's fork, `upstream` = the base repo). The fetch
uses the base repo's URL, not `origin`, so `pull/42/head` resolves. Right after writing the diff
file the orchestrator re-reads `headRefOid`; had the author pushed in between, the run aborts
instead of reviewing a diff and a worktree from different commits.

A finding that a test was deleted is anchored `base:tests/test_users.py:30` — the line has no
head-side position. It is grounded on the diff's `-` line and a grep of the worktree confirming
the test was removed, not moved.

A finding located in an untouched caller (`api/routes.py:40`) is publishable because its cause,
`api/users.py:12`, is a line the diff changes; the comment shows both.

## Posting

`post-never-edit-last` — the user's latest comment on PR #42 is an unrelated question. The skill
looks up comments whose author is the current user and whose body starts with `## Review:`,
PATCHes the last such comment by id through `gh api`, and leaves the unrelated question alone.
With no prior review comment it creates a new one with `gh pr comment --body-file`.
`gh pr comment --edit-last` is never used.

## Invariants exercised

- `critic-type-explicit-tool-grant` — critics never run as `general-purpose`.
- `diff-read-mismatch-yields-unverifiable` — a wrong or missing `DIFF-READ` counts as a dead critic.
- `adjudicate-at-pr-head-worktree` — code is read at `headRefOid`, not the session branch.
- `post-never-edit-last` — only this skill's own `## Review:` comment is ever edited.
