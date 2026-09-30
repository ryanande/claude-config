# Fixture: d1-contrast-metric

Exercises the `metric: precision-contrast` branch of `references/pre-registration.md`
§Field notes — the case where the flagger under study takes more than one
evaluable parameter value, so a bare `precision` metric would hide which
value the study is actually about. This fixture's payload is an open
question rather than an artifact under probe, so the section below is named
`## Open question under design` instead of `## Artifact under probe` — the
same deliberate, stated deviation the sibling D1 fixture carries.

## Open question under design

```yaml
---
id: "0002"
status: open
date: 2026-06-02
tags: [review-pipeline, staleness]
unblock-by:
  - "At what threshold does the staleness flagger's flag rate stop tracking
     real drift and start tracking noise — 60 days, 90 days, or 180 days?"
---
```

Body (excerpt): the OQ names three evaluable threshold values for the
staleness flagger — 60, 90, and 180 days — asking which one the flagger
should actually run at. Because the OQ record names more than one evaluable
value, `metric: precision-contrast` triggers per `pre-registration.md`
regardless of the flag rate at any single value.

## Expected skill output

D1 matches (the question shape is "of the findings X emits, what fraction
are real," now asked separately per threshold). The D1 sample pre-scan
(Workflow Step 4a) enumerates the same population once and reports a
flagged column per evaluable value:

| Threshold | Flagged |
|---|---|
| 60 days | 53 |
| 90 days | 38 |
| 180 days | 0 |

The flag sets nest — everything the 90-day threshold flags is a subset of
what 60 days flags, and 180 days flags nothing at all — so the union across
all three values equals the 60-day census: N = 53. No `frozen-by-construction`
row applies (n = 0), so cap = ⌈0.10 × 53⌉ + ⌈0.05 × 53⌉ = 6 + 3 = **9**, at N
and at N minus the stratum count (53 − 0 = 53, same cap).

Per `pre-registration.md`'s `primary-value` derivation, the primary is **the
named evaluable value with the largest flag set at the pinned sample
commit** — 60 days, at 53 flagged, the largest of the three. 180 days is
named evaluable in the OQ record but flags 0 items, so it is excluded from
the primary choice by that same "largest flag set" rule; it cannot be the
primary regardless of how the OQ record orders the three values.

flag-rate-forces-contrast

```yaml
pre-registration:
  design: D1
  metric: precision-contrast
  sample: >
    53 staleness-flagged items at the 60-day threshold (the union across all
    three evaluable values, since 90 days and 180 days nest inside it) —
    single population, no PR/author clustering.
    strata:
      - {name: frozen-by-construction, rule: none-applicable, n: 0}
  stopping-rule: all 53 items in the 60-day census re-read; no new items solicited
  resolution: separates 'mostly real' (>80%) from 'mostly noise' (<40%) at the primary value's 53-item census; not 60% from 70%
  negative-result: >
    precision at the primary (60-day) value below 0.50, with UNRESOLVED at or
    under the cap of 9 = ⌈5.3⌉ + ⌈2.65⌉; AND the contrast conjunct for T=90:
    NOISE dropped − REAL dropped ≥ 0.10; T=180 has an empty flag set and is
    reported, not tested.
  protocol:
    enumerator:  assets/evals/eval-0002/enumerate.py@sha256:7b4e…
    repo-owners: [Wyatt-Rupp_prepass]
    repo-map:    assets/evals/eval-0002/repo-map.json@sha256:2d8f…
    unresolved-identities: []
    primary-value: {value: 60, oq-record-sha: 3c9d…}
    clause-set:
      - {type: content-note, clause: "REAL if the flagged item's cited source has in fact drifted since the flag date; NOISE otherwise."}
    evidence-scope:
      - {remote: https://github.com/Wyatt-Rupp_prepass/research-docs.git, ref: HEAD-at-run}
    evidence-scope-excluded: []
    labels-per-item: 2
    screen: none
    evidence-pack: citation-neighbourhood
    disagreement: ordered-3way
    model-policy: fixed-slots
    recheck: gate+rederive
    spawn-budget: {expected: 159, worst-case: 212}
```

Written to `content/evals/staleness-threshold-calibration.md`, provisional id
EVAL-NNNN (human assigns the real number at merge).

## Invariants exercised

- `flag-rate-forces-contrast` token present, asserting the precision-contrast
  branch fired because the OQ record names more than one evaluable value.
- 180 days is *named evaluable* in the OQ record but yields N = 0 at the
  pinned sample commit, so it is excluded from the primary choice by the
  "largest flag set" rule and cannot be the primary — the primary is 60
  days (53 flagged), not the first- or last-listed value.
- `protocol.primary-value` names both the value (60) and the OQ-record SHA,
  per `pre-registration.md`'s protocol table.
- `negative-result` states the contrast conjunct in the study's own terms —
  "for T=90: NOISE dropped − REAL dropped ≥ 0.10; T=180 has an empty flag set
  and is reported, not tested" — never a bare precision threshold alone.
- `spawn-budget.expected` reconciles against N = 53 and `screen: none`
  (`content-note` is not a structural type): unscreened 53 × 2 = 106,
  escalation 0, tiebreak allowance ⌈0.10 × 53⌉ = 6, one re-derivation per
  expected resolved item (53 − 6 = 47) = 106 + 0 + 6 + 47 = **159**; worst =
  53 × 4 = 212.
