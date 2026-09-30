# Fixture: verdict-deadcritic

Exercises the dead-critic path for `/ra-pr-review`: a critic that dies / returns null contributes
exactly ONE synthetic `unverifiable` row for its lens, and with no `fail` row present the aggregate
verdict is `unverifiable`, never `pass`.

Marker token: `verdict-deadcritic-yields-unverifiable`.

## Scenario

k=2 run over PR #42. Critic 1 (`correctness`, opus) returns cleanly with no surviving finding →
`pass`. Critic 2 (`security-and-data-safety`, sonnet) dies / returns null → one synthetic
`unverifiable` row for the `security-and-data-safety` lens.

Row set: `[pass, unverifiable]`. Per the §Verdict computation — `fail` iff ≥1 `fail`; else
`unverifiable` iff ≥1 `unverifiable`; else `pass` — there is no `fail` row and one `unverifiable`
row, so the verdict is `unverifiable`. This is `verdict-deadcritic-yields-unverifiable`: a dead lens
must escalate to the user, not silently read as a clean PR.

```json
{
  "version": "1.0",
  "skill": "ra-pr-review",
  "artifact": "https://github.com/org/repo/pull/42",
  "invoked_at": "2026-08-04T00:00:00Z",
  "verdict": "unverifiable",
  "rows": [
    {
      "citation-id": "correctness",
      "check-name": "lens-finding-should-fix",
      "status": "pass",
      "cited-value": "the diff's new retry loop terminates correctly on success",
      "actual-value": "<no-surviving-finding — critic assertion refuted on adjudication>",
      "evidence-quote": ""
    },
    {
      "citation-id": "security-and-data-safety",
      "check-name": "lens-finding-minor",
      "status": "unverifiable",
      "cited-value": "",
      "actual-value": "<critic-dead-or-null — lens ran, produced nothing checkable>",
      "evidence-quote": ""
    }
  ]
}
```

## Invariants exercised

- `verdict-deadcritic-yields-unverifiable` — `[pass, unverifiable]` → verdict `unverifiable`, never
  `pass`.
- A dead critic yields exactly one synthetic `unverifiable` row for its lens; the run continues
  with survivors.
- The comment drafted from this run posts zero findings but the user is told the
  `security-and-data-safety` lens is unconfirmed, per SKILL.md §8.
