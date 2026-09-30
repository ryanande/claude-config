---
name: study-run
description: Execute ONE pre-registered study document emitted by /study-design and append its results to that same document. Refuses any document whose pre-registration block was modified after its committing commit — the metric-shopping guard, and the reason design and execution are separate skills. Adjudicates by spawning cold-run labeling subagents that reuse the RFC-0018 spawn mechanics — fresh context, one item each, distinct models, no cross-talk, no expected-label slot — and re-checking every returned label against the artifact. Reports the metric with unresolved items in the denominator explicitly, never silently dropped, and states whether the result crossed the pre-registered negative-result threshold. Refuses caller-supplied expected results, caller-supplied labels or hints about which items are real, a caller verdict, a metric not already in the frozen block, and more than one study per invocation. Refuses an already-run document, one whose OQ has another live study, and a runner on the re-deriver's model. Trigger with /study-run --study <path>, "run this pre-registered study", or "execute EVAL-NNNN". EXECUTES ONLY — does not design studies, choose metrics, or amend the pre-registration block; that is /study-design.
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash, Write, Agent
---

# /study-run — execute one pre-registered study, behind a tamper guard

`/study-design` proposes a study and freezes its `pre-registration:` block —
design, metric, sample, stopping-rule, resolution, negative-result, protocol —
into a study document in `research-docs`. `study-run` is the only skill that
executes that document. The split exists so the metric cannot be chosen after
seeing results: design and execution are different skills, running at different
times, so "which metric looks best" is never a question execution gets to
answer.

## When to invoke

- A pre-registered study document already exists (`content/evals/<slug>.md` or
  `content/benchmarks/<slug>.md`) with a frozen `pre-registration:` block, and
  it has not yet been run.
- `oq-resolver` or a human wants EVAL-NNNN / BENCH-NNNN actually executed.

**Don't invoke when:**
- No pre-registered document exists yet — that's `/study-design`.
- The caller wants to change the metric, design, or sample source. Those are
  frozen; amending them is `/study-design`'s job, run again as a new proposal.
- More than one study document is in scope for the call. One study per
  invocation.

## Refusals

Refuses, per the suite's refusal discipline:
- More than one study document passed to a single invocation.
- A study document whose `pre-registration:` block fails the tamper guard
  (Workflow Step 2) — untracked, uncommitted, or touched by other than
  exactly one commit.
- A caller-supplied expected result for the study.
- A caller-supplied label, or hint about which sample items are real.
- A caller-supplied verdict.
- A metric not already present in the frozen `pre-registration:` block.
- An already-run document — a completed `run-<date>.json`, results content, or
  a `study-run/<id>-*` branch on the remote other than those this run's own
  registration names.
- A freezing commit that is not an ancestor of `main` at the publication URL.
- Another live document for the same OQ (Workflow Step 3a).
- A runner recorded on the same model as the re-deriver slot (`fable`).
- Any pinned slot model that is unavailable.
- A registration push that fails.
- A design-time invariant `study-run` re-derives (Step 3a) that does not match
  the block — including a `protocol` key outside its design's key set, a D2
  `blind-scope` carrying the publication remote, and a D3 ledger row whose arm
  the frozen `arm-assignment` does not reproduce.
- A caller-supplied D3 phase, arm assignment, or manifest — frozen or derived,
  never a flag; `recheck.py phase` takes no date argument.
- A D2 `blind-scope` entry that is not path-scoped and ref-pinned, or an export
  of one that carries `.git` — the corpus history IS the answer key.
- A D3 enrolment row carrying an outcome or an arm split, and a phase derived
  from a ledger that did not validate.

## Workflow

1. Resolve the document (refuse if more than one) and the research-docs
   checkout the same way `study-design` does (`dxroot research_docs` here,
   `$DX_ARCH_META_ROOT/repos/research-docs` upstream, or an explicit `--repo`
   override); never
   guess or fall back to the CWD. Read the block's `research-docs`
   `evidence-scope` URL; refuse if the checkout's `origin` differs (six-field
   block: no URL — record the checkout's `origin` as a disclosed, unverified
   identity). Record the runner's model (source stated; refuse if it is the
   re-deriver's; correlation if a labeler's or tiebreak's; refuse if any pinned
   model is unavailable). Pin the executing code: sha256 of the deployed
   `scripts/` + `references/` vs the same at `research-skills` `main`
   (`git ls-remote`), refuse on mismatch. Resolve every scope entry per
   [`references/evidence-scope.md`](references/evidence-scope.md) — D2's
   `blind-scope` and D3's `evidence-scope-rule` included; refuse any unresolved
   entry; re-attempt `ls-remote` for excluded remotes.
2. **Tamper guard.** Conditions (a)–(c) as before (untracked; uncommitted;
   more than one committing commit — worked commands in
   `test-corpus/tamper-refusal.md`), plus (e) freezing commit is an ancestor of
   `main` fetched from the publication URL (`recheck.is_ancestor`), then
   **register** (`started-<date>.json` pushed on `study-run/<id>-<date>`;
   refuse to spawn if the push fails), then (d) already-run: whole-file
   `git log` returns exactly the freezing commit; no completed
   `run-<date>.json`; no results content; no `study-run/<id>-*` branch on the
   remote other than those the registration names. Resume / restart (a D3 enrol
   pass always restarts) per [`references/run-record.md`](references/run-record.md).
3. Refuse caller-supplied label, hint, expected result, verdict, metric.
3a. Liveness (`recheck.py liveness`): refuse if any *other* live document has
   this OQ. When `protocol:` is present, re-derive THAT DESIGN's invariants and
   refuse on mismatch; a key outside the design's own set refuses too. Steps
   3a, 5a, 6 and 7 are per design —
   [`references/per-design-steps.md`](references/per-design-steps.md).
4. Detect version by `protocol:` presence. A six-field block runs only if its
   freezing commit predates `MERGE_SHA`
   ([`study-design/references/pre-registration.md`](../study-design/references/pre-registration.md));
   defaults: labels-per-item 2, any-disagreement → UNRESOLVED, scope =
   research-docs only, publication identity = checkout `origin` (unverified),
   screen/pack/budget/strata off, gate off, re-derivation on, fixed-slots on.
   Record each default applied.
5. Collect the sample per `sample:` (sidecar path per
   [`references/sample-collection.md`](references/sample-collection.md)).
5a. The matched design's own collection step (per-design steps).
5b. When `screen: structural-real`: `screen.py` per item; provisional REAL to
   the ledger only.
5c. Ledger rows pushed per attempt (launch before fire, done before read).
6. Build packs, render briefs from
   [`references/labeler-brief.md`](references/labeler-brief.md), spawn in
   batches ≤ 10 per
   [`references/adjudication-mechanics.md`](references/adjudication-mechanics.md);
   apply `recheck.disagree` / `apply_tiebreak`. Which items spawn, and on which
   pack, is per design.
7. `recheck.py gate` over every label; a REAL or NOISE label with no evidence
   entry fails the gate. One re-derivation spawn per resolved item from
   [`references/rederive-brief.md`](references/rederive-brief.md); match
   keeps, else UNRESOLVED. The runner adjudicates nothing. The gate's legs are
   per design.
7a. `recheck.unresolved_source` for every UNRESOLVED; unknown identities and
   reachable "inaccessible" remotes recorded as deviations.
8. Second `ls-remote` snapshot; write `run-<date>.json` per
   [`references/run-record.md`](references/run-record.md), whose per-design
   field substitutions it states; append results to the document: the frozen
   metric over its full denominator, cap met or not, unresolved by source,
   dissent rate and pre/post split, contrast per value, negative-result
   crossed. A D3 enrol pass appends no results.

## Invocation discipline

Framework: skill-invocation-discipline (`~/dx-arch-meta/repos/research-docs/content/design/skill-invocation-discipline.md`). (Upstream path, unresolvable here — `~/dx-arch-meta/repos/research-docs` is an uninitialized checkout on this machine and the doc is not mirrored into `research_docs`. Historical provenance, not a runtime dependency; the invocation-discipline rules the skill enforces are restated in this file's own §Invocation discipline.) The tamper guard controls whether a document can be run at all; bias control governs what can be smuggled into the run once it starts.

**IN-contract (required):**
- `--study <path>` — the pre-registered study document to execute.

**IN-contract (optional):**
- `--repo <path>` — explicit `research-docs` checkout override, when neither `dxroot research_docs` nor `DX_ARCH_META_ROOT` resolves one.

**Per-skill bias surfaces (forbidden — refusal-record emitted per `refusal-record.md` v1.1):**
- Caller's expected result for the study.
- Caller-supplied expected label, or hint about which sample items are real or noise.
- A caller-supplied verdict.
- Caller interpretation of an individual item's finding text.
- A metric not already present in the frozen `pre-registration:` block. The metric is frozen at design time; this skill never chooses or substitutes one.

**Per-skill bloat surfaces (forbidden — refusal-record emitted):**
- Attached study body. The skill reads the document from its resolved path, after the tamper guard passes.
- More than one study document per invocation.
- A caller-supplied D3 phase, arm assignment, or manifest — frozen or derived, never a flag.

**The payload carve-out.** The finding set the pre-registration block's `sample:` field hands to each labeling spawn is the payload under measurement — fixed by `study-design` before this run ever existed — and is NOT the "pre-filtered focus" OUT-bias surface `invocation-discipline-lint` otherwise refuses. The carve-out also covers the evidence pack (derived, not chosen), the screen's provisional label (held in the ledger, never shown to a spawn), and the cited list handed to the re-deriver (files, never labels). State this split explicitly whenever this skill's call signature is linted, or `enforce` mode refuses every `study-run` invocation on its own sample.

## Load-when table

| Step | Reference | Why load |
|------|-----------|----------|
| 1 | [`references/evidence-scope.md`](references/evidence-scope.md) | The resolver chain (in-checkout → sibling checkout → clone root → refuse), the clone root's protection, and why `~/.claude` is never a scope path. |
| 2, 8 | [`references/run-record.md`](references/run-record.md) | The `started-<date>.json` / `ledger.json` / `run-<date>.json` shapes, resume-vs-restart, and what each field records. |
| 3a, 5a, 6, 7 | [`references/per-design-steps.md`](references/per-design-steps.md), [`../study-design/references/pre-registration.md`](../study-design/references/pre-registration.md) | What each of those four steps does under D1, D2 and D3, and the per-design `protocol` key tables the re-derivation checks against. |
| 5 | [`references/sample-collection.md`](references/sample-collection.md) | Discovery of the `candidates.jsonl` sidecars (tracked at HEAD, plus spool rows tagged separately), the per-design field mapping, the recorded-trail-vs-re-run rule, and the provenance strip list for labelers. Reads the record contract at [`../citation-detail-verify/references/candidates-contract.md`](../citation-detail-verify/references/candidates-contract.md) v1.0. |
| 6 | [`references/adjudication-mechanics.md`](references/adjudication-mechanics.md), [`references/labeler-brief.md`](references/labeler-brief.md) | The reused spawn rules, why `/review-artifact`'s entry point is not called instead, why the finding batch is payload not a bias surface, the fixed slot table, and the labeler brief template. |
| 7 | [`references/rederive-brief.md`](references/rederive-brief.md), [`scripts/recheck.py`](scripts/recheck.py) | The re-deriver's brief (sees the cited list, never the labels) and the gate/rederive/unresolved-source/ledger-validation functions the runner calls but never substitutes for. |

## Self-check

Before reporting done, confirm:
- Exactly one study document was in scope, and the tamper guard ran before any
  other step.
- All five tamper-guard conditions were checked (a)–(e), not only the
  commit-history one.
- Registration was pushed before any spawn fired.
- Every returned label was gated, and every resolved item was re-derived on a
  distinct slot (`fable`) before being accepted.
- The runner labelled nothing itself — every judgment traces to a spawn or a
  script.
- Every final UNRESOLVED carries an `unresolved_source`.
- When the block ran under v1.0 defaults, every default applied was listed in
  the run record.
- The appended result states the metric over the full denominator, and the
  `negative-result` crossing explicitly.

## Success criteria

- `detect refusal-preregistration-edited-after-commit in ~/.claude/skills/study-run/test-corpus/tamper-refusal.md count >=1`
- `detect payload-distinct-from-bias-surface in ~/.claude/skills/study-run/test-corpus/payload-not-bias.md count >=1`
- `detect unresolved-counted-in-denominator in ~/.claude/skills/study-run/test-corpus/unresolved-in-denominator.md count >=1`
- `detect candidates-sidecar-discovery in ~/.claude/skills/study-run/test-corpus/candidates-sidecar-discovery.md count >=1`
- `detect noise-vs-unresolved-tiebreaks in ~/.claude/skills/study-run/test-corpus/disagreement-ordered-3way.md count >=1`
- `detect recheck-not-performed-by-runner in ~/.claude/skills/study-run/test-corpus/recheck-gate-and-rederive.md count >=1`
- `detect liveness-reads-full-history in ~/.claude/skills/study-run/test-corpus/liveness-full-history.md count >=1`
- `detect v10-block-defaults-recorded in ~/.claude/skills/study-run/test-corpus/v10-block-runs-under-defaults.md count >=1`

## Out of scope

- Designing a study, choosing a metric, or amending the pre-registration block
  — that's `/study-design`.
- Choosing a disposition for the OQ — that's `oq-resolver`'s Step 6.
- Generating findings by spawning critics over a document — that's
  `/review-artifact`; `study-run` reuses its spawn mechanics, not its entry
  point, because it adjudicates a caller-supplied batch that `/review-artifact`
  has no channel for. See `references/adjudication-mechanics.md`.
