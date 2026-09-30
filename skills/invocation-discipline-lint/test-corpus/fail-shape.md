# Fixture: fail-shape

A spec + a call signature with at least one OUT-bias violation → verdict FAIL.

## Synthetic spec stub (the `--spec` input)

> ## Invocation discipline
>
> **Per-skill bias surfaces (forbidden):**
> - Pre-named findings to check for.

## Candidate call signature (the `--call` input)

```
/adversarial-frame --artifact content/rfc/0002.md --focus-on "section 3 weighting"
```

The `--focus-on` knob pre-names a finding to check for → one `bias.knob-as-hint` violation.

## Expected lint behavior

The knob-as-bias-hint detector fires. At least one row has `status: "fail"`, so by the lock §Verdict computation (`fail` dominates) the skill produces `emitted-verdict-fail`: envelope `verdict: "fail"`. In enforce mode this refuses the target skill; in advisory mode it logs and runs anyway.
