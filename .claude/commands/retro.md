---
description: End-of-work-chunk retrospective — what got lost, what worked, what surprised — saved to ~/.claude/retros/ before /handoff
---

You are running the **Retro** skill.

## How to invoke

1. **Resolve repo root.** Try `git rev-parse --show-toplevel`. If the result does not end with `/ryan-claude-config`, fall back to `/Users/ryan.anderson/projects/pp/dx-prepass-meta/repos/ryan-claude-config`. Cache as `ROOT`.

2. **Read** `ROOT/skills/retro/SKILL.md` and follow the workflow exactly. Retro takes no typed arguments — `$ARGUMENTS` is informational only and may carry an audience hint or scope note that you can pass into Step 2.

3. **Execute** Steps 0 → 8 of the SKILL.md workflow. Honor every operating constraint, especially: the validity gate at Step 0 (don't fabricate findings on a thin session), the 3-bullet cap per section, the path confinement on `~/.claude/retros/`, the secrets scrub before write, and the per-action confirmation gates (write / apply / commit / push) at Step 6.

4. **Reply** with: audience declaration, finding counts (process/technical + any "what got cut"), triage row count, the saved retro file path and INDEX.md update, and any Proposed Config Changes. If Step 8 applies, suggest `/handoff` next.

## Notes

- This is a SKILL, not a routine. Same shape as `execution-audit` and `session-rundown`.
- Retros are personal workflow archives — they live in `~/.claude/retros/`, never in a repo's `./retros/`.
- Designed to run **before** `/handoff` so durable findings land first and the handoff transcript stays focused on session-only context.
