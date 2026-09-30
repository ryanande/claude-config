---
name: retro
description: End-of-work-chunk retrospective. Honestly answers what got lost, what worked, what didn't happen but should have, and what surprised — split process vs technical, capped, audience-tagged, with confidence and inference tags. Persists findings to ./retros/ before sign-off so unapplied items survive context decay. Designed to run before /handoff. Trigger with /retro, "let's do a retro", "what did we miss this session", or before declaring a session done.
user-invocable: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

## Why these tools

| Tool | Used at | Why |
|---|---|---|
| Bash | Step 0 prereq checks; Step 1 git/gh survey; Step 5.5 `git cat-file -e <sha>` cite validation | git/gh state queries with no native equivalent |
| Read | Step 1 INDEX recurrence; Step 2/3/5 reference loads; Step 5.5 self-verify | reference + verification loads |
| Write | Step 5 retro file creation; Step 5 INDEX append (when file is absent) | net-new files |
| Edit | Step 5 INDEX append (when file exists); Step 6 applying accepted triage items | in-place edits to existing files |
| Glob | Step 1 enumerate prior `./retros/*.md` for recurrence check | path discovery |
| Grep | Step 1 INDEX scan; Step 5.5 grep-asserts on saved file (header presence, tag presence, cap counts) | content search with structural extraction |

# Retro

End-of-work-chunk retrospective. Output is a saved findings file plus a triaged action list ready to apply.

The point: convert ephemeral session learnings into durable artifacts (committed files, fixtures, CI gates) BEFORE `/handoff` writes the transcript. Things captured by /retro and acted on never become "things to mention in the handoff" — they become commits. Things captured but not acted on still survive on disk.

## Load when

| Reference | Load at step |
|---|---|
| [`references/anti-patterns.md`](references/anti-patterns.md) | Before drafting (Step 3) — guards against sycophancy, hallucinated coherence, recency bias |
| [`references/audience-taxonomy.md`](references/audience-taxonomy.md) | Step 2 — declaring the retro's audience |
| [`references/question-prompts.md`](references/question-prompts.md) | Step 3 — Q1-Q8 prompts and per-bullet tagging rules |
| [`references/failure-mode-checklist.md`](references/failure-mode-checklist.md) | Step 3, Q2 — checklist of LLM-session failure modes |
| [`references/output-templates.md`](references/output-templates.md) | Step 5 — file template, INDEX line format, triage table columns, Proposed Config Changes format |
| [`references/secrets-scrub.md`](references/secrets-scrub.md) | Step 5 — three-way gate before file write |

## When to run

- **End-of-chunk:** before `/handoff`. /retro's actions land first, then /handoff captures whatever's left. Trigger with /retro, "are we done?", "let's wrap up", "what did we miss?".
- **Skip** for tiny edits, single-question conversations, or anything where the commit message already says it all.

## Workflow

### Step 0 — Prerequisite + validity gates

Run prerequisite checks first:

```bash
git rev-parse --is-inside-work-tree   # must be a git repo
test -w .                              # cwd must be writable for ./retros/
gh auth status 2>/dev/null             # gh optional — skip PR view if absent
```

Abort with a specific message if any required check fails.

Then the validity gate: scan the conversation for evidence that a real workflow ran — specific skill invocations, tool calls beyond Read/status, gates passed, external side-effects (commits, PRs, Jira transitions, file writes). If you don't find any, **stop and say so** — don't fabricate. Wrong findings feed wrong skill edits, and the next session is worse, not better.

### Step 1 — Survey what shipped + recurrence check

Detect base first. If `git symbolic-ref refs/remotes/origin/HEAD` returns empty (detached HEAD, missing remote HEAD, fresh clone without remote), **abort** with "could not resolve origin/HEAD — pass base explicitly via env or arg." Do not let `git log ..HEAD` run with an empty `<base>`.

Once `<base>` is resolved, run these git/gh commands in a single batched tool call (they're independent):

```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'
git log <base>..HEAD --oneline
git diff <base>..HEAD --stat
git status --short
gh pr view --json number,url,title 2>/dev/null
```

Note quantitative session stats: commit count, files touched, redirections (user said "no, that's wrong" or similar), tool-call count. Q1 needs a denominator.

If `./retros/INDEX.md` exists, Read the last 2-3 entries via Grep on the file. Recurring patterns matter more than fresh ones — surfacing recurrence ("3rd retro flagging context-window pressure") is what turns retros into structural change. If a current finding matches a prior entry, mark it `(recurrent: <date>)`.

If zero commits since base AND working tree is clean AND no significant external side-effects, there's nothing to retro on — say so and stop.

### Step 2 — Declare audience

Read [`references/audience-taxonomy.md`](references/audience-taxonomy.md) and pick a primary (+ optional secondary). State at the top of the findings file. Same lesson lands differently for `next-agent` vs `skill-author` vs `future-me` vs `human-reviewer`.

### Step 3 — Findings (split, capped, tagged)

Read [`references/anti-patterns.md`](references/anti-patterns.md), [`references/question-prompts.md`](references/question-prompts.md), and [`references/failure-mode-checklist.md`](references/failure-mode-checklist.md).

Apply the three anti-pattern guards. Split findings into **process** and **technical** sections — they route to different homes (skill edits/runbooks vs passports/fixtures/code comments).

**Cap enforcement is preventive, not reactive.** While drafting each section: count bullets as you write. The moment a section reaches 3, stop adding. If more candidates exist, drop the weakest into a "what got cut" subsection with a one-line rationale per cut. **Do not write 5-6 bullets and trust Step 5.5 to catch the overflow** — by then the weaker bullets have already shaped the draft and skewed the triage. Step 5.5 is a backstop, not a primary control.

Tag every bullet per the rules in `question-prompts.md`. At least one finding (across Q1-Q5) must come from the first third of the session.

### Step 4 — Triage table

Translate Q1/Q2/Q4 actionable findings into the table format in [`references/output-templates.md`](references/output-templates.md). Order by leverage (highest payoff per minute first).

### Step 5 — Save first, then ask

**Save before asking for sign-off, not after.** A token-limit drop after the user pushes back loses everything.

**Location of record:** always `~/.claude/retros/`.

Retros are personal workflow archives — observations about how the user collaborates with AI, what skills need iteration, what failure modes recurred. They are *not* project documentation; PRs, ADRs, and runbooks handle the project-side stuff. Don't write them into any repo's `./retros/`, even when the session's work landed in that repo.

Cross-references to the project context (repo, branch, PR, commits) go in **YAML frontmatter** at the top of the retro file (see `references/output-templates.md`). Frontmatter is machine-readable so the user can later filter retros by repo or by skill ("show me my retros that touched waf-skill-review") during rewrites elsewhere.

Validate the slug before use: regex `^[a-z0-9][a-z0-9-]{1,40}$`, no `..`, no path separators. Derive from Q1's top finding (3-5 lowercased dash-joined tokens) or fall back to current branch name. Abort with a clear error on malformed input.

**Path confinement assert.** Compute the resolved write path (`realpath` or shell-equivalent) and confirm it stays under `~/.claude/retros/`. Abort if it escapes — defends against symlink games and slug-regex edge cases the regex alone wouldn't catch.

For same-day collisions (`~/.claude/retros/YYYY-MM-DD-<slug>.md` already exists): apply the three-branch decision tree in [`references/output-templates.md`](references/output-templates.md) — refine in place / new slug / stop.

Apply the secrets scrub from [`references/secrets-scrub.md`](references/secrets-scrub.md) **before write**. Default to redact. If clean, say so explicitly.

Write to `~/.claude/retros/YYYY-MM-DD-<slug>.md` using the template in [`references/output-templates.md`](references/output-templates.md), starting with YAML frontmatter capturing project cross-references (repo / branch / worktree / pr / commits / related_skills). After saving, append one line to `~/.claude/retros/INDEX.md` (create if absent) per the format in the same reference.

If the user pushes back during sign-off, **overwrite the same file** (with confirmation) — don't create a second one.

### Step 5.5 — Self-verify before reporting saved

Re-Read the saved file and Grep for:

- All required section headers present (`## Findings`, `### Process`, `### Technical`, `## Triage table`, `## Proposed Config Changes`).
- Every bullet under Findings carries `(cited:` or `(inferred)`.
- No section has more than 3 bullets unless a "what got cut" subsection follows.
- At least one bullet sourced from the first third of the session per the recency-bias guard.
- INDEX.md got the new line.

For each `(cited:<ref>)` referencing a commit hash or file:line, validate it: `git cat-file -e <sha>` for commits, `Read` for file paths. Drop or downgrade unverifiable cites to `(inferred)` and note the change.

If any check fails, fix before asking sign-off. Fail loudly with which check failed.

### Step 6 — Sign-off, then apply

Ask: **"Apply which? (all / specific items / none)"**

Parse "specific items" as a comma-separated list of triage table row indices (1-based) or short identifiers from the Lever column. Reject anything else with a clear error and re-prompt.

For each accepted item:

1. Make the file changes / add the fixture / write the test / wire the workflow.
2. Run the project's test suite. If red, **stop the entire loop** — surface output, don't commit, record state (see partial-state contract below).
3. Stage and commit related changes. **Ask explicitly: "commit + push? (yes/no)"** — separate confirmation per logical group. Never push without that gate.
4. If push fails (rejection, network), leave the commit local and surface the error.

**Partial-state contract.** If the loop aborts mid-flight (red tests, push failure, user interrupt), append a `## Partial application` section to the saved retro file listing exactly which items landed (file changes made? committed? pushed?) and which didn't. This becomes the resume point on next run — don't re-apply landed items, don't lose unlanded ones. The retro file is the source of truth for application state, not chat history.

If a CI workflow is added, mention that the first run may fail for org-policy reasons (e.g., GitHub Actions hosted runners disabled on Enterprise repos) and that's a config issue, not a workflow bug.

### Step 7 — Proposed Config Changes (don't edit other skills directly)

If the retro surfaces "we should change skill X" or "this rule belongs in the constitution," **do not edit those files in this session.** Reflection-as-edit skips review and cross-skill impact analysis. List them in the saved retro under **Proposed Config Changes** per the template in [`references/output-templates.md`](references/output-templates.md). That list becomes the input to a separate session or PR.

### Step 8 — Hand off coupling

If the user hasn't run `/handoff` yet and the session is wrapping up, suggest it: *"Want a /handoff next? The retro just landed durable findings, so the transcript stays focused on session-only context."*

When `/handoff` runs after `/retro`, it should link the saved retro path and not restate Q1-Q8 bullets — those live in the retro file. The handoff covers session-only context (in-flight tasks, environment state) that the retro doesn't capture. (`/handoff`'s SKILL.md must opt in for this to be enforced.)

Don't invoke `/handoff` automatically — it's a user choice.

## Rules

- **Honesty over politeness.** A retro that says "all good" wasted everyone's time. Stop early on a clean session — don't manufacture critiques.
- **Commit message decides what counts as "documented."** If a finding is fully captured in `git log`, don't list it under Q1.
- **Save before sign-off** (Step 5). Always.
- **Don't apply changes without confirmation** (Step 6). Per-action gates: write, apply, commit, push are separate prompts.
- **Hard cap of 3 per section** with "what got cut" if you have more.
- **At least one finding from the first third of the session** (recency-bias counterweight).
- **Every bullet tagged** — cited/inferred + strength + process/technical (+ skill if multi-agent).
- **One retro per chunk of work.** Multiple deliverables retro as a unit unless the user asks otherwise.
- **Don't update someone else's skill files directly.** Surface as Proposed Config Changes (Step 7); let the human own the edit.
- **Self-verify before reporting saved** (Step 5.5). The skill's caps and tag rules don't enforce themselves — the verification step does.
