# study-run — registration, ledger, and run record

All three live under `assets/evals/<id>/` in the publication repository and
are pushed to branch `study-run/<id>-<date>` at the publication URL.

## `started-<date>.json` (Step 2, before any spawn)

```json
{"block_sha256": "…", "runner_model": {"value": "…", "source": "harness-identity | self-report"},
 "resolved": [{"remote": "…", "path": "…", "sha": "…", "rung": 1}],
 "prior_attempts": [{"branch": "study-run/<id>-<date>", "head": "…",
                     "partial": {"labels": 40, "real": 7, "noise": 25, "unresolved": 8, "provisional_precision": 0.13}}],
 "skill_code": {"deployed_sha256": "…", "main_sha": "…", "main_sha256": "…"},
 "started_at": "…"}
```

Resume iff a pushed `started-*.json` has the same `block_sha256`, no results
commit exists, and the freshly resolved set equals `resolved`. Otherwise
restart: new file, new branch, prior attempts listed with partial disposition
reconstructed from their ledgers.

**D3 enrol passes always restart.** The resume predicate requires the freshly
resolved set to equal the recorded one, and D3's `ref: HEAD-at-run` resolutions
will not match months later, so every enrol pass after the first takes the
restart path — a new `started-<date>.json` on a new branch. An enrol pass fires
no spawn and writes no `ledger.json`, so there is no spawn-ledger partial
disposition to reconstruct; its `prior_attempts` entry records the **enrolment**
ledger's state instead — `{"branch": …, "head": …, "enrolment": {"rows": <n>,
"last_identifier": "<id>"}}`, the two values `recheck.py enrolment` returns. It
MUST NOT claim a `partial` label count no enrol pass produced. The already-run
tamper leg tolerates these branches through its "other than those the
registration names" clause, so the branch set grows with the study's length
without the document reading as already run.

## `enrolment.jsonl` (D3 only, Step 5a, one row per enrolled artifact)

Pinned by PATH in `protocol.enrolment.ledger`, never by sha256 — no hash over an
enrolment record can exist before enrolment begins. Append-only: one row per
enrolled artifact, `{identifier, arm, merge_sha, eligibility_rationale,
resolved: [{remote, path, sha, rung}]}`, committed and pushed as it is appended.

**No row carries an outcome.** An operator holding the running per-arm delta can
stop enrolling when the interim suits them — optional stopping the phase
derivation does not detect. So outcomes are read at score time from
`outcome.source`, and a row carrying `outcome`, `arm_split`, or `delta` refuses.

`recheck.py enrolment` validates it at Step 3a: the arm mode is implemented, no
row shrank or changed after it was appended, no duplicate identifier, no peek
field, and every recorded `arm` reproduced by `assign_arm` keyed on the study's
FREEZING COMMIT — there is no salt field. `--prior` is required and is the ledger
blob at the previous registration branch's head (`git show <prior-branch>:<ledger
path>`), not a caller-supplied history: against an empty prior every append-only
leg is vacuous, and a ledger rewritten down to one hand-picked row would validate.

It also returns `gaps` — skipped numeric identifiers within the enrolment window.
A gap is how an operator bumps an incrementable counter to move their own arm, and
it also arises from an ineligible artifact, so it is recorded as a deviation rather
than refused. `eligibility_rationale` is recorded but not recomputed: applying
`enrolment.eligibility` is a judgment, and the named residual arm assignment's
mechanical half exists to offset.

## `ledger.json` (Steps 5b–7, one row per spawn attempt)

`{item, slot, attempt, model, spawn-id, state: launched|done, trigger:
null|timeout|tool-error|concurrency-cap|user-interrupt, verdict-path,
reported-model, screen: REAL|null}`. **A D2 run of the skill under test takes a
row too** — `item` the manifest artifact, `slot` `skill-run` — so
`validate_ledger`'s existing `flagged_items` leg fires on a second run of the
same artifact. Without it, best-of-N over the paid measurement itself is the one
re-attempt the machinery cannot see, in a design whose whole point is running a
nondeterministic skill many times. Launch row committed and pushed before
the spawn fires; done row before the runner reads the verdict. Batches ≤ 10.
`recheck.py ledger` (`validate_ledger`) returns three keys —
`flagged_items` (items whose done row follows an earlier attempt, or whose
attempt number exceeds 1, whatever the trigger), `unverified_slots` (rows
whose `reported-model` is `unknown`), and `errors` (missing keys, missing
`verdict-path` on a done row, or a `reported-model` that mismatches the
requested `model`).

## `run-<date>.json` (Step 8)

Fields, in order: tamper guard result per condition (a)–(e); registration
branch and its commit chain; resolved set; both `ls-remote` snapshots for
excluded remotes; defaults applied (v1.0 blocks); enumerator replay counts
and `gh_login`; screen decisions and contradictions; ledger summary
(attempts, flagged items, unverified slots); labels per slot; disagreement
outcomes; gate failures per item; re-derivation dissent rate; unresolved by
`unresolved_source`; precision = REAL/census; cap and whether met; under
`precision-contrast`, per-value precision and each pair's `noise_dropped`,
`real_dropped`, `passes`; stratum count; out-of-scope identities with
scope-list status; deviations; spawn count vs budget; negative-result
crossed: yes | no | not-evaluable (cap exceeded).

Three of those fields are D1-shaped, and the run record substitutes per design.

**D2.** In place of enumerator replay counts and `gh_login`: the manifest's
sha256 as hashed at run time against the frozen value, its verified path in the
publication repository, `corpus-ref` with its ancestry result, per-class planted
and clean-control counts, all three blindness legs, `skill-runs` versus the
manifest's distinct artifact count, and the sha256 of the emitted-rows file
`match` was given. In place of screen decisions: the mechanical match's true
positives, false negatives, false positives, and residual size. Precision and
recall are reported over their own denominators, the cap over the **residual**
count alongside the manifest count.

**D3, enrol phase.** The derived phase and the condition that derived it, this
pass's date, the enrolment ledger's row count and last identifier, the rows
appended this pass, and any identifier `gaps`. **Not** the arm split, and not any
outcome — an enrol pass that reports the interim is the peek channel the ledger
row shape exists to close. No metric, no cap, no results appended to the document.

**D3, score phase.** The derived phase, the closed ledger's row count against
`target-n` and any shortfall the deadline forced, the rate per arm and their
delta, and — when `outcome.adjudicated` is true — labels per slot, disagreement
outcomes, gate failures including arm-leak breaches, re-derivation dissent, and
the cap over the ledger's row count. When it is false: the citation-gate result
per row and any citation that failed to resolve, recorded as a deviation.
