# Output Template — Session Rundown

This template defines the branded structure of the rendered report. Every rundown produces this shape — variations are content, not structure.

Placeholders are written as `{{like_this}}` and resolved at render time.

---

## Required structural envelope

```markdown
# 🎪 Session Rundown — {{date}}

> "Many threads, one mind — keep them all warm." — Juggler's principle

Greetings, multi-thread maestros! Here's where each open Claude session left off — sourced from session metadata and linked worktrees, cross-checked for duplicates and merged-PR cleanup candidates.

**At a glance:** {{n}} open sessions · {{n_today}} today · {{n_this_week}} this week · {{n_stale}} stale (>7d) · {{n_flagged}} flagged for cleanup.

---

## 🪢 Threads in Play

> "A session unfinished is a question pending." — Practitioner's note

| Session | Repo / Worktree | Last activity | State | Outstanding |
|---|---|---|---|---|
{{#each sessions}}
| {{title_truncated_50}} | {{repo_short}} / `{{worktree_short}}` | {{last_activity_relative}} | {{state_glyph}} | {{outstanding}} |
{{/each}}

**Each row is a context switch you've already paid for. Spend the second one wisely.**

---

## 🪶 Loose Ends

> "Closing well costs less than closing late." — Operations adage

{{#if flagged}}
{{#each flagged}}
- **{{kind}}** — {{note}}{{#if candidates}} _Candidates: {{candidates_with_overlap}}_{{/if}} _Move: `{{suggested_move}}` · session: `{{session_id_short}}`_
{{/each}}
{{else}}
_All threads in healthy state — no merged-PR sessions, no duplicates, no cold-with-dirty-tree._
{{/if}}

**Loose ends compound — one un-archived session today is three to triage by Friday.**

---

## 🧭 Next Moves

> "Pick the smallest finishable thread." — Juggler's rule

1. {{move_1}}
2. {{move_2}}
3. {{move_3}}

---

## 📎 Rundown Metadata

| Field | Value |
|---|---|
| Generated | {{timestamp_iso}} |
| Limit | {{limit}} |
| Include archived | {{include_archived}} |
| Sources | sessions: ✓ · worktrees: ✓ |

---

**Threads tallied. Direction is yours.**
```

---

## Rendering rules

1. **Quote placement is non-negotiable.** Each `##` section opens with a quote block on the line immediately after the header, with one blank line before the prose begins.
2. **Emoji per section is fixed** — 🎪 (header) 🪢 🪶 🧭 📎. Do not substitute.
3. **Empty sections still render** — show the italic `_no items_` sentinel rather than omitting.
4. **Bold pull-statements** appear at the end of each major section. They are the report's memorable anchors.
5. **Closing line is literal:** `**Threads tallied. Direction is yours.**` — do not paraphrase.
6. **No corporate jargon.** Plain English; replace "leverage" with "use," "circle back" with "revisit," etc.
7. **State glyphs (closed enumeration):** `🟢 active` (today + no flags), `🟡 idle` (this-week + no flags), `🔴 cold` (stale), `✅ merged` (`prState == MERGED`), `⚪ archived` (only when `--include-archived`).
8. **Title truncation:** if a session title exceeds 50 chars, truncate to 47 + `…`.
9. **Worktree-name short form:** strip the trailing 6-char hash (e.g. `dreamy-visvesvaraya-1bf4cf` → `dreamy-visvesvaraya`).
10. **Candidates with overlap evidence:** for `pick one, archive other` flags, render both candidates as `<id_a> / <id_b> (overlap: "<shared substring>")` so the developer can decide which to keep.
11. **Idle-time relative format:** `~Nh ago` for < 24h, `~Nd ago` for ≥ 24h. Round down. Use the same `now` reference across all rows.

## Next-Move selection algorithm

The "Next Moves" section pulls exactly three items from the flagged list:

1. **First move** — the first `archive` (merged-PR cleanup is the cheapest win). If none, the first `commit or stash` (recoverable lost-work risk).
2. **Second move** — the first `commit or stash` not already taken in slot 1. If none, the first `pick one, archive other`.
3. **Third move** — the first `pick one, archive other` not already taken. If none, the most-stale `OPEN` PR session.

If fewer than three flagged sessions exist, fill remaining slots with `_No additional moves this run._`.

Phrase each move as an observation: `Consider {action} on {target} — {reason}.` Never as an imperative.
