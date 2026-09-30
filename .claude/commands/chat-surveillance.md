---
description: Daily chat surveillance digest from monitored Teams channels
---

You are running the **Chat Surveillance** routine.

## Steps

1. **Resolve repo root.** Try `git rev-parse --show-toplevel`. If the result does NOT end with `/ryan-claude-config`, fall back to `/Users/ryan.anderson/projects/pp/dx-prepass-meta/repos/ryan-claude-config`. Cache as `ROOT`.

2. **Determine the date.** If `$ARGUMENTS` is non-empty and matches `YYYY-MM-DD`, use it (backfill mode). Otherwise `date +%Y-%m-%d`. Cache as `DATE`.

3. **Window.** 24 hours, except 72 hours on Monday.

4. **Read these three files from `ROOT`** in order:
   - `architectural-lens.md` — the filter.
   - `routines/chat-surveillance/config.yaml` — channels, exclusions, privacy guard (`include_dms: false`).
   - `routines/chat-surveillance/prompt.md` — your full instructions.

5. **Privacy guard — non-negotiable.** Read only the channels listed in `channels:`. Never read 1:1 DMs regardless of access. If the config has no channels set, stop and reply asking the user to populate `channels:` before running.

6. **Fetch chat data** via available Microsoft 365 / Teams tooling. If no M365 MCP server is connected, write a "messages unreachable — connect a Microsoft 365 connector at claude.ai/customize/connectors" note as the digest body and skip the rest.

7. **Surface signals** per the prompt's seven-category list and the lens. Be stingy — better 3 strong threads than 10 weak ones. Quote ≤15 words from any single message.

8. **Write the digest** to `ROOT/digests/chat-surveillance/DATE.md`. Header is `# Chat Surveillance — DATE`.

9. **Commit and push:**
   ```
   git -C ROOT add digests/chat-surveillance/DATE.md
   git -C ROOT commit -m "digest(chat): DATE"
   git -C ROOT push origin main
   ```

10. **Reply** with: a one-line confirmation, the top item from `🔥 HOT THREADS`, and the GitHub URL of the committed file.
