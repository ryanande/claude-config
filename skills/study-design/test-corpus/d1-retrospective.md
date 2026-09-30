# Fixture: d1-retrospective

Exercises the D1 (retrospective adjudication) design match per
`references/study-catalog.md`. This fixture's payload is an open question
rather than an artifact under probe, so the section below is named `## Open
question under design` instead of `## Artifact under probe` — a deliberate,
stated deviation on the first heading only; `## Expected skill output` and
`## Invariants exercised` stay verbatim, per the sibling skills' fixture
shape (`grep -H "^## " skills/adversarial-frame/test-corpus/*.md`).

## Open question under design

```yaml
---
id: "0049"
status: open
date: 2026-06-02
tags: [review-pipeline, reliability]
unblock-by:
  - "Of the findings adversarial-frame emits on real research-docs PRs, what
     fraction are real vs noise?"
---
```

Body (excerpt): the OQ asks what fraction of `adversarial-frame`'s emitted
findings, across the merged PRs that already carry a `## Critic findings`
section, are real on re-read against the artifact and its cited source. No
existing measurement covers this — the unblock-by item classifies at
`folklore` on the evidence-strength ladder (codified expectation that the
skill's findings are mostly useful, no measurement behind it).

## Expected skill output

The question shape — "of the findings X emits, what fraction are real?" — is
D1's defining shape. Precision-only, sample already exists (merged PR bodies +
`content/notes/` + `~/.claude/telemetry/fires.jsonl`), no control arm needed.

design-d1-retrospective-selected

The D1 sample pre-scan (Workflow Step 4a) ran over the 144-finding, 36-PR
census at the pinned sample commit: N = 144, one `frozen-by-construction`
stratum applies at n = 0 (no landed-by-construction row in this census), so
cap = ⌈0.10 × 144⌉ + ⌈0.05 × 144⌉ = 15 + 8 = **23**, both at N and at N minus
the stratum count (144 − 0 = 144, same cap). The pre-scan report declares the
strata it found — here, none applicable — before Step 5's infeasibility
judgment runs.

sample-prescan-strata-declared

```yaml
pre-registration:
  design: D1
  metric: precision
  sample: >
    144 adversarial-frame findings clustered in 36 merged PRs, single author —
    effective n nearer 36 than 144.
    strata:
      - {name: frozen-by-construction, rule: none-applicable, n: 0}
  stopping-rule: all findings in the 36 already-merged PRs re-read; no new PRs solicited
  resolution: separates 'mostly real' (>80%) from 'mostly noise' (<40%) at n=36 clusters; not 60% from 70%
  negative-result: >
    precision = REAL / 144 below 0.50, with UNRESOLVED (every source) at or
    under the cap of 23 = ⌈14.4⌉ + ⌈7.2⌉.
  protocol:
    enumerator:  assets/evals/eval-0049/enumerate.py@sha256:3f2a…
    repo-owners: [Wyatt-Rupp_prepass]
    repo-map:    assets/evals/eval-0049/repo-map.json@sha256:9c1e…
    unresolved-identities: []
    clause-set:
      - {type: critic-finding, clause: "REAL if the finding's defect is present in the artifact at the PR's base SHA; NOISE otherwise."}
    evidence-scope:
      - {remote: https://github.com/Wyatt-Rupp_prepass/research-docs.git, ref: HEAD-at-run}
    evidence-scope-excluded: []
    labels-per-item: 2
    screen: none
    evidence-pack: citation-neighbourhood
    disagreement: ordered-3way
    model-policy: fixed-slots
    recheck: gate+rederive
    spawn-budget: {expected: 432, worst-case: 576}
```

Written to `content/evals/adversarial-frame-precision-retrospective.md`,
provisional id EVAL-NNNN (human assigns the real number at merge).

## Invariants exercised

- `design-d1-retrospective-selected` token present, asserting the D1 match.
- `sample-prescan-strata-declared` token present, asserting the pre-scan's
  strata declaration ran before Step 5.
- The pre-registration block carries all seven fields, matching
  `references/pre-registration.md`.
- `screen: none` because `critic-finding` is not a structural type, so the
  escalation allowance is 0; `spawn-budget.expected` = unscreened 144 × 2 +
  escalation 0 + tiebreak allowance ⌈0.10 × 144⌉ = 15 + one re-derivation per
  expected resolved item (144 − 15 = 129) = 288 + 0 + 15 + 129 = **432**;
  worst = 144 × 4 = 576. The pre-scan report states the expected-resolved
  estimate it used (here N minus the tiebreak allowance).
- `resolution:` names the comparisons foreclosed in the study's own numbers
  (36 clusters, 60% vs 70%), not a generic band.
- `sample:` states the clustering structure (PR, then author) rather than a
  bare count.
