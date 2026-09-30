# Fixture: refusal-reachable

Exercises the refusal surface for `/ra-pr-review` — the skill refuses ONLY the invocation-
discipline violations its interface can actually carry. Marker token (one per reachable
violation): `refusal-only-reachable-violations`.

Anti-anchoring is NOT a refusal here — it is enforced by construction (no input channel), so there
is no anchoring invocation to refuse. Malformed `--k` (not `2`/`3`) is a plain parse abort, not a
refusal-record (the `{bias,bloat}` enum has no bucket for it). The six records below are the
complete reachable set, in the SKILL.md §Refusal surface table order. Each `rule` is the table's
Violation cell verbatim. All six are argument checks that run before any `gh` call — Violation 1
never reaches `gh pr view` with two PR arguments.

Wire `version: "1.0"` per `references/envelope-schema.md` §Refusal record.

## Violation 1 — more than one PR specified (bloat)

`refusal-only-reachable-violations`

```json
{
  "version": "1.0",
  "skill": "ra-pr-review",
  "invoked_at": "2026-08-04T00:00:00Z",
  "refusal": {
    "category": "bloat",
    "rule": "more than one PR specified",
    "evidence": "/ra-pr-review 42 87"
  }
}
```

## Violation 2 — lens count > 3 (over-sized ensemble) (bloat)

`refusal-only-reachable-violations`

```json
{
  "version": "1.0",
  "skill": "ra-pr-review",
  "invoked_at": "2026-08-04T00:00:00Z",
  "refusal": {
    "category": "bloat",
    "rule": "lens count > 3 (over-sized ensemble)",
    "evidence": "--lenses correctness,security-and-data-safety,concurrency-and-performance,tests-and-maintainability"
  }
}
```

## Violation 3 — `--k` ≠ `--lenses` count (when both given) (bias)

`refusal-only-reachable-violations`

```json
{
  "version": "1.0",
  "skill": "ra-pr-review",
  "invoked_at": "2026-08-04T00:00:00Z",
  "refusal": {
    "category": "bias",
    "rule": "`--k` ≠ `--lenses` count (when both given)",
    "evidence": "--k 3 --lenses correctness,security-and-data-safety"
  }
}
```

## Violation 4 — derived `k` < 2 (e.g. a single `--lenses` value) (bias)

`refusal-only-reachable-violations`

```json
{
  "version": "1.0",
  "skill": "ra-pr-review",
  "invoked_at": "2026-08-04T00:00:00Z",
  "refusal": {
    "category": "bias",
    "rule": "derived `k` < 2 (e.g. a single `--lenses` value)",
    "evidence": "--lenses correctness"
  }
}
```

## Violation 5 — unknown lens name (bias)

`refusal-only-reachable-violations`

```json
{
  "version": "1.0",
  "skill": "ra-pr-review",
  "invoked_at": "2026-08-04T00:00:00Z",
  "refusal": {
    "category": "bias",
    "rule": "unknown lens name",
    "evidence": "--lenses correctness,vibes-check"
  }
}
```

## Violation 6 — repeated lens name (bias)

`refusal-only-reachable-violations`

```json
{
  "version": "1.0",
  "skill": "ra-pr-review",
  "invoked_at": "2026-08-04T00:00:00Z",
  "refusal": {
    "category": "bias",
    "rule": "repeated lens name",
    "evidence": "--lenses correctness,correctness"
  }
}
```

## Order of evaluation

`--lenses correctness,correctness,vibes-check,correctness` violates rows 2, 5 and 6. The record's
`refusal` is row 2 (lens count > 3, `bloat`), the first in table order; rows 5 and 6 go in
`multi`. With four real lens names in the catalog, row 2 is also reachable on its own (Violation 2
above).

## Invariants exercised

- Six `refusal-only-reachable-violations` records — the complete reachable set (multi-PR, lens>3,
  k≠lens-count, derived k<2, unknown lens, repeated lens).
- Each `rule` string equals the table's Violation cell character for character.
- Malformed `--k` is NOT in this set (plain parse abort).
- Anti-anchoring is NOT in this set (structural, no input channel).
