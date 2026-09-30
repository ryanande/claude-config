# Fixture: pass-shape

A spec + a clean call signature with no violations → verdict PASS, and the emitted row populates every required field of the locked row shape.

## Synthetic spec stub (the `--spec` input)

> ## Invocation discipline
>
> **IN-contract (required):**
> - Spec path.
> - Call signature.
>
> **Per-skill bias surfaces (forbidden):**
> - Caller's belief about whether the call signature passes.

## Candidate call signature (the `--call` input)

```
/source-recency-probe --artifact content/survey/x.md
```

Pointer only — no forbidden surface present.

## Expected lint behavior

No detector fires. The skill produces `emitted-verdict-pass`: an envelope with `verdict: "pass"`. The clean-on-this-rule row demonstrates `output-row-with-all-required-fields` — all six required fields of the locked row shape are present and non-empty per the lock's empty-string rules:

```json
{
  "version": "1.0",
  "skill": "invocation-discipline-lint",
  "artifact": "/Users/example/notes/source-recency-probe-skill-brief.md",
  "invoked_at": "2026-05-26T00:00:00Z",
  "verdict": "pass",
  "rows": [
    {
      "citation-id": "bias.caller-verdict",
      "check-name": "Caller's belief about whether the call signature passes.",
      "status": "pass",
      "cited-value": "Caller's belief about whether the call signature passes.",
      "actual-value": "",
      "evidence-quote": ""
    }
  ]
}
```

On a `pass` row, `actual-value` and `evidence-quote` MAY be the literal empty string per the lock — that is still a complete row (every key present), not a row that omits a key. A row that dropped one of the six keys entirely would be malformed and fail the schema; this fixture deliberately shows the complete-row shape instead.
