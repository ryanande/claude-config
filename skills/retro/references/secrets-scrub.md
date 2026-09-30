# Secrets scrub procedure

Before writing the retro file to disk, scan the body for sensitive content.

## What to scan for

- API keys, tokens, JWTs, OAuth secrets
- Connection strings (database URLs with embedded passwords, Azure/AWS connection strings)
- `.env` paths or contents quoted from tool output
- PII: emails, phone numbers, names of customers, employee IDs
- Internal URLs with embedded auth (e.g., `https://user:pass@host`)
- Customer data (account numbers, transaction IDs from production)
- Verbatim quotes from `gh pr view`, Jira payloads, MCP tool responses, error logs — these are the most common leak vectors
- Anything quoted from `git log` of a private repo if the retro might be checked into a public one

## Three-way gate per hit

For each match, apply one of:

- **Redact (default).** Replace the value with `[REDACTED]`. Continue.
- **Override.** User explicitly confirms it's safe to persist (rare — e.g., a public issue ID that looks like a key, a username already in the repo).
- **Abort.** Surface the find and stop. User decides what to do next — most often, they'll redact and resume.

Default to redact. The retro file is durable — once a secret is written, clawing it back is harder than never writing it. Even if the retro stays local, it might get fed into another skill, committed by accident, or read months later.

## What to do if no secrets found

Say so in the chat ("scrubbed retro body for tokens/keys/PII/connection strings — none found") and continue. Silence is ambiguous; an explicit clean signal is what the user needs.

## Why scrub *before* save, not after

A token-limit drop or interrupt after writing means the secret is on disk and your scrub step never ran. Scrub-then-save means the persistent artifact is the safe one.
