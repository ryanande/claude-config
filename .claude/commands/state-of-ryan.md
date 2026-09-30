---
description: Daily personal-WIP triage — ranks your worktrees, PRs, and tickets as advance / park / kill
---

You are running the **State-of-Ryan** routine.

## Steps

1. **Resolve repo root.** Try `git rev-parse --show-toplevel`. If the result does NOT end with `/ryan-claude-config`, fall back to `/Users/ryan.anderson/projects/pp/dx-prepass-meta/repos/ryan-claude-config`. Cache as `ROOT`.

2. **Determine the date.** If `$ARGUMENTS` is non-empty and matches `YYYY-MM-DD`, use it (backfill mode). Otherwise `date +%Y-%m-%d`. Cache as `DATE`.

3. **Read these two files from `ROOT`** in order:
   - `routines/state-of-ryan/config.yaml` — globs, thresholds, caps.
   - `routines/state-of-ryan/prompt.md` — your full instructions.

4. **Walk worktrees.** Expand each pattern in `worktree_globs`. For each worktree directory, capture: path, current branch, last commit timestamp, last commit subject. Skip worktrees whose `.git` file points to a stale gitdir (deleted worktree directories).

5. **Pull authored PRs.** Run:
   ```
   gh pr list --author @me --search "org:PrePass" --state open \
     --json number,title,url,headRepository,headRefName,reviewDecision,updatedAt,isDraft,mergeable
   ```

6. **Pull assigned tickets.** Use the Atlassian MCP tool `mcp__13d891ff-6397-44e0-8851-38d30663c8db__searchJiraIssuesUsingJql` with JQL `assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC` and a reasonable page size (50 is plenty).

7. **Cross-reference and bucket** per the prompt. Each effort gets one row in one of: `ADVANCE` / `PARK` / `ZOMBIE` / `AWAITING`. Apply the per-section caps from config.

8. **Write the digest** to `ROOT/digests/state-of-ryan/DATE.md`. Create the directory if missing. Header is `# State-of-Ryan — DATE`.

9. **Commit and push:**
   ```
   git -C ROOT add digests/state-of-ryan/DATE.md
   git -C ROOT commit -m "digest(sor): DATE"
   git -C ROOT push origin main
   ```

10. **Reply** with: a one-line confirmation, the WIP summary line (e.g. `7 active · cap 3 · 2 zombies · 4 awaiting`), the 🎯 TODAY section verbatim, and the GitHub URL of the committed file (`https://github.com/Ryan-Anderson_prepass/claude-config/blob/main/digests/state-of-ryan/DATE.md`).

## Failure modes

- **No PRs / no tickets reachable** (gh not authed, Atlassian MCP not connected): write the digest with whatever buckets you have, and add a `> note: <source> unreachable` line at the top. Don't bail.
- **Empty plate.** If all four buckets are empty, write a one-line digest (`Empty plate. Nothing to triage.`) and still commit — the empty days are the record you want.
