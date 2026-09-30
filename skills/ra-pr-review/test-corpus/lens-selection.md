# Fixture: lens-selection

Exercises the default lens set, the whole-diff-per-critic rule, and distinct-model-per-critic
assignment for `/ra-pr-review`.

## Default set (one fixed set, sized to k)

Marker: `lens-default-set-pr-diff`. Unlike `review-artifact`'s by-artifact-type table, PR review
has one fixed input shape — a diff — so there is a single default set:

- k=2 → `correctness`, `security-and-data-safety`. `lens-default-set-pr-diff`.
- k=3 → + `concurrency-and-performance`. `lens-default-set-pr-diff`.

`tests-and-maintainability` is in the catalog but never in a default set; it runs only when named
in `--lenses`.

## Whole diff to every critic

Marker: `whole-diff-to-every-critic`. Given PR #42 with k=2, BOTH critics receive the full diff
(every changed file), not a file-group partition. This skill tightens RFC-0018 rule 2 to
whole-diff-only, the same way `review-artifact` tightens it for whole-artifact review, because a
security or correctness defect can span multiple files in one PR. `whole-diff-to-every-critic`
holds for every lens.

## Distinct model per critic

Marker: `k-distinct-models-per-critic`. For k=2 the two critics get `opus` and `sonnet`; for k=3,
`opus`, `sonnet`, `haiku`. No model repeats across critics in one run.
`k-distinct-models-per-critic` is assigned per `references/lens-catalog.md` §Model assignment.

Example k=2 assignment:

| critic | lens | model |
|---|---|---|
| 1 | correctness | opus |
| 2 | security-and-data-safety | sonnet |

## Invariants exercised

- `lens-default-set-pr-diff` — the fixed k=2/k=3 default sets.
- `whole-diff-to-every-critic` — no partitioning, for any lens.
- `k-distinct-models-per-critic` — distinct lens AND distinct model per critic.
