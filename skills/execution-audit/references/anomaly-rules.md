# Anomaly Rules — Execution Audit

The set of rules that produce the "Friction Findings" section. Each rule has a stable ID, a category, a severity, an evaluation, and a note template. Rules are evaluated independently — one source of data can produce multiple findings.

Severity scale:
- **🔴 High** — actively misleading state (e.g., a closed-out parent with open children) or P-High work going cold. Costs compound.
- **🟡 Medium** — staleness, drift, or clutter that hasn't caused harm yet but is on the path to it.
- **🟢 Low** — minor housekeeping. Surface for visibility, not action.

Category labels: `skew` · `staleness` · `priority` · `clutter` · `drift`.

## Canonical finding shape

Every finding emitted by every rule conforms to this structure. Step 3 produces a list of these; Step 4 renders them in the Friction Findings section.

```yaml
severity: high | medium | low
category: skew | staleness | priority | clutter | drift
target: <jira-key | pr-url | worktree-path | memory-name>
note: "<one-line human-readable explanation>"
rule_id: EA-NNN
```

`rule_id` is required so the renderer can group multiple findings that share an underlying rule, and so finding-count regressions across runs can be attributed to specific rules.

---

## Rule registry

### EA-001 — Epic/child status skew (skew, 🔴 High)

**Evaluation:** For every open Jira ticket whose `parent.status` is `Done` or `Ready To Test`, AND whose own `status` is `To Do` or `In Progress`.

**Note:** `Sub-ticket {{key}} is "{{child_status}}" but parent {{parent_key}} is "{{parent_status}}". Either the sub-ticket is genuinely outstanding (parent should not be closed) or it's covered by the parent's PR (transition or close it).`

**Target:** `{{key}}`.

---

### EA-002 — High-priority idle (priority, 🔴 High)

**Evaluation:** Any open Jira ticket with `priority = High` AND `(now - updated) > 21 days`.

**Note:** `P-High {{key}} idle {{idle_days}}d ({{summary}}) — either de-prioritize, schedule, or assign to someone else.`

**Target:** `{{key}}`.

---

### EA-003 — Memory cites a closed ticket (drift, 🟡 Medium)

**Evaluation:** Any `project_*.md` whose body cites an `AT-\d+` key whose live status is `Done` AND the memory's `originSessionId` is older than 7 days. (Younger than 7 days is fresh enough to ignore — the user may not have synced memory yet.)

**Note:** `Memory "{{memory_name}}" cites {{ticket_key}} which is now Done. Consider updating or removing the memory entry.`

**Target:** `{{memory_name}}`.

---

### EA-004 — Memory cites a status that has changed (drift, 🟡 Medium)

**Evaluation:** Any `project_*.md` containing a phrase like `Status: <X>` or `status: <X>` followed by an `AT-\d+`, where `<X>` does not match the live status of the ticket. (Annotate inline in Strategic Stakes regardless; flag here only when severity is Medium+.)

**Note:** `Memory "{{memory_name}}" reports {{ticket_key}} as "{{recorded_status}}" but live status is "{{live_status}}".`

**Target:** `{{memory_name}}`.

---

### EA-005 — PR idle past threshold (staleness, 🟡 Medium)

**Evaluation:** Any open PR with `(now - updatedAt) > pr_idle_days` (default 7).

**Note:** `PR {{repo}}#{{number}} idle {{idle_days}}d — review missing, conflicts brewing, or work has gone cold.`

**Target:** `{{pr_url}}`.

**Severity bump:** if PR has `reviewDecision = CHANGES_REQUESTED` and is idle past threshold, severity escalates to 🔴 High and the note becomes: `PR {{repo}}#{{number}} has changes requested and is {{idle_days}}d idle — reviewer is blocked on you.`

---

### EA-006 — Worktree without recent activity (clutter, 🟢 Low)

**Evaluation:** Any worktree under `<meta_root>/.claude/worktrees/` with `(now - last_commit) > 7 days` AND only submodule pointer changes in `git status` (i.e., not real in-progress work).

**Note:** `Worktree {{name}} idle {{idle_days}}d on branch {{branch}} — only submodule pointer changes. Safe to remove with "git worktree remove {{path}}".`

**Target:** `{{worktree_path}}`.

**Severity bump:** if 4+ such worktrees exist, escalate to 🟡 Medium with note: `{{count}} stale worktrees in {{meta_root}}/.claude/worktrees/ — consider a sweep.`

---

### EA-007 — Worktree has uncommitted real work (clutter, 🟡 Medium)

**Evaluation:** Any worktree where `git status --short` shows non-submodule changes AND `(now - last_commit) > 3 days`.

**Note:** `Worktree {{name}} has uncommitted changes from {{idle_days}}d ago — {{dirty_count}} files dirty. Either commit or stash before it's lost.`

**Target:** `{{worktree_path}}`.

---

### EA-008 — Multiple worktrees on near-identical branches (clutter, 🟢 Low)

**Evaluation:** Two or more worktrees whose last commit subject is byte-identical. Suggests abandoned restarts of the same task.

**Note:** `Worktrees {{names}} share the same last commit subject — likely abandoned restarts.`

**Target:** `{{worktree_paths}}` (joined).

---

### EA-009 — Stale local branch (clutter, 🟢 Low)

**Evaluation:** Local branch in any tracked repo with no upstream AND last commit older than 14 days.

**Note:** `Local branch "{{branch}}" in {{repo}} has no upstream and is {{idle_days}}d old.`

**Target:** `{{repo}}#{{branch}}`.

---

### EA-010 — Strategic initiative without live anchor (drift, 🟡 Medium)

**Evaluation:** Any `project_*.md` whose body does NOT cite an `AT-\d+` key, AND whose `originSessionId` is older than 30 days.

**Note:** `Initiative "{{memory_name}}" has been in memory for {{age_days}}d with no Jira anchor. Either create a ticket or retire the memory.`

**Target:** `{{memory_name}}`.

---

### EA-011 — Open PR without Jira linkage (drift, 🟢 Low)

**Evaluation:** Any open PR whose title and head branch contain no `AT-\d+` key.

**Note:** `PR {{repo}}#{{number}} has no Jira reference in title or branch — traceability gap.`

**Target:** `{{pr_url}}`.

**Suppress when:** the PR repo is `ADRs`, `dx-aicentral`, `claude-config`, or any repo whose default behavior is documentation-only.

---

### EA-012 — Worktree branch references a closed Jira ticket (clutter, 🟡 Medium)

**Evaluation:** Worktree branch contains an `AT-\d+` key whose live status is `Done`.

**Note:** `Worktree {{name}} is on branch {{branch}} (linked to {{ticket_key}}, now Done) — work likely complete, worktree can be removed.`

**Target:** `{{worktree_path}}`.

---

## Evaluation order

Rules are evaluated in registry order. Each rule produces zero or more findings. The full findings list is then sorted by severity (🔴 → 🟡 → 🟢), and within each tier by category in the order: `skew → priority → drift → staleness → clutter`. Within a category, sort by target alphabetically for stability across runs.

## Adding new rules

A new rule must:

1. Get a stable ID `EA-NNN` with the next free integer. Never re-use an ID, even after retirement.
2. Specify a single category from the canonical set.
3. Provide a deterministic evaluation that can be computed from the gathered data alone — no further API calls.
4. Provide a note template with `{{placeholders}}` only for fields available in the gathered data.
5. State a severity AND any escalation condition.
6. State suppression conditions if the rule is noisy in some contexts.

If a rule generates more findings than 10% of the total, it's likely undertuned — narrow the evaluation or raise the threshold rather than suppressing in the report.

## Retired rules

(empty — track removals here when they happen, with the run date and the reason)
