# Fixture: d2-planted-defect

Exercises the D2 (planted-defect corpus) design match per
`references/study-catalog.md`. This fixture's payload is an open question
rather than an artifact under probe, so the section below is named `## Open
question under design` instead of `## Artifact under probe` — a deliberate,
stated deviation on the first heading only; `## Expected skill output` and
`## Invariants exercised` stay verbatim, per the sibling skills' fixture
shape.

## Open question under design

```yaml
---
id: "0050"
status: open
date: 2026-06-02
tags: [review-pipeline, reliability]
unblock-by:
  - "What does citation-detail-verify miss — its false-negative rate on
     broken citations it does not flag?"
---
```

Body (excerpt): OQ-0049's sibling — asks for the miss rate, not the hit rate.
No retrospective corpus of merged PRs carries labeled *missed* defects (a
finding that never fired leaves no trace to re-read), so D1 cannot answer
this shape. The unblock-by item classifies at `folklore` on the ladder.

## Expected skill output

The question shape — "what does X miss?" — is D2's defining shape; D1 is
disqualified because it has no sample source for false negatives (nothing to
re-read when the skill stays silent). A planted-defect corpus is buildable:
citation-integrity defects (dead URL, mismatched title, missing anchor) can be
seeded into known-clean research-docs artifacts alongside clean regions.

design-d2-planted-defect-selected

```yaml
pre-registration:
  design: D2
  metric: recall
  sample: "40 planted citation defects across 10 seeded artifacts (4 defects
           each) plus 40 known-clean citations in the same artifacts —
           clustered by artifact, effective n nearer 10 than 80"
  stopping-rule: "all 10 seeded artifacts scored once by
                  citation-detail-verify, run blind to defect placement"
  resolution: "separates recall above vs below 70% at n=10 artifact clusters;
               does not separate 80% from 90%"
  negative-result: >
    citation-detail-verify flags fewer than half of the 40 planted defects.
    An UNRESOLVED residual item stays in the denominator of whichever metric it
    bears on; the cap is counted over the RESIDUAL, reported alongside the
    manifest's 80 rows.
  protocol:
    corpus-manifest: assets/benchmarks/0007/manifest.json@sha256:3f1c9d2ab84e5077c1de6b0f4a29e8135c7d0b62f4ae918d3c52760bb1e4a9d0
    corpus-ref:      {remote: https://github.com/Wyatt-Rupp_prepass/research-skills.git, ref: origin/main, sha: 072ddd2, path: skills/citation-detail-verify/test-corpus/seeded/}
    blind-scope:     [{remote: https://github.com/Wyatt-Rupp_prepass/research-skills.git, ref: 072ddd2, path: skills/citation-detail-verify/test-corpus/seeded/}]
    defect-classes:
      - {class: dead-url,      planted: 14, clean-controls: 14}
      - {class: title-drift,   planted: 13, clean-controls: 13}
      - {class: missing-anchor, planted: 13, clean-controls: 13}
    match:           region-overlap+class-equality
    match-rule:      "<verbatim MATCH_RULE from study-run/scripts/recheck.py>"
    labels-per-item: 2
    evidence-pack:   defect-neighbourhood
    disagreement:    ordered-3way
    model-policy:    fixed-slots
    recheck:         gate+rederive
    spawn-budget:    {skill-runs: 10, adjudication-expected: 24, worst-case: 96}
```

The manifest is committed in the PUBLICATION repository under
`assets/benchmarks/0007/`, never in the corpus. Repository granularity alone would
not be enough: the corpus repository's own history carries the placement, and this
very fixture states the per-class counts a few lines above. So `blind-scope` omits
the publication remote, is path-scoped to the seeded subtree, and is materialized
as a history-free `git archive` export at `corpus-ref.sha` — the export the skill
under test actually reads carries no `.git`, so `git log -p` cannot recover the
planting commit. `corpus-manifest`'s sha256 is hashed from the file's bytes at run
time, so the answer key cannot be edited after the output is seen.

`citation-detail-verify` is not parametrised here, so this is one study. Were it
parametrised, D2 would emit one study document per evaluable value rather than a
`precision-contrast` conjunct: `primary-value` and `precision-contrast` are
D1-only.

Written to `content/benchmarks/citation-detail-verify-recall-planted.md`
(benchmark, not eval — the corpus is reusable across every future reliability
question against the same artifact kind, per the eval-vs-benchmark routing
rule), provisional id BENCH-NNNN.

## Invariants exercised

- `design-d2-planted-defect-selected` token present, asserting the D2 match.
- The pre-registration block carries all seven fields, and `protocol` carries
  the twelve-key D2 set — no `enumerator`, `repo-owners`, `repo-map`,
  `unresolved-identities`, `clause-set`, `evidence-scope`,
  `evidence-scope-excluded`, `screen`, or `primary-value`.
- `corpus-manifest` resolves in the publication repository, and `blind-scope`
  omits that remote, is path-scoped, and is ref-pinned — the three legs blindness
  actually needs, since repository granularity alone leaves the corpus history and
  its sibling paths readable.
- No `defect-classes` entry records `planted: 0`.
- Each `defect-classes` count matches the manifest, and the manifest's rows carry
  well-formed `[start, end)` regions with unique ids — a degenerate region can
  never overlap, which would silently reclassify every false positive over it as
  residual.
- The cap and the UNRESOLVED denominator are stated over the RESIDUAL, not the
  manifest's row count.
- The document routes to `content/benchmarks/`, not `content/evals/`, per the
  routing rule the catalog states.
- `resolution:` states the foreclosed comparison in the study's own numbers
  (10 clusters, 80% vs 90%), not a generic band.
