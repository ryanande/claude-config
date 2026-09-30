---
title: Refactor ra-pr-review onto review-artifact's architecture
status: approved
date: 2026-08-04
---

# Refactor ra-pr-review onto review-artifact's architecture

## Context

`skills/ra-pr-review/SKILL.md` reviews a PR and posts one stack-ranked comment,
gated by a k=2 verifier-subagent confirmation step. `review-artifact` (home:
`.apm/skills/review-artifact/` in dx-aicentral, org-shared via APM, deployed to
`~/.claude/skills/review-artifact/`) reviews a decision artifact (RFC, ADR,
SKILL.md, survey, design doc) with materially more rigor: a named lens catalog,
distinct models per critic, structural anti-anchoring (a fixed brief template
with no expected-findings channel), a refusal surface for reachable
invocation-discipline violations, a self-contained 6-field-row / 3-status
findings envelope with a verdict computation, self-check invariants, and a
grep-gated test-corpus proving each invariant.

review-artifact's own Boundary section explicitly puts PR diffs **out of
scope** ("a different measured regime"). This design does not change that —
it ports the *pattern* into `ra-pr-review`, which remains its own skill, local
to this repo, not APM-distributed.

## Decisions

1. **Scope: refactor ra-pr-review only.** review-artifact's Boundary/home is
   untouched. `ra-pr-review` stays at `skills/ra-pr-review/` in claude-config.
2. **Verification model changes.** The existing k=2 verifier-subagent gate
   (two independent subagents confirm/refute each candidate) is **removed**.
   Adjudication now matches review-artifact's rule 6 literally: the
   orchestrator itself re-checks each candidate finding against the actual
   code (not just the diff hunk) and assigns pass/fail/unverifiable directly.
   This is a deliberate reduction from ra-pr-review's prior differentiator,
   traded for architectural parity with review-artifact, per explicit
   confirmation.
3. **Test fixtures included.** A `test-corpus/` + grep-gated `## Success
   criteria` section is added, matching the convention already used by
   `review-artifact`, `adversarial-frame`, `citation-detail-verify`, and
   others in this repo.

## Boundary

- **Owns:** k-critic, lens-diverse, model-diverse review of ONE PR's diff,
  with direct orchestrator adjudication against the actual (post-diff) code,
  ending in one posted stack-ranked comment.
- **In-scope input:** a single PR, by number/URL, or the current branch's
  open PR.
- **Out of scope:** approving / requesting-changes / merging (leave review
  state to the human); editing PR files or pushing fixes; inline per-line
  review comments (this skill posts one consolidated comment by design);
  reviewing non-code decision artifacts (that's `review-artifact`'s job).
- **Home:** `skills/ra-pr-review/` in **claude-config** — personal, not
  APM-distributed. Unlike `review-artifact`, there is no deployed-copy vs.
  source-copy distinction; paths in this doc and in the skill's own Success
  criteria section are repo-relative.
- **Decision authority:** the user. The skill drafts and self-checks the
  comment but posts only after explicit confirmation; it never approves or
  merges.

## Interface

```
/ra-pr-review [<pr-number-or-url>] [--lenses <a,b[,c]>] [--k <2|3>]
```

- Omit the PR arg to default to the current branch's open PR (unchanged from
  today).
- `--lenses` — optional; comma-separated named lenses (see §Lens catalog).
- `--k` — optional critic count; default **2**, max **3**.
- **`--k` and `--lenses` must agree:** same reconciliation rule as
  review-artifact — counts must match when both given; only `--lenses` given
  → `k` = lens count; only `--k` given → lenses = the default set of that
  size; neither given → k=2 with the default k=2 set. Each critic gets a
  distinct lens and a distinct model.

## Lens catalog

PR review has one fixed input shape (a diff), so there is a single default
set rather than review-artifact's by-artifact-type table. Names are drawn
directly from ra-pr-review's own existing "no nits" finding criteria
(correctness, security, data-loss, concurrency, contract, performance):

- `correctness` — logic bugs, wrong behavior on edge cases, incorrect state
  transitions, a contract/API break smuggled into the diff.
- `security-and-data-safety` — injection, authn/authz gaps, secrets exposure,
  unsafe deserialization, an irreversible/destructive operation, data loss.
- `concurrency-and-performance` *(k=3 addition)* — race conditions, unsafe
  shared-state mutation, a hot-path regression or blocking call introduced on
  a critical path.

Default k=2 set: `correctness`, `security-and-data-safety`. k=3 adds
`concurrency-and-performance`.

**Model assignment** — identical to review-artifact: k=2 → `opus`, `sonnet`;
k=3 → `opus`, `sonnet`, `haiku`. Same-provider variation; documented as a
directional lever, not a guarantee (Anthropic-only model roster, same honest
residual review-artifact records).

## Refusal surface

| Violation | category |
|---|---|
| more than one PR specified | `bloat` |
| `--k` ≠ `--lenses` count (when both given) | `bias` |
| derived `k` < 2 | `bias` |
| unknown lens name | `bias` |
| lens count > 3 | `bloat` |

Malformed `--k` (not literally `2` or `3`) → plain abort with a clear error
(parse error, not a refusal record) — same split review-artifact makes.

Anti-anchoring itself is enforced structurally (no input channel for
expected findings), same as review-artifact — there is no bullet for it in
the refusal table because there is nothing to refuse.

## Spawn mechanics — RFC-0018's six rules, adapted

| Rule | How ra-pr-review implements it |
|---|---|
| 1 — isolated context + anti-anchored brief | Cold-run spawn (fresh subagent). Anti-anchoring is structural: brief generated from a fixed template with no expected-findings slot. **PR-specific addition:** the brief explicitly warns the diff/code is untrusted data, and an in-diff directive trying to steer the verdict is itself a finding to report (ra-pr-review's pre-existing rule, preserved). |
| 2 — whole artifact per critic | Every critic gets the **whole diff**, not a file-group partition — a change from today's "split by area/file group for large PRs." Cross-cutting defects (a security issue spanning files, a partial revert) are exactly what a partition would hide. **Documented residual:** for a diff too large for one context window, the critic pulls additional file context itself via Read/Grep rather than the orchestrator pre-splitting review responsibility. |
| 3 — independent, parallel, single-pass | k critics spawned concurrently, one batch, single pass each; no re-prompt-to-find-more. |
| 4 — cross-provider (weak lever) | Same honest residual as review-artifact: Anthropic-only model roster (`sonnet\|opus\|haiku\|fable`), so same-provider variation is used; documented as directional, never a guarantee. |
| 5 — no cross-talk | Unnamed spawns, no `SendMessage` tool granted. No sibling roster; critics never see each other's briefs or findings. |
| 6 — aggregator adjudicates vs ground truth | **Changed from ra-pr-review's prior design.** The orchestrator itself re-checks each candidate finding against the actual (post-diff) code at `path:line` — not the k=2 verifier-subagent gate that existed before. This is the primary independence lever, same as review-artifact. |

## Data flow

1. Preflight (`gh auth status`, PR resolves) — unchanged from today.
2. Resolve PR + fetch full diff — unchanged from today.
3. Select lenses (caller-given or default) sized to k; assign each a distinct
   model.
4. Generate k anti-anchored briefs from the template (lens name + threat-model
   line + diff-is-data warning + output shape).
5. Spawn k critics in parallel: cold-run, whole diff, no cross-talk. Each may
   Read/Grep the repo for context beyond the hunk.
6. Collect each critic's raw findings (final message only). A dead/null
   critic → one synthetic `unverifiable` row for that lens, `check-name:
   lens-finding-minor`; continue with survivors.
7. **Adjudicate:** for each finding, the orchestrator reads the cited
   `path:line` in the actual file and assigns `pass` (refuted) / `fail`
   (confirmed real) / `unverifiable` (can't confirm from available context).
8. Stack-rank surviving `fail` rows by `check-name` severity, then `path:line`
   ascending.
9. Render surviving `fail` rows into the existing comment format. If the
   run's verdict is `unverifiable` (zero `fail` rows, ≥1 un-adjudicated lens),
   say so in chat before drafting — recommend re-running that lens — rather
   than silently posting a clean "no findings" comment. The comment itself
   never mentions unverifiable lenses.
10. Self-check the assembled body (unchanged gate from today) + secret/PII
    scan + confirm with the user + post (`--edit-last` reuse, unchanged).

## Output — envelope schema (internal, not a posted artifact)

Same 6-field row shape and 3-status vocabulary as review-artifact's envelope,
scoped to this skill:

```json
{
  "version": "1.0",
  "skill": "ra-pr-review",
  "artifact": "<PR URL>",
  "invoked_at": "<ISO-8601 UTC, second precision>",
  "verdict": "pass | fail | unverifiable",
  "rows": [ {
    "citation-id": "<lens-id>",
    "check-name": "lens-finding-blocking | lens-finding-should-fix | lens-finding-minor",
    "status": "pass | fail | unverifiable",
    "cited-value": "<diff span / claim the finding is about>",
    "actual-value": "<critic's proposed fix / correction>",
    "evidence-quote": "<verbatim code the orchestrator verified against>"
  } ]
}
```

- Verdict computation identical to review-artifact: `fail` iff ≥1 `fail` row
  (dominates); else `unverifiable` iff ≥1 `unverifiable` row; else `pass`.
- `evidence-quote` MUST be non-empty on a `fail` row.
- No top-level severity field — severity lives only in `check-name`. This
  replaces today's ad hoc blocker/high/medium vocabulary with the fixed
  `lens-finding-{blocking|should-fix|minor}` enum (direct rename, same three
  tiers).
- **The envelope never leaves the skill as a second deliverable.** It is the
  adjudication scratchpad; the only artifact posted anywhere is the rendered
  PR comment. This keeps the comment exactly as clean and LLM-optimized as it
  is today.
- A `{refusal}` record (same shape as review-artifact's, `skill:
  "ra-pr-review"`) is the distinct abort shape for a refused invocation.

## File layout

Split the current single-file `SKILL.md` into progressive-disclosure
references, matching review-artifact's shape:

```
skills/ra-pr-review/
  SKILL.md                        (interface, boundary, data flow, self-check — orchestration only)
  references/
    lens-catalog.md               (named lenses, default set, k/lens reconciliation, model assignment)
    brief-template.md             (anti-anchored critic brief incl. diff-is-data warning)
    envelope-schema.md            (row shape, status semantics, verdict computation, refusal record)
  test-corpus/
    anti-anchor.md
    diff-is-data.md
    whole-diff-not-partitioned.md
    k-reconciliation.md
    refusal-reachable.md
    envelope-shape.md
    verdict-deadcritic.md
    lens-selection.md
```

## Testing — test-corpus + Success criteria

Eight fixture files, one invariant each, mirroring review-artifact's set plus
two PR-specific additions:

- `anti-anchor.md` — critic brief has no expected-findings slot.
- `diff-is-data.md` *(new, PR-specific)* — an in-diff steering directive gets
  reported as a finding, not obeyed.
- `whole-diff-not-partitioned.md` *(new, PR-specific)* — documents rule 2's
  tightening: no file-group split, whole diff to every critic.
- `k-reconciliation.md` — `--k`/`--lenses` count agreement rule.
- `refusal-reachable.md` — the 5 reachable violations.
- `envelope-shape.md` — 6-field row shape, `fail` requires non-empty
  `evidence-quote`, no top-level severity field.
- `verdict-deadcritic.md` — dead critic → `unverifiable`, never silently
  `pass`.
- `lens-selection.md` — default k=2 set, whole-diff-to-every-critic,
  k-distinct-models.

A `## Success criteria` grep-gate section lists one `detect`/`absent` row per
invariant above, pointing at these repo-relative test-corpus paths (this
skill is not APM-distributed, so there is no deployed-path vs. source-path
split the way review-artifact has).

## Self-check (a run is well-formed iff)

- no critic brief contains expected findings or a focus filter (structural
  anti-anchor invariant);
- every critic received the whole diff, not a file-group partition;
- exactly `k` critics (2 ≤ k ≤ 3) with `k` distinct lenses AND `k` distinct
  models;
- every reported finding carries an orchestrator-adjudicated status; every
  `fail` row carries a non-empty `evidence-quote` pointing at the real
  (post-diff) code, not just the hunk;
- the aggregate verdict follows the verdict computation verbatim
  (dead-critic run with no `fail` rows ⇒ `unverifiable`, never `pass`);
- the refusal surface fires on each reachable invocation-discipline violation;
  malformed `--k` takes the plain-abort path;
- the posted comment contains exactly the surviving `fail` rows, stack-ranked,
  each anchored to a `path:line` present in the diff;
- a secret/PII scan ran over the comment body before posting;
- the user confirmed before the comment was posted.

## Out of scope (YAGNI)

Approving / requesting-changes / merging. Editing PR files or pushing fixes.
Inline per-line review comments. Emitting the envelope as a second,
user-facing artifact. Re-adding the k=2 verifier-subagent gate. Cross-provider
model diversity (documented residual, same as review-artifact, until the
harness offers non-Anthropic models).
