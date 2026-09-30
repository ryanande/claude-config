# study-design — the study catalog

Loaded at Workflow Steps 4 and 5. Three designs, fixed. Each states question
shape, sample source, what it yields, what it cannot yield, cost, and the
disqualifying condition that routes a question away from it.

## D1 — retrospective adjudication

**Question shape.** "Of the findings X emits, what fraction are real?"

**Sample source.** Already exists — no new artifact authoring. Merged pull
request bodies carrying a `## Critic findings` section, `adversarial-frame`
output in `content/notes/`, and `~/.claude/telemetry/fires.jsonl`.

**Uptake is not correctness, and D1 must not conflate them.** Whether a finding
changed the diff records whether it was *acted on*. A correct finding that was
ignored would label as noise under an uptake-based label; a wrong finding that
was acted on would label as real. D1's adjudication is defined instead as
**re-reading each finding against the artifact it targeted and that artifact's
cited source**, deciding real, noise, or unresolved on that basis alone. Uptake
is recorded as a separate covariate, never as the label.

**Yields.** Precision only — no control arm, no recall — or `precision-contrast`
when the flagger is parametrised (see `pre-registration.md`).

**Cannot yield.** Recall or false-negative rate. Because it is observational, a
transfer argument is still required when generalizing the result forward.

**Cost.** Hours.

**Disqualifying condition.** The question asks for a false-negative rate, or
for what the artifact under test *misses* rather than what it *flags*. Route to
D2 instead.

**Strata.** One catalog stratum, `frozen-by-construction`: a landed artifact
asserts the item's status by design (an RFC frozen by ADR-0018's kernel
lock). Reported, never removed from the census or any conjunct.

**Re-check.** Every label passes a mechanical gate (path exists at the pinned
SHA, quote greps verbatim, clause matches the frozen `clause-set`) and a
distinct-model re-derivation; the runner adjudicates nothing. See
`study-run/references/adjudication-mechanics.md`.

## D2 — planted-defect corpus

**Question shape.** "What does X miss?"

**Sample source.** Real artifacts, seeded with N known planted defects
alongside known-clean regions. The skill under test runs blind against the
seeded corpus.

**Yields.** Precision and recall — including the false-negative rate D1 cannot
reach.

**Cannot yield.** A causal answer to "does changing lever L change the
outcome" — the corpus is fixed, not an A/B arm.

**Cost.** Corpus authoring, measured in days. The corpus is reusable across
every reliability question aimed at the same artifact kind, which is why its
document is a **benchmark** rather than an eval (see routing rule below).

**Disqualifying condition.** No planted-defect corpus is buildable for the
artifact kind in question (no known-clean region exists to seed against), or
the question is really about self-consistency under a fixed input rather than
correctness against a ground truth. The latter is the excluded config-sweep
shape below.

**Cross-repo fixture citation.** D2's seeded corpus lives in `research-skills`
(alongside the skill it tests, per that repo's `test-corpus/` convention),
while the study document it seeds lives in `research-docs`. Because the split
is cross-repo, the study document cites the corpus by an
`origin/main:<path>` git reference, never a local filesystem path — D1's
sample and D3's prospective arms carry no such fixture, so this rule binds D2
only. `protocol.corpus-ref` is that citation in machine-checkable form.

**The answer key lives in the publication repository, and blindness takes three
legs.** The manifest — the frozen `{item_id, path, region, class, planted|clean}`
rows — is committed under `assets/benchmarks/<id>/` in `research-docs`, not in the
corpus. That is necessary and not sufficient: the corpus repository's own history
carries the placement (`git log -p` recovers it), and sibling paths in the same
repository can state the counts. So `protocol.blind-scope` must omit the
publication remote, be PATH-SCOPED to the corpus subtree, and be materialized as a
history-free export — never a checkout or clone. The manifest is frozen by a
sha256 of its bytes, without which an operator who has seen the output can demote
the missed defects to `clean` and recall jumps.

**Mechanical first, residual only by spawn.** D2's primary measurement is code:
every emitted row is matched against manifest rows by region overlap and class
equality. Only the residual — a row describing a planted defect under a
different class name, a planted defect a row may cover without overlapping its
region — is adjudicated by spawn, and the UNRESOLVED cap is computed over that
residual rather than the census.

**A parametrised flagger emits one study per evaluable value.** Each parameter
value needs its own blind run against the whole corpus, so D2 has no analogue of
D1's `precision-contrast`: emit one study document per evaluable value, each
citing the same manifest and corpus ref, and compare them side by side.

## D3 — prospective A/B

**Question shape.** "Does lever L change the outcome?"

**Sample source.** The next N artifacts, run through both arms, with outcomes
logged at merge. **No census exists at design time**, so D3's `protocol:` pins
RULES rather than values: `arm-assignment`, `enrolment`, and `outcome`. The
values arrive over the study's months and land in the append-only enrolment
ledger the block pins by path.

**Yields.** The only design here that produces a causal answer.

**Cannot yield.** A fast answer — cost is months of throughput. Reserve for
levers whose answer would change standing process, not a single configuration
value.

**Cost.** Months.

**Disqualifying condition.** The lever's answer would only ever change one
local configuration value rather than standing process — the study cost is not
justified by the decision it informs. Consider D1 or D2 against existing
artifacts instead.

**Arm assignment is a pinned mode with no author-chosen salt.**
`arm-assignment.mode: hmac-sha256-parity` over a pre-existing identifier, keyed on
the study's own freezing commit SHA. Alternation by arrival order is rejected — an
author who knows the alternation state can hold work back to land it in the
preferred arm — and so is a published salt, which every author can precompute
against and the study author can grind at freeze time. A single-operator D3 still
cannot be made fully unsteerable; skipped identifiers are reported as gaps so the
attempt is visible.

**Enrolment rows carry no outcome.** Otherwise the operator holds the running
per-arm delta and can stop enrolling when the interim suits them. Outcomes are
read at score time.

**Enrolment and scoring are separate derived phases.** A months-long study
cannot be one invocation. `study-run` derives `enrol` (append ledger rows,
append no results) or `score` (read the closed ledger, measure once) from the
frozen stopping rule, never from a caller flag — so no one can ask for an early
score pass to see whether the numbers look good.

**Adjudication, when needed, is arm-blinded.** `outcome.adjudicated` says
whether the per-item outcome is mechanically readable or needs judgment. When it
needs judgment, the pack strips every arm marker and the gate fails a rationale
that names either arm.

## Eval-vs-benchmark routing rule

From `content/benchmarks/_index.md`: "if you'll run it again next month against
the same baseline, it's a benchmark." D1 and D3 studies are one-shot verdicts —
`content/evals/<slug>.md`. D2's planted-defect corpus is reusable against every
future reliability question for the same artifact kind, so its document is a
persistent regression tracker — `content/benchmarks/<slug>.md`.

## Not in the catalog: config-sweep

Considered and excluded. Holding the artifact fixed and sweeping a lever (k, model
family, brief on/off) measures self-consistency, not correctness, unless paired
with a labeled corpus — and once a labeled corpus exists it is a variation of D2,
not a distinct design. Do not reintroduce it as a fourth design; the skill refuses
inventing one.
