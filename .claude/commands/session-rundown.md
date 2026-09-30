---
description: Roundup every open Claude Code session with what's outstanding and a suggested next move
---

You are running the **Session Rundown** skill.

## How to invoke

1. **Resolve repo root.** Try `git rev-parse --show-toplevel`. If the result does not end with `/ryan-claude-config`, fall back to `/Users/ryan.anderson/projects/pp/dx-prepass-meta/repos/ryan-claude-config`. Cache as `ROOT`.

2. **Read** `ROOT/skills/session-rundown/SKILL.md` and follow the workflow exactly. The skill's typed-input contract accepts an optional argument string in `$ARGUMENTS` of the form:

   ```
   [--limit <n>] [--include-archived] [--out <path>] [--allow-path <prefix>]
   ```

   Pass these through to Step 0a argument parsing. Apply defaults per the SKILL.md inputs table.

3. **Execute** Steps 0 → 4 of the SKILL.md workflow. Honor every operating constraint, especially: the output-path allowlist, secret/PII scrub at Step 3a, render validation at Step 3b, and atomic write at Step 3c when `--out` is supplied.

4. **Reply** with: `sessions_count`, `flagged_count`, `redaction_count` (with banner if non-zero), the three Next Moves inline, and the report path if `--out` was set. End with the literal sentence `**Threads tallied. Direction is yours.**`.

## Notes

- This is a SKILL, not a routine. Same shape as `execution-audit`.
- Read-only against `mcp__ccd_session_mgmt`; the skill never archives. Archive commands are surfaced as suggested next moves; the developer runs them.
