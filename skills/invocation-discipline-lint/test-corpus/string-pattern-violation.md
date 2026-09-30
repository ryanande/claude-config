# Fixture: string-pattern-violation

Exercises the **string-pattern** detector — a free-text payload containing framing leakage ("I think" / "I expect").

## Synthetic spec stub (the `--spec` input)

> ## Invocation discipline
>
> **Per-skill bias surfaces (forbidden):**
> - Author's interpretation of the cited evidence.

## Candidate call signature (the `--call` input)

```
/load-bearing-fullread --artifact content/rfc/0002.md "I think the [A18] framing leaks into the conclusion — I expect this fails."
```

The free-text payload carries `I think` and `I expect` — forbidden framing strings per `references/bias-pattern-rubric.md` string-pattern detector.

## Expected lint behavior

The string-pattern detector fires and the skill produces `surfaced-string-pattern-violation`: a `bias.author-interpretation` row whose `actual-value` is the offending substring `"I think the [A18] framing leaks…"` and whose `evidence-quote` suggests dropping the prose framing and passing only the artifact path. Verdict `fail`.
