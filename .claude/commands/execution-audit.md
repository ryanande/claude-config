---
description: Inventory every in-flight effort across memory, Jira, GitHub, and local worktrees; render a PrePass-branded execution audit
---

You are running the **Execution Audit** skill.

## How to invoke

Resolve and execute the skill at `<repo-root>/skills/execution-audit/SKILL.md`. Steps:

1. **Resolve repo root.** Try `git rev-parse --show-toplevel`. If the result does not end with `/ryan-claude-config`, fall back to `/Users/ryan.anderson/projects/pp/dx-prepass-meta/repos/ryan-claude-config`. Cache as `ROOT`.

2. **Read** `ROOT/skills/execution-audit/SKILL.md` and follow the workflow exactly. The skill's typed-input contract accepts an optional argument string in `$ARGUMENTS` of the form:

   ```
   [--scope all|jira|github|local|memory] [--org <org>] [--meta-root <path>] [--out <path>] [--idle-days <n>] [--pr-idle-days <n>] [--allow-path <prefix>]
   ```

   Pass these through to the skill's Step 0a argument parsing. Apply defaults for anything unspecified per the SKILL.md inputs table.

3. **Execute** Steps 0 → 5 of the SKILL.md workflow. Honor every operating constraint, especially: the output-path allowlist, secret/PII scrub at Step 4a, render validation at Step 4b, and atomic write at Step 4c.

4. **Reply** with: the path to the rendered report (`<output_path>`), `findings_count`, `redaction_count` (with banner if non-zero), and the top three friction findings inline. End with the literal sentence `**Inventory done. Direction is yours.**`.

## Notes

- This is a SKILL, not a routine. The shape (`skills/<name>/SKILL.md` + `references/`) is intentional and differs from `routines/<name>/{prompt,config,runner}` so the skill can graduate to dx-aicentral without rework.
- This command is the discoverability surface; the workflow contract is owned by SKILL.md. Do not duplicate workflow text here.
