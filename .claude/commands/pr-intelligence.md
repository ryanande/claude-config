---
description: Daily PR intelligence digest, filtered through the architectural lens
---

You are running the **PR Intelligence** routine.

## Steps

1. **Resolve repo root.** Try `git rev-parse --show-toplevel`. If the result does NOT end with `/ryan-claude-config`, fall back to `/Users/ryan.anderson/projects/pp/dx-prepass-meta/repos/ryan-claude-config`. Cache as `ROOT`.

2. **Determine the date.** If `$ARGUMENTS` is non-empty and matches `YYYY-MM-DD`, use it (backfill mode). Otherwise `date +%Y-%m-%d`. Cache as `DATE`.

3. **Window.** 24 hours, except 72 hours if today is Monday (`date +%u` returns `1`).

4. **Read these three files from `ROOT`** in order:
   - `architectural-lens.md` — the filter; every judgment is grounded here.
   - `routines/pr-intelligence/config.yaml` — scope and exclusions.
   - `routines/pr-intelligence/prompt.md` — your full instructions.

5. **Enumerate PRs.** Use GitHub tools to list PRs across the PrePass org per the config — opened, updated, or merged in the window. Prefer `mcp__MCP_DOCKER__list_pull_requests`; fall back to `gh` CLI (`gh pr list --search "is:pr org:PrePass updated:>YYYY-MM-DD" --json …`). Apply `exclude_repos`, `exclude_authors`, and `down_rank_repos` from the config.

6. **Filter and rank** following the prompt's evaluation criteria and the lens's strategic priorities (G1–G5). Maximum 10 items total across the three sections.

7. **Write the digest** to `ROOT/digests/pr-intelligence/DATE.md`. Create the directory if missing. Header is `# PR Intelligence — DATE`.

8. **Commit and push:**
   ```
   git -C ROOT add digests/pr-intelligence/DATE.md
   git -C ROOT commit -m "digest(pr): DATE"
   git -C ROOT push origin main
   ```

9. **Reply** with: a one-line confirmation, the top item from each of `🚨 NEEDS MY EYES` / `📈 OPPORTUNITIES` / `📋 FYI`, and the GitHub URL of the committed file (`https://github.com/Ryan-Anderson_prepass/claude-config/blob/main/digests/pr-intelligence/DATE.md`).
