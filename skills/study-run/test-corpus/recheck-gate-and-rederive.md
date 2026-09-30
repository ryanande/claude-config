# Fixture: the gate and the re-derivation spawn replace the runner's own re-check

## Study document under execution

`content/evals/eval-0031-precision-of-cold-run-labeling.md`, tamper guard
passed, `protocol.recheck: gate+rederive` (`references/adjudication-mechanics.md`
§The re-check). Slots per `references/adjudication-mechanics.md` §Slots:
labeler A = `opus`, labeler B = `sonnet`, tiebreak = `haiku`, re-deriver =
`fable`. Two items and one runner-identity case:

### F-201 — gate failure

Labeler A returns `{"label": "NOISE", "clause": "<matches clause-set row>",
"evidence": [{"remote": "https://github.com/o/research-docs.git", "path":
"content/notes/x.md", "quote": "", "what": "the note contradicts the
finding"}]}` — an evidence entry with an empty `quote`. `recheck.gate_label`
walks `label.get("evidence", [])`: the entry's `remote` resolves in `trees`,
the `path` exists at the pinned SHA, but `q = ev.get("quote")` is falsy, so
`gate_label` appends `"evidence[0] has no quote"` to `fails` and returns it
non-empty. A non-empty `fails` list means the label never reaches
re-derivation: F-201 lands UNRESOLVED, `unresolved_source: gate-failure`
(`recheck.unresolved_source`'s first-checked branch, `rec.get("gate_failures")`
truthy).

### F-202 — re-derivation dissent

Labeler A and labeler B both return REAL with a clause that matches the
clause-set row and evidence whose quote greps verbatim in the pinned tree —
`gate_label` returns `[]` (no fails) for both. The disagreement rule never
fires (A == B == REAL). Per Workflow Step 7, one re-derivation spawn runs on
the `fable` slot (`references/rederive-brief.md`), seeing the pinned trees,
the item, the clause, the pack, and the labelers' cited paths — never their
REAL label. `fable` returns NOISE. `rec.rederive = "NOISE"`,
`rec.final_before = "REAL"` (the gated pre-rederivation value); since
`rederive != final_before`, `recheck.unresolved_source` returns
`rederivation-dissent` before ever reaching the labeler-contradiction check —
a REAL that passed the gate still does not survive an independent
re-derivation that disagrees with it.

### F-203 — gate failure on an ungrounded resolved label

Labeler A returns `{"label": "REAL", "clause": "<matches clause-set row>",
"evidence": []}` — a resolved label carrying no evidence entries at all (the
same shape a `NOISE` label with the `evidence` key omitted entirely would
take). `recheck.gate_label` checks the clause first, then — before ever
walking `label.get("evidence", [])` — sees `label.get("label") in ("REAL",
"NOISE")` with no evidence and appends `"REAL/NOISE label carries no
evidence"` to `fails`, returning immediately. This is the gate closing the
bypass `UNRESOLVED with no evidence passes gate` deliberately leaves open for
the one label value that is honestly evidence-free: only `UNRESOLVED` may
carry an empty (or absent) `evidence` list and still pass; a `REAL` or
`NOISE` verdict must ground itself or the gate fails it, exactly like a bad
path or a non-verbatim quote would.

### Runner identity

The runner's harness-session model is not exposed for this fire, so its model
is recorded as a disclosed self-report: `opus`. `opus` is labeler A's pinned
slot model (`references/adjudication-mechanics.md` §Slots) — per `SKILL.md`
Workflow Step 1, a runner equal to a *labeler's or tiebreak's* model is
recorded as a **correlation**, not refused; the run proceeds, and the
correlation is disclosed in the run record. Had the runner instead
self-reported `fable` — the re-deriver's slot model — Step 1 refuses the run
outright, before any spawn: the re-deriver exists specifically to be an
independent check on the labelers, and a runner sharing that slot's model
could, in principle, be the same process reasoning about its own
re-derivation. Token for this distinction: `recheck-not-performed-by-runner`
— in neither F-201 nor F-202 does the runner itself decide anything; every
verdict traces to `recheck.gate_label`, a labeler spawn, or the `fable`
re-derivation spawn.

## Expected skill output

```
F-201: UNRESOLVED (gate-failure) — evidence[0] has no quote
F-202: UNRESOLVED (rederivation-dissent) — gated REAL, fable re-derived NOISE
runner_model: {"value": "opus", "source": "self-report"}, correlated with labeler A slot
```

A runner self-reporting `fable` instead: `REFUSE: runner model equals
re-deriver slot (fable)` — refused at Step 1, before Step 2's tamper guard
even runs.

## Invariants exercised

- The gate runs before re-derivation, not after: F-201 never reaches the
  `fable` spawn because `gate_label` already failed it.
- A label that passes the gate is not thereby final — F-202 shows a
  gate-clean REAL still landing UNRESOLVED on re-derivation dissent.
- `unresolved_source`'s precedence (`gate-failure > rederivation-dissent >
  labeler-contradiction > failed-tiebreak > both-unresolved`) is what
  distinguishes F-201 from F-202; both are UNRESOLVED but for different,
  individually named reasons.
- The runner never labels, gates, or re-derives anything itself — `opus`
  (correlated) and `fable` (refused) are properties of the runner's own
  recorded identity, checked once at Step 1, entirely separate from the
  per-item gate and re-derivation machinery that runs at Step 7.
