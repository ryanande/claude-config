# Fixture: k-reconciliation

Exercises the `--k` ↔ `--lenses` reconciliation rule for `/ra-pr-review`: the number of lenses
always equals `k`.

Marker token: `k-lens-count-reconciliation-rule`.

## Cases (all resolved by `k-lens-count-reconciliation-rule`)

| Invocation | Resolves to | Rationale |
|---|---|---|
| `/ra-pr-review 42` (neither given) | k=2, default set `correctness`, `security-and-data-safety` | default per `k-lens-count-reconciliation-rule` |
| `/ra-pr-review 42 --k 3` only | k=3, default set of 3 (+ `concurrency-and-performance`) | lenses = default set of size k |
| `/ra-pr-review 42 --lenses correctness,security-and-data-safety,concurrency-and-performance` only | k=3, those 3 lenses | k = lens count |
| `/ra-pr-review 42 --k 2 --lenses correctness,security-and-data-safety` | k=2, those 2 lenses | counts agree |
| `/ra-pr-review 42 --k 3 --lenses correctness,security-and-data-safety` | **refuse (`bias`)** | counts disagree — `k-lens-count-reconciliation-rule` forbids silent truncate/pad |

Each critic gets a distinct lens (no repeats) and a distinct model. Bounds: `2 ≤ k ≤ 3`. A
derived `k < 2` refuses (`bias`); a lens count `> 3` refuses (`bloat`); a malformed `--k`
(not `2`/`3`) is a plain parse abort, not a refusal-record.

## Invariants exercised

- `k-lens-count-reconciliation-rule` — lens count equals k across all input combinations;
  disagreement refuses rather than silently reconciling.
