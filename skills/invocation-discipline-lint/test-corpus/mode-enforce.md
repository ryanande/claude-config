# Fixture: mode-enforce

Exercises `--mode enforce`: a call signature with one declared violation MUST cause the skill to refuse, emit the violation report, and exit non-zero — the target skill never fires.

## Synthetic spec stub (the `--spec` input)

> ## Invocation discipline
>
> **Per-skill bias surfaces (forbidden):**
> - Caller's belief about the correct value.

## Candidate call signature (the `--call` input)

```
/citation-detail-verify --artifact content/survey/x.md --expected-year 2023   # --mode enforce
```

The `--expected-year` knob encodes a caller belief about the correct value → one `bias.knob-as-hint` violation.

## Expected lint behavior

In enforce mode the skill produces `emitted-refusal-in-enforce-mode`: it refuses to run `/citation-detail-verify`, exits non-zero, and produces `emitted-violation-report` — the output-schema envelope below with `verdict: "fail"`.

```json
{
  "version": "1.0",
  "skill": "invocation-discipline-lint",
  "artifact": "/Users/example/notes/citation-detail-verify-skill-brief.md",
  "invoked_at": "2026-05-26T00:00:00Z",
  "verdict": "fail",
  "rows": [
    {
      "citation-id": "bias.knob-as-hint",
      "check-name": "Caller's belief about the correct value.",
      "status": "fail",
      "cited-value": "Caller's belief about the correct value.",
      "actual-value": "--expected-year 2023",
      "evidence-quote": "Drop --expected-year; let the skill fetch the year mechanically."
    }
  ]
}
```

Because the verdict is `fail` and the mode is enforce, the target skill is NOT run.
