# Fixture: unverifiable-shape

A spec whose §"Invocation discipline" section is malformed / absent → verdict UNVERIFIABLE. The lint cannot read the contract and refuses to render a confident pass or fail.

## Synthetic spec stub (the `--spec` input)

> # Some skill brief
>
> ## Intent
> Does a thing.
>
> ## Scope
> In scope: the thing.

There is no `## Invocation discipline` heading and no `**Per-skill bias surfaces (forbidden):**` / `**Per-skill bloat surfaces (forbidden):**` blocks — the parse step finds nothing to check against.

## Candidate call signature (the `--call` input)

```
/some-skill --artifact content/notes/y.md
```

## Expected lint behavior

The parse step returns empty category lists. The skill produces `emitted-verdict-unverifiable`: envelope `verdict: "unverifiable"` with a single row whose `status: "unverifiable"` and `evidence-quote` instructs the operator to add an §"Invocation discipline" section to the spec. Per the lock, `unverifiable` is an escalation surface — not a pass, not a fail. In enforce mode this refuses the target skill (an unparseable contract is not a clean signature); in advisory mode it logs and runs anyway.
