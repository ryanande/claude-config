# study-run — what Steps 3a, 5a, 6 and 7 do, per design

Loaded at Steps 3a, 5a, 6 and 7. `protocol:`'s key set is per design
([`../../study-design/references/pre-registration.md`](../../study-design/references/pre-registration.md)),
and so are these four steps. A `protocol` key outside the block's own design's
set refuses; it is never ignored as a harmless extra.

| Step | D1 | D2 | D3 |
|---|---|---|---|
| 3a re-derive | cap, budget, owners, repo map, unresolved identities, scope, exclusions, screen, clause-set coverage, pinned values | `recheck.py manifest` (every flag required, non-zero exit on any error): manifest sha256 hashed from the file's BYTES, `corpus-ref` ancestry, every manifest row's path at `corpus-ref.sha`, each row's `region` a `[start, end)` integer pair, no duplicate `item_id`, class counts with no zero-planted class, all three blindness legs, `skill-runs` = distinct artifact count | `recheck.py enrolment`, `phase`: arm mode in `ARM_MODES`, arm tokens long enough and off the common-word denylist, every ledger row's arm recomputed from the FREEZING COMMIT, ledger append-only against the previous registration branch's blob, no row carrying an outcome, phase derived from the frozen stopping rule over a VALIDATED ledger, pinned values iff `outcome.adjudicated` |
| 5a sample | run `protocol.enumerator` at the pinned commit; refuse on sha256, repo-map hash/content, or count mismatch; record `gh_login` | read the manifest from the PUBLICATION repo, refuse on sha256 mismatch, materialize each `blind-scope` entry as a history-free `git archive` export at `corpus-ref.sha` scoped to its `path`, then run the skill under test once per manifest artifact against that export — one ledger row per run (`slot: skill-run`) so a second run of the same artifact is flagged; record the emitted-rows file's sha256; no repo map, no `gh_login` | phase is DERIVED, never a flag — `enrol` while `target-n` is unreached and the deadline unpassed, `score` otherwise. **enrol**: apply `enrolment.eligibility` to artifacts merged since the last ledger row, apply `arm-assignment`, append and push rows carrying NO outcome and NO arm split, append NO results. **score**: the sample is the closed ledger; read outcomes from `outcome.source`; record any deadline-forced shortfall |
| 6 spawn | every census item, `citation-neighbourhood` pack | `recheck.py match` first; only the RESIDUAL spawns, on a `defect-neighbourhood` pack carrying ONE candidate manifest row, never the manifest. A planted defect with no unmatched row on its own path is a decided false negative and never spawns | none in enrol phase; none when `outcome.adjudicated` is false; otherwise `arm-blinded-artifact`, arm markers stripped — the pack is the blinding mechanism, the gate leg only a backstop |
| 7 gate | every label; clause matches `clause-set`; `--arms none` | residual labels only, legs scoped to the corpus export, claim matching `match-rule`; `--arms none` | adjudicated: `--arms '["<A>","<B>"]'` so `recheck.arm_leak` fails a label naming either arm anywhere but the frozen clause. mechanical: no labels — gate each recorded outcome's CITATION at the enrolled artifact's merge SHA; one that will not resolve is a deviation, not an UNRESOLVED label |

## Why the phase is derived and not a flag

`study-run`'s surface takes no optional mode flag, and the suite's shared-contract
lock forbids adding one. `recheck.py phase` returns `enrol` while `target-n` is
unreached and `enrolment.deadline` unpassed, `score` otherwise — the same
condition the block froze. That is what stops a caller asking for an early score
pass to see whether the numbers look good, so the subcommand takes **no date
argument**: a caller-supplied "today" IS that early pass. It also derives the
count from a ledger that validated, because an unvalidated ledger padded with
empty rows reaches `target-n` on its own.

Optional stopping remains possible and is not claimed otherwise: enrolment only
advances when the operator fires an enrol pass, and eligibility is a judgment. What
the row shape removes is the peek — no enrol row carries an outcome or an arm
split, so the running delta is not there to read — and each pass's date and any
identifier `gaps` land in the run record, so an unusual cadence is visible.

A D3 enrol pass therefore repeats across the study's months. Each pass registers,
and because the resume predicate cannot hold once `HEAD-at-run` resolutions move,
each takes the restart path — see
[`run-record.md`](run-record.md) §`started-<date>.json` for what its
`prior_attempts` entry records in place of a spawn-ledger partial disposition.

## Why one gate serves three designs

`recheck.gate_label` is not branched. D2 and D3 items carry no corpus type, so
both the rule set and the item use the literal `"*"`, the frozen rule text
(`match-rule` for D2, `outcome.measure` for D3) travels in the label's `clause`
field, and the label vocabulary stays `REAL` / `NOISE` / `UNRESOLVED` so the
evidence-presence leg keeps firing. `test_recheck.py` pins the single-entry
`"*"` set. Full reasoning:
[`adjudication-mechanics.md`](adjudication-mechanics.md) §The wildcard rule set.
