# Fixture: refusal-clause-set-incomplete

Exercises the Self-check's `clause-set` coverage requirement — a row per
census type present, not only per structural type. This fixture's payload is
an open question rather than an artifact under probe, so the section below
is named `## Open question under design` instead of `## Artifact under
probe`, per the sibling fixtures' stated deviation. This is a refusal
fixture: it asserts the skill emits nothing when the computed `clause-set`
under-covers the census.

## Open question under design

```yaml
---
id: "0058"
status: open
date: 2026-06-02
tags: [review-pipeline, documentation]
unblock-by:
  - "Of the findings a cross-artifact-type critic emits against rfc, design,
     and runbooks documents, what fraction are real?"
---
```

Body (excerpt): the OQ asks a D1-shaped question over a census that spans
three artifact types — `rfc`, `design`, and `runbooks` documents — each of
which needs its own REAL/NOISE rule before any item can be adjudicated.

## Expected skill output

D1 matches (the "of the findings X emits, what fraction are real" shape).
The census enumerator returns items of three types: `rfc`, `design`,
`runbooks`. Per `references/pre-registration.md`'s protocol table, the
`clause-set` field carries `screen.py`'s fixed `CLAUSES` text for every
`STRUCTURAL_TYPES` member present (here, only `rfc` is a `STRUCTURAL_TYPES`
member — `design` and `runbooks` are not), but the Self-check's requirement
is broader: a row **per census type present**, not only per structural type,
so `design` and `runbooks` both still need a row — `design`'s and
`runbooks`' rows just carry an author-derived REAL rule instead of
`screen.py`'s text.

The computed `clause-set` for this census carries only two rows:

```
clause-set:
  - {type: rfc,    clause: "REAL if `superseded-by` is set or a landed (accepted/decided) ADR lists this document in `decided-from`; NOISE if the proposal is still the live position."}
  - {type: design, clause: "REAL if the finding's defect is present in the design doc at the PR's base SHA; NOISE otherwise."}
```

No row exists for `runbooks`, even though the census contains `runbooks`
items. The Self-check runs the same coverage check `recheck.py`'s
`gate_label` runs at label time and fails with:

```
clause-set has no row for type runbooks
```

clause-set-covers-census-types

Because the Self-check fails before Step 6, the skill emits nothing — no
study document is written, and no seven-field block is emitted for this
census. The skill reports the missing type (`runbooks`) rather than
proceeding with a two-row `clause-set` and silently omitting one census
type's items from adjudication.

## Invariants exercised

- `clause-set-covers-census-types` token present, asserting the Self-check's
  clause-set coverage requirement fired.
- The `clause-set` failure is reported in `recheck.py`'s own error string —
  "clause-set has no row for type runbooks" — not a paraphrase, since
  `study-run`'s `gate_label` re-derives and checks this exact coverage at
  label time and the two error paths must agree.
- The `rfc` row's clause is a verbatim subset of `screen.py`'s `CLAUSES["rfc"]`
  text ("REAL if `superseded-by` is set or a landed (accepted/decided) ADR lists this
  document in `decided-from`; NOISE if the proposal is still the live
  position.") — the census includes `rfc`, so its row must carry that fixed
  text, never an author's paraphrase of it.
- No study document is described or emitted; the fixture contains no
  seven-field block anywhere in its body, and the skill's report names the
  missing census type explicitly rather than a generic "incomplete."
