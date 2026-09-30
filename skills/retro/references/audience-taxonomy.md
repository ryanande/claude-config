# Audience taxonomy

Declare audience at the top of the retro file. The same lesson lands very differently depending on reader.

## Audiences

| Audience | Reader | Tone |
|---|---|---|
| `next-agent` | A fresh agent picking up this branch tomorrow | Imperative, terse, cite paths and lines |
| `skill-author` | The person maintaining the skills that ran in this session | Behavior gaps, prompts that misfired, contract violations |
| `future-me` | Same human, in a week or month | Decisions and rationale, not mechanics |
| `human-reviewer` | Manager / teammate skimming for status | Outcomes, blockers, what's at risk |

## Choosing audience

Most retros have one **primary** + one **secondary**. Per-finding overrides are allowed (`→skill-author` on a bullet whose primary audience is `next-agent`).

Decision:

- Multi-skill session that hit friction with one of the skills → primary = `skill-author`
- Hand-off coming next or branch will be picked up tomorrow → primary = `next-agent`
- Cross-week or cross-month gap before continuation → primary = `future-me`
- Stakeholder check-in pending → secondary = `human-reviewer` (rarely primary)

## Why this matters

Writing for an undifferentiated reader produces vague findings that serve none of them well. The bullets oscillate between agent instructions ("re-read the spec before writing tests") and human takeaways ("we should formalize the spec process") and end up landing nowhere. Naming the audience disciplines the wording.
