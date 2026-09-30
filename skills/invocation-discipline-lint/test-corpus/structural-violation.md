# Fixture: structural-violation

Exercises the **structural** detector — an attached source full-text blob where the spec declares only a path is required.

## Synthetic spec stub (the `--spec` input)

> ## Invocation discipline
>
> **Per-skill bloat surfaces (forbidden):**
> - Attached source full-texts.

## Candidate call signature (the `--call` input)

```
/citation-detail-verify --artifact content/survey/x.md --attach-source "<<< 8400 chars of pasted paper full text >>>"
```

The `--attach-source` blob is a structural marker: an attached source full-text the skill should fetch itself.

## Expected lint behavior

The structural detector fires and the skill produces `surfaced-structural-violation`: a `bloat.attached-source` row whose `actual-value` names the structural marker (`attached-body:8400-chars`) and whose `evidence-quote` suggests dropping the blob and letting the skill WebFetch the source. Verdict `fail`. This detector inspects the call's *shape*, not its prose — no framing string is required to fire it.
