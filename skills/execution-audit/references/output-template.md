# Output Template — Execution Audit

This template defines the branded structure of the rendered report. Every audit produces this shape — variations are content, not structure.

Placeholders are written as `{{like_this}}` and resolved at render time.

---

## Required structural envelope

```markdown
# 🧭 Execution Audit — {{date_local}}

> "You cannot steer what you have not surveyed." — Operations adage

Greetings, ground-truth seekers! Here's where the work actually stands today — sourced from memory, Jira, GitHub, and your local worktrees, cross-checked against each other, and flagged where reality and intent have drifted apart.

**At a glance:** {{n_initiatives}} strategic initiatives · {{n_jira_open}} open Jira tickets · {{n_prs_open}} open PRs · {{n_worktrees}} active worktrees · {{n_findings}} findings.

---

## 🎯 Strategic Stakes

> "Initiative without inventory is improvisation." — PrePass Engineering Principles

These are the multi-week bets currently in your memory. Each one is a thread you've explicitly chosen to pull.

{{#each initiatives}}
### {{name}}
- **Status:** {{status}}{{#if memory_drift}} _(memory drift: {{memory_drift}})_{{/if}}
- **Why it exists:** {{why}}
- **Live linkage:** {{linked_jira | "—"}} · {{linked_pr | "—"}}
- **Last memory update:** {{origin_date}}
{{/each}}

{{#if no_initiatives}}
_No strategic initiatives currently in memory. Either you're between bets, or memory hasn't captured the bet yet._
{{/if}}

**Strategic initiatives are the spine — everything below is the limbs.**

---

## 🚦 Tickets in Transit

> "A ticket open is a promise outstanding." — Operations adage

Open Jira work assigned to you, grouped by status and ordered most-recent-first inside each group.

### In Progress ({{n_in_progress}})
{{#each in_progress}}
- [{{key}}]({{url}}) — {{summary}} _{{type}}, P-{{priority}}{{#if parent}}, parent {{parent_key}}{{/if}}, updated {{updated_date}}{{#if linked_pr}}, PR {{linked_pr_md}}{{/if}}_
{{/each}}

### Ready To Test ({{n_ready_to_test}})
{{#each ready_to_test}}
- [{{key}}]({{url}}) — {{summary}} _{{type}}, P-{{priority}}{{#if linked_pr}}, PR {{linked_pr_md}}{{/if}}_
{{/each}}

### To Do — clustered by epic ({{n_to_do}})
{{#each to_do_clusters}}
**{{epic_label}}** ({{children_count}} child{{#if children_plural}}ren{{/if}})
{{#each children}}
  - [{{key}}]({{url}}) — {{summary}} _P-{{priority}}, idle {{idle_days}}d_
{{/each}}

{{/each}}

{{#if jira_unavailable}}
_⚠ Jira unavailable this run ({{jira_error}}) — ticket data is empty for this audit._
{{/if}}

**A To-Do under a Ready-to-Test parent is a bookkeeping bug, not a backlog item.**

---

## 🌊 Pull-Request Pipeline

> "An open pull request is a half-finished sentence." — Engineering wisdom

PRs you authored that are still open across {{org}}.

| # | Repo | Title | Linked Jira | Idle | Status |
|---|---|---|---|---|---|
{{#each open_prs}}
| [{{number}}]({{url}}) | {{repo}} | {{title_truncated}} | {{linked_jira_md | "—"}} | {{idle_days}}d | {{review_status}}{{#if is_draft}} (draft){{/if}} |
{{/each}}

{{#if github_unavailable}}
_⚠ GitHub unavailable this run ({{github_error}}) — PR data is empty for this audit._
{{/if}}

**A PR idle past {{pr_idle_days}} days is signal — review missing, conflicts brewing, or the work has gone cold.**

---

## 🧹 Local Litter

> "Tidiness is a tax on future-you." — Carpenter's law

Worktrees and branches sitting on disk in `{{meta_root}}`.

### Active worktrees ({{n_worktrees}})
{{#each worktrees}}
- `{{name}}` — branch `{{branch}}`, {{dirty_count}} dirty files, last commit {{last_commit_relative}} ({{last_commit_subject}}){{#if linked_jira}}, linked {{linked_jira_md}}{{/if}}
{{/each}}

### Stale local branches ({{n_stale_branches}})
{{#each stale_branches}}
- `{{branch}}` in `{{repo}}` — last commit {{last_commit_relative}}, no upstream
{{/each}}

{{#if no_clutter}}
_Clean — no abandoned worktrees, no orphan local branches._
{{/if}}

**Worktrees are cheap to create, expensive to ignore.**

---

## ⚠ Friction Findings

> "What gets measured stops drifting." — Process axiom

Auto-flagged anomalies. Each finding is an observation, not an order — context that helps you choose where attention is most overdue.

{{#if findings}}
{{#each findings_by_severity}}
### {{severity_label}} ({{count}})
{{#each items}}
- **{{category_label}}** — {{note}} _Target: {{target}}_
{{/each}}

{{/each}}
{{else}}
_Zero findings. Either everything is genuinely on-rails, or the audit's rule set is undertuned. Both are worth noticing._
{{/if}}

**Findings flagged ≠ work to do. Findings flagged = signals to weigh.**

---

## 🧭 Next-Step Nudges

> "Awareness compounds. Action follows." — Practitioner's note

Three observations, ranked by friction-cost not by judgment-call. Read them, then decide.

1. {{nudge_1}}
2. {{nudge_2}}
3. {{nudge_3}}

---

## 📎 Audit Metadata

| Field | Value |
|---|---|
| Generated | {{timestamp_iso}} |
| Scope | {{scope}} |
| Jira idle threshold | {{jira_idle_days}} days |
| PR idle threshold | {{pr_idle_days}} days |
| Sources | memory: {{memory_status}} · jira: {{jira_status}} · github: {{github_status}} · local: {{local_status}} |

---

**Inventory done. Direction is yours.**
```

---

## Rendering rules

1. **Quote placement is non-negotiable.** Each `##` section opens with a quote block on the line immediately after the header, with one blank line before the prose begins.
2. **Emoji per section is fixed** — 🎯 🚦 🌊 🧹 ⚠ 🧭 📎. Do not substitute, even if the section has zero items.
3. **Empty sections still render** — show the italic `_no items_` sentinel rather than omitting the section. The audit's value is consistency.
4. **Bold pull-statements appear at the end of each major section** (the alliterative one-liners). They are the report's memorable anchors.
5. **The closing line is literal:** `**Inventory done. Direction is yours.**` — do not paraphrase.
6. **No corporate jargon.** Replace "leverage" with "use," "circle back" with "revisit," "align on" with "agree on," "stakeholder" with the actual person or team.
7. **Truncation rule for PR titles:** if a title exceeds 60 chars, truncate to 57 chars + `…`. Always preserve the leading `feat(...)`, `fix(...)`, `chore(...)` prefix verbatim.
8. **Idle-days computation:** integer days between `now` and `updatedAt` (UTC). Round down. Always render as `{{n}}d`.
9. **Memory drift annotation format:** `_(memory drift: was {{old_status}}, now {{new_status}})_` — italicized, parenthesized, lowercase prefix.
10. **Severity labels:** `🔴 High` · `🟡 Medium` · `🟢 Low`. No other glyphs.

## Nudge selection algorithm (Step 5 input)

The "Next-Step Nudges" section pulls exactly three items from the findings list:

1. **First nudge** — the highest-severity `skew` finding (epic/child status mismatch, memory drift). If none, the highest-severity `staleness` finding.
2. **Second nudge** — the highest-priority Jira ticket (P-High > P-Medium > P-Low) that has been idle longest.
3. **Third nudge** — the most-stale PR or worktree with a linked Jira ticket.

If fewer than three findings exist, fill remaining slots with `_No additional nudges this run._`.

Phrase each nudge as an observation: "Consider {action} on {target} — {reason}." Never as an imperative.
