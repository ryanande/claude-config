# Fixture: spec-parse

Exercises the §"Invocation discipline" parse step — the skill must extract both the bias category list and the bloat category list from a synthetic spec stub.

## Synthetic spec stub (the `--spec` input)

> ## Invocation discipline
>
> **Dominant concern: bias.**
>
> **IN-contract (required):**
> - Artifact path.
>
> **IN-contract (optional):**
> - `--mode` stance flag.
>
> **Per-skill bias surfaces (forbidden):**
> - Caller's preferred conclusion.
> - Pre-named findings to check for.
>
> **Per-skill bloat surfaces (forbidden):**
> - Attached source full-texts.
> - Full artifact body when only a section is read.

## Candidate call signature (the `--call` input)

```
/example-skill --artifact content/survey/x.md
```

## Expected lint behavior

The parse step MUST populate `parsed-out-bias-categories` with the two bias bullets (caller's preferred conclusion; pre-named findings) and MUST populate `parsed-out-bloat-categories` with the two bloat bullets (attached source full-texts; full artifact body). Both category lists are non-empty → the spec is parseable and the lint can proceed to the detector stage. A spec missing both blocks would instead drive the `unverifiable` verdict.
