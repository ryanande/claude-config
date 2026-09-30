# Lens catalog — named lenses, default set, k/lens reconciliation, model assignment

The named lens set, the default lens set, and the rules that reconcile `--k` with `--lenses` and
assign a distinct model per critic, for `/ra-pr-review`. Consumed by the SKILL.md procedure (lens
selection + model assignment) and by `references/brief-template.md` (each brief is generated from
a lens + its threat-model line).

## Named lenses (threat model — one line each, NO expected findings)

Each line states the **failure class** the lens hunts for — the threat model, never a checklist of
what the diff "should" contain and never a pre-named defect. These four categories are drawn
directly from this skill's own no-nits finding criteria (correctness, security, data-loss,
concurrency, contract, performance, maintainability) so the catalog doesn't invent vocabulary the
operating principles didn't already name.

- `correctness` — Logic bugs, wrong behavior on edge cases, incorrect state transitions, a
  contract/API break smuggled into the diff.
- `security-and-data-safety` — Injection, authn/authz gaps, secrets exposure, unsafe
  deserialization, an irreversible/destructive operation, data loss.
- `concurrency-and-performance` — Race conditions, unsafe shared-state mutation, a hot-path
  regression or blocking call introduced on a critical path.
- `tests-and-maintainability` — Changed behavior no test exercises, a test weakened or deleted so
  the change passes, or a maintainability hazard a reviewer would block on (logic duplicated that
  must stay in sync, a dead path left reachable). Opt-in only; not in the default set.

## Default lens set (sized to k)

PR review has one fixed input shape — a diff — so there is a single default set, unlike
`review-artifact`'s by-artifact-type table.

| k | Default set |
|---|---|
| 2 | `correctness`, `security-and-data-safety` |
| 3 | + `concurrency-and-performance` |

`tests-and-maintainability` is never picked by default; name it in `--lenses` to use it (e.g.
`--lenses correctness,security-and-data-safety,tests-and-maintainability`).

## `--k` ↔ `--lenses` reconciliation rule

The number of lenses **equals** `k`. Resolve as follows:

- **Both `--k` and `--lenses` given, counts unequal** → refuse (`bias`). Do not silently truncate
  or pad.
- **Only `--lenses` given** → `k` = the lens count.
- **Only `--k` given** → lenses = the default set of size `k`.
- **Neither given** → `k` = 2 (default); lenses = the default set of size 2.
- Each critic gets a **distinct lens** (no repeats) and a **distinct model**. A repeated lens name
  in `--lenses` → refuse (`bias`) — it would silently shrink the ensemble's lens diversity.
- Bounds: `2 ≤ k ≤ 3`. A **derived** `k < 2` (e.g. a single `--lenses` value) → refuse (`bias`,
  breaks the k≥2 ensemble invariant). A **derived** lens count > 3 → refuse (`bloat`) — reachable
  with four real lens names, since the catalog has four. An unknown lens name → refuse (`bias`).
- Checks run in the SKILL.md §Refusal surface table order; the first violation is the record's
  `refusal`, any others go in `multi`. A malformed `--k` **flag** value (anything that is not literally `2`
  or `3` — including `1`, `4`, non-numeric) → plain abort (parse error, not a refusal-record). The
  refusal path is for out-of-bounds counts *derived from `--lenses`*; a bad `--k` flag never
  reaches it.

## Model assignment (distinct model per critic)

The harness Agent-tool `model` roster is Anthropic-only (`sonnet | opus | haiku | fable`). Assign
distinct models in this order so a k=2 run gets the two strongest independent lenses:

- **k=2** → `opus`, `sonnet`
- **k=3** → `opus`, `sonnet`, `haiku`

This is same-**provider** model variation — RFC-0018 rule 4's *weaker* diversity form
("directional, never a guarantee"). Genuine cross-provider independence is an unreached residual;
the direct ground-truth adjudication (rule 6) is the primary independence lever, not model spread.
