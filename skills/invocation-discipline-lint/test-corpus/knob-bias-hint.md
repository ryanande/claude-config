# Fixture: knob-bias-hint

Exercises the **knob-as-bias-hint** detector — an optional knob whose NAME encodes a finding.

## Synthetic spec stub (the `--spec` input)

> ## Invocation discipline
>
> **Per-skill bias surfaces (forbidden):**
> - Expected verdict / pass-fail expectation.

## Candidate call signature (the `--call` input)

```
/criteria-validate --brief backlog/x.md --expected-verdict pass
```

The knob name `expected-verdict` matches the `expected-*` pattern in `references/bias-pattern-rubric.md` knob-as-bias-hint detector — the name alone leaks the expected finding, regardless of value.

## Expected lint behavior

The knob-as-bias-hint detector fires and the skill produces `surfaced-knob-as-bias-hint`: a `bias.knob-as-hint` row whose `actual-value` is `--expected-verdict pass` and whose `evidence-quote` suggests dropping the knob so the mechanical-verdict-from-counts protection holds. Verdict `fail`. The detector classifies on the knob name, so it fires even if the value were `fail` or empty.
