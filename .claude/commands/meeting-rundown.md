---
description: Daily meeting rundown digest from yesterday's Teams meetings
---

You are running the **Meeting Rundown** routine.

## Steps

1. **Resolve repo root.** Try `git rev-parse --show-toplevel`. If the result does NOT end with `/ryan-claude-config`, fall back to `/Users/ryan.anderson/projects/pp/dx-prepass-meta/repos/ryan-claude-config`. Cache as `ROOT`.

2. **Determine the date.** If `$ARGUMENTS` is non-empty and matches `YYYY-MM-DD`, use it (backfill mode). Otherwise `date +%Y-%m-%d`. Cache as `DATE`.

3. **Coverage.** "Prior business day" — yesterday for Tue–Fri, Friday + weekend for Monday.

4. **Read these three files from `ROOT`** in order:
   - `architectural-lens.md` — the filter.
   - `routines/meeting-rundown/config.yaml` — categories, exclusions.
   - `routines/meeting-rundown/prompt.md` — your full instructions.

5. **Fetch meeting data.** Use available Microsoft 365 / Teams tooling to read meeting transcripts and recordings the user has access to, filtered by the categories in the config. If no M365 MCP server is connected, write a clear "transcripts unreachable — connect a Microsoft 365 connector at claude.ai/customize/connectors" note as the digest body and skip the rest.

6. **Extract and synthesize** per the prompt's per-meeting extraction list and the lens. Skip meetings with no architectural content. List any meetings where transcripts are missing under "missing transcripts" at the end.

7. **Write the digest** to `ROOT/digests/meeting-rundown/DATE.md`. Header is `# Meeting Rundown — DATE`.

8. **Commit and push:**
   ```
   git -C ROOT add digests/meeting-rundown/DATE.md
   git -C ROOT commit -m "digest(meeting): DATE"
   git -C ROOT push origin main
   ```

9. **Reply** with: a one-line confirmation, the TL;DR's first three bullets, and the GitHub URL of the committed file.
