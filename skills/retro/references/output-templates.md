# Output templates

## Retro file: `~/.claude/retros/YYYY-MM-DD-<slug>.md`

Retros are personal workflow archives, always written to user scope. Project cross-references go in YAML frontmatter — machine-readable, so future filtering ("retros that touched waf-skill-review", "retros from the LWAF work") is cheap.

```markdown
---
date: YYYY-MM-DD
slug: <slug>
audience: [<primary>, <secondary>]
repo: <basename of git rev-parse --show-toplevel, or null if no git>
branch: <git branch --show-current, or null>
worktree: <linked-worktree name if cwd is one, else null>
pr: <PR number if `gh pr view` returned one, else null>
commits: <integer count of commits since base>
related_skills: [<list of skills exercised or discussed this session>]
---

# Retro: <slug>

**Session stats:** N files / N tool calls / N redirections
**Recurrence:** <link to prior retros that flagged related patterns, or "none">

## Findings

### Process
[Q1-Q8 with tags, capped at 3 per question; "what got cut" if more]

### Technical
[Q1-Q8 with tags, capped at 3 per question; "what got cut" if more]

## Triage table

| Lever | Effort | Payoff | Audience | Confidence |
|---|---|---|---|---|
| <concrete action> | <30s / 5m / 20m / 1h> | <one-sentence why> | <who acts> | <cited\|inferred + strength> |

## Proposed Config Changes
[skill / passport / constitution edits — see Proposed Config Changes section below]
```

The body's `Session stats` line drops `N commits` (it's in frontmatter) and the `Date / Audience` lines (also frontmatter). Avoid restating frontmatter in the body.

Slug derivation: first 3-5 lowercased dash-joined tokens from Q1's top finding; fallback to current branch name. Reject if it contains `/`, `..`, or non-`[a-z0-9-]` chars — abort with clear error.

## Same-day re-run decision tree

If `./retros/YYYY-MM-DD-<slug>.md` already exists at write time:

1. **Same chunk of work, user pushed back on findings** → overwrite the same file (with confirmation). This is the path Step 5 of SKILL.md describes.
2. **New chunk of work since the prior retro** (new commits since the file's mtime, or user explicitly says "new chunk") → derive a new slug from this chunk's Q1 top finding and write to `YYYY-MM-DD-<new-slug>.md`. Don't append; new chunk = new file.
3. **Same chunk, no pushback, just re-running** → stop with "today's retro already exists at <path>; nothing new to capture." Don't regenerate.

## INDEX line

After saving, append one line to `./retros/INDEX.md` (create the file if it doesn't exist):

```
- YYYY-MM-DD <slug> | top: <one-line top finding> | confidence: <cited|inferred> | audience: <primary>
```

On Step 1 recurrence check, read the last 2-3 entries from this file. If a current finding matches a prior entry, mark it `(recurrent: <date>)` in the body.

## Triage table columns

| Column | Content |
|---|---|
| Lever | Concrete action, no hedging. "Add Step 0 prereq check" — not "consider improving validation." |
| Effort | 30s / 5m / 20m / 1h. Honest — "5m" includes running the tests; "20m" can expand to 40. Never call something "trivial" — that's a reason to do it, not a description. |
| Payoff | One sentence on why this is worth doing. |
| Audience | Who acts: next-agent / skill-author / future-me / human-reviewer. |
| Confidence | `cited` or `inferred` + strength score 1-5. |

Order rows by leverage (high payoff per minute first).

## Closing report (chat output after Step 6/7)

After Step 6 finishes applying and Step 7 is staged, emit one structured block to chat. The user should be able to skim this and know exactly what just happened without scrolling the transcript.

```markdown
**Retro saved:** ./retros/YYYY-MM-DD-<slug>.md
**INDEX line:** appended (or "INDEX created")
**Audience:** <primary> [+ <secondary>]
**Stats:** N commits / N files / N tool calls / N redirections
**Bullets:** Q1 P:N T:N | Q2 P:N T:N | ... | Q8 P:N T:N (P=process, T=technical; "what got cut" inline if any)
**Redactions:** <count, or "none">
**Recurrence hits:** <count, with dates>
**Applied:** <list of accepted triage items, with commit shas if pushed>
**Deferred:** <list of triage items not accepted>
**Proposed Config Changes:** <count> entries staged for separate session
**Suggested next:** /handoff (and link to the retro path)
```

If a section has zero entries, write `none` rather than omitting the line — readers should be able to count fields, not infer from absence.

## Proposed Config Changes section

Format for each entry:

```
- Target: skills/<name>/SKILL.md (or passports/X.md, constitution/Y.md, etc.)
- What: <exact wording or behavioral change>
- Why: <session evidence — cite the moment>
- Confidence: cited | inferred (strength 1-5)
```

These are proposals only. The retro must not edit the target files in this session — see Step 7 in SKILL.md for the rationale (reflection-as-edit skips review and cross-skill impact analysis).
