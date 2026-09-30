# Fixture: envelope-shape

Exercises the 6-field row shape, the `fail`-row grounding requirement, and the absence of any
aggregate severity key on the envelope, for `/ra-pr-review`.

Markers: `envelope-row-6-field-shape`, `fail-row-requires-nonempty-evidence-quote`.

## A conformant emit (one surviving blocking finding)

`envelope-row-6-field-shape` — every row carries exactly the six required fields per
`references/envelope-schema.md` §Required row fields: `citation-id`, `check-name`, `status`,
`cited-value`, `actual-value`, `evidence-quote`. No extra row fields; no shadowing.

```json
{
  "version": "1.0",
  "skill": "ra-pr-review",
  "artifact": "https://github.com/org/repo/pull/42",
  "invoked_at": "2026-08-04T00:00:00Z",
  "verdict": "fail",
  "rows": [
    {
      "citation-id": "security-and-data-safety",
      "check-name": "lens-finding-blocking",
      "status": "fail",
      "cited-value": "loadUser(id) returns db.users.find(u => u.id === id).name without checking find's result",
      "actual-value": "find returns undefined for an unknown id, so .name throws — add a null check before .name",
      "evidence-quote": "return db.users.find(u => u.id === id).name;"
    }
  ]
}
```

The single row above is `status: fail` and carries a non-empty `evidence-quote` —
`fail-row-requires-nonempty-evidence-quote`. Per the §Envelope schema, a `fail` row MUST carry a
non-empty grounding span — here, the orchestrator's own read of the real function, not just the
diff hunk. A `pass` or `unverifiable` row MAY leave it empty.

## No aggregate severity key

Severity lives ONLY in the per-row `check-name` enum (`lens-finding-blocking |
lens-finding-should-fix | lens-finding-minor`). The envelope adds no aggregate severity key at the
top level — that would shadow the envelope, whose only top-level verdict is the 3-value `pass |
fail | unverifiable`. Only surviving `fail` rows render into the comment; the caller (you) reads
per-row severities to decide comment structure.

## Invariants exercised

- `envelope-row-6-field-shape` — exactly the six required row fields.
- `fail-row-requires-nonempty-evidence-quote` — every `fail` row's `evidence-quote` is non-empty.
- The envelope carries no aggregate severity key beyond the 3-value verdict.
