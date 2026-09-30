# Fixture: d3-prospective-ab

Exercises the D3 (prospective A/B) design match per
`references/study-catalog.md`. This fixture's payload is an open question
rather than an artifact under probe, so the section below is named `## Open
question under design` instead of `## Artifact under probe` — a deliberate,
stated deviation on the first heading only; `## Expected skill output` and
`## Invariants exercised` stay verbatim, per the sibling skills' fixture
shape.

## Open question under design

```yaml
---
id: "0051"
status: open
date: 2026-06-02
tags: [review-pipeline, process]
unblock-by:
  - "Does requiring a pre-registered `## Critic findings` section on a PR
     (vs leaving critique optional) change the merged-PR defect escape rate?"
---
```

Body (excerpt): asks whether a standing-process lever — making the critic
section mandatory — changes an outcome, not what an existing artifact's
findings look like in retrospect. No corpus of already-run "mandatory vs
optional" PRs exists to re-read; the comparison has never been run. The
unblock-by item classifies at `folklore` on the ladder.

## Expected skill output

The question shape — "does lever L change the outcome?" — is D3's defining
shape, and it is the only design here that yields a causal answer. D1 and D2
are disqualified: both require a fixed artifact set scored after the fact,
and this question is about a process choice going forward. The lever (mandatory
critic section) is judged to change standing process for every future PR
rather than one configuration value, satisfying D3's cost bar.

design-d3-prospective-ab-selected

```yaml
pre-registration:
  design: D3
  metric: defect-escape-rate-delta
  sample: "next 60 merged research-docs PRs, arms assigned by the frozen
           hmac-sha256-parity rule over the PR number, keyed on this study's own
           freezing commit — clustered by author (roughly 4 authors active),
           effective n nearer 4 author-clusters than 60 PRs"
  stopping-rule: "60 PRs merged across both arms, or 6 months elapsed,
                  whichever comes first"
  resolution: "separates a large defect-escape-rate delta (>20 points)
               between arms at ~4 author clusters; does not separate a
               5-point delta"
  negative-result: "the escape rate in the mandatory arm is not lower than
                     the optional arm across the full run"
  protocol:
    arm-assignment: {mode: hmac-sha256-parity, identifier: pr-number, arms: [mandatory-critic, optional-critic]}
    enrolment:      {eligibility: "a research-docs PR merged to main that changes at least one file under content/, excluding PRs whose only changes are to _index.md files", target-n: 60, deadline: 2027-03-07, ledger: assets/evals/0008/enrolment.jsonl}
    outcome:        {measure: "a defect escaped when a commit merged after this PR reverts or corrects a line this PR introduced, and cites this PR by number", source: "git log over content/ at each enrolled PR's merge SHA", at: merge, adjudicated: false}
```

`outcome.adjudicated` is false, so this block carries three `protocol` keys and
no adjudication group: the outcome is read mechanically from git history, no
labeling spawn fires, no cap applies, and Step 7 gates each recorded outcome's
CITATION at the enrolled PR's merge SHA rather than a label. Were the outcome a
judgment instead, the block would additionally carry `evidence-scope-rule`,
`labels-per-item`, `evidence-pack: arm-blinded-artifact`, `disagreement`,
`model-policy`, `recheck`, and `spawn-budget`.

Arms are not assigned alternately, and there is no salt field. Alternation by
arrival order is steerable — an author who knows the alternation state can hold a
PR back to land it in the preferred arm — and an author-generated salt is no
better, because the block publishes it and the study author can grind salts at
freeze time until the assignment they want falls out. The HMAC is keyed on this
study's own freezing commit SHA, which the tamper guard already pins and nobody
chooses; `study-run` recomputes every ledger row's arm from it at Step 3a.

The arm tokens are `mandatory-critic` and `optional-critic`, not `mandatory` and
`optional`. The blinding gate scans for the token literally, and `optional` is a
common word that ordinary review prose would trip, failing every label.

A single-operator D3 is still not fully unsteerable: this study's author also
authors the PRs, so once the freezing commit exists they can compute their own arm
and bump the PR number by opening a throwaway issue. `recheck.py enrolment`
reports skipped identifiers as `gaps`, so the attempt is visible in the run
record rather than foreclosed.

Enrolment spans months, so `study-run` derives its phase from this stopping rule:
`enrol` until 60 PRs or 2027-03-07, appending ledger rows and no results; `score`
once, thereafter. The phase subcommand takes no date argument, and it counts only
a ledger that validated. Enrolment rows carry no outcome and no arm split, so the
running per-arm delta is not there for the operator to read between passes.

Written to `content/evals/critic-section-mandatory-vs-optional-ab.md`,
provisional id EVAL-NNNN.

## Invariants exercised

- `design-d3-prospective-ab-selected` token present, asserting the D3 match.
- The pre-registration block carries all seven fields, and `protocol` carries
  the three-key D3 base set with no adjudication group, because
  `outcome.adjudicated` is false.
- `arm-assignment` is the pinned `hmac-sha256-parity` mode over a pre-existing
  identifier, never an arrival-order alternation, and it carries no salt field —
  the key is the study's freezing commit.
- Both arm tokens are at least four characters and off the common-word denylist,
  so the literal blinding scan cannot fail every label.
- `enrolment.ledger` is a PATH, carrying no sha256 — none could exist before
  enrolment begins.
- `metric` names a rate DELTA between arms, matching the terms `resolution` and
  `negative-result` are already stated in.
- `resolution:` names the foreclosed comparison in the study's own numbers
  (4 author clusters, 20-point vs 5-point delta), not a generic band.
- `sample:` states the clustering structure (author) rather than a bare PR
  count.
