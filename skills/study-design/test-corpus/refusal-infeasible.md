# Fixture: refusal-infeasible

Exercises Workflow Step 5 — the case where no catalog design's envelope can
separate the outcomes the open question cares about. This fixture's payload
is an open question rather than an artifact under probe, so the section below
is named `## Open question under design` instead of `## Artifact under
probe` — a deliberate, stated deviation on the first heading only; `##
Expected skill output` and `## Invariants exercised` stay verbatim, per the
sibling skills' fixture shape. This is the load-bearing fixture: it asserts
that the skill emits a rationale and no study document is written.

## Open question under design

```yaml
---
id: "0052"
status: open
date: 2026-06-02
tags: [review-pipeline, philosophy]
unblock-by:
  - "Is an AI-generated critique ever genuinely 'independent' of the artifact
     it critiques, in the way two human reviewers are independent of each
     other?"
---
```

Body (excerpt): the unblock-by item does not name an observable outcome —
"genuinely independent" has no operational definition that a sample, a
metric, or a stopping rule could target. Nothing distinguishes, in advance,
what a "yes" run would look like from what a "no" run would look like.

## Expected skill output

Each catalog design is considered and its envelope checked against the
question, per `references/study-catalog.md`:

- **D1** disqualified: there is no fraction-real/fraction-noise outcome to
  adjudicate here — the question is not "how many findings are correct" but
  whether the review relationship itself counts as independent, which no
  re-read of merged findings can settle either way.
- **D2** disqualified: no known-clean/known-defect distinction can be planted
  for "genuine independence" — there is no ground-truth label to seed against.
- **D3** disqualified: there is no lever whose two arms would produce a
  distinguishable outcome; both arms would run the same review mechanism, so
  an A/B comparison collapses to comparing a thing against itself.

No design's envelope separates a "yes" outcome from a "no" outcome, so the
skill stops at Workflow Step 5 rather than proceeding to Step 6.

refusal-infeasible-envelope

```yaml
infeasibility-rationale:
  oq: "0052"
  designs-considered: [D1, D2, D3]
  envelope-failure: "no candidate design defines an observable outcome that
                     would distinguish a 'yes' answer from a 'no' answer to
                     the unblock-by item; D1 has no ground truth to re-read
                     against, D2 has no label to plant, D3 has no lever whose
                     arms would differ"
  recommendation: "park — real-but-not-now, pending a reformulation of the
                    unblock-by item into an operational, observable claim"
```

No study document is written for this open question — nothing lands under
`content/evals/` or `content/benchmarks/`, and no seven-field block accompanies
this fixture anywhere. The rationale above is the only artifact this
invocation produces, and per the disposition table it is the one legitimate
input to a park.

### Second route: D1 pre-scan infeasibility (C > cap)

Workflow Step 5's second infeasibility trigger fires independently of the
envelope check above: even when D1's question shape matches, the D1 sample
pre-scan (Step 4a) can itself make the study infeasible when too much of the
census is unreachable to adjudicate. This route belongs to a separate,
D1-shaped OQ (a retrospective-adjudication census, not the philosophy
question above) whose 40-item census names `PrePass/private-audit` in 9 of
its bodies. Access to that repository has since been revoked; `git
ls-remote` against it returns:

```
ERROR: Repository not found
```

The design-time checkout's refs show no fetch history for that remote —
"no fetch history" is what the pre-scan report states for last reachability
when there is none to show. Cap at N = 40: ⌈0.10 × 40⌉ + ⌈0.05 × 40⌉ = 4 + 2
= **6**. C, the count of census items whose body names an
`evidence-scope-excluded` repository, is 9 — a mention-vs-unreachability
rate of 9/40. Because C (9) exceeds cap (6), the skill re-attempts `git
ls-remote` immediately before emitting (the pre-emission re-attempt required
by `sample-prescan.md` §The infeasibility test), confirms the exclusion
still holds, and only then emits the rationale skeleton below rather than
proceeding to Step 6:

```
infeasibility-rationale (D1 pre-scan route):
  oq: <D1 census OQ>
  trigger: pre-scan-C-exceeds-cap
  census-n: 40
  excluded-remote: PrePass/private-audit
  ls-remote-stderr: "ERROR: Repository not found"
  last-reachability: no fetch history
  c: 9
  cap: 6
  rate: 9/40
  pre-emission-reattempt: confirmed-still-excluded
  recommendation: park — measure infeasible at current scope; revisit if access is restored
```

negative-result-unreachable-by-inaccessible-remote

No study document is written for this second route either — the same
"no seven-field block anywhere" invariant holds across both routes in this
fixture, and the skeleton above is written as plain lines, never as the
frozen block, so this fixture still names no frozen block by its keyed form.

## Invariants exercised

- `refusal-infeasible-envelope` token present, asserting the infeasibility
  path fired.
- All three catalog designs are named as considered, with a per-design
  reason the envelope fails — not a bare "unmeasured."
- No study document is described or emitted; the fixture contains no seven-field
  block anywhere in its body.
- The rationale names the designs considered and why each envelope fails, per
  the disposition table's requirement that a park on infeasibility grounds
  must do so.
- `negative-result-unreachable-by-inaccessible-remote` token present,
  asserting the second, D1-pre-scan infeasibility route (C > cap) fired
  independently of the envelope-failure route above.
- The second route states C (9), cap (6, from N = 40), the rate (9/40), the
  `ls-remote` failure text verbatim, "no fetch history" for last
  reachability, and the pre-emission re-attempt — per `sample-prescan.md`
  §The infeasibility test — never a bare "unreachable."
- No study document is described or emitted for either route; the fixture
  names no frozen block, by its keyed form or otherwise, anywhere in its
  body.
