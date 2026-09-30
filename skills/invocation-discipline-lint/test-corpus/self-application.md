# Fixture: self-application

Recursion-bias coverage. The skill lints ITS OWN brief plus a well-formed call signature against itself. The lint MUST pass when its own invocation is clean — otherwise the framework is rubber-stamping its own contract.

## Synthetic spec stub (the `--spec` input)

The skill's own brief — `~/.claude/skills/invocation-discipline-lint/SKILL.md` §Invocation discipline. Dominant concern: recursion-bias. 3 bias surfaces + 2 bloat surfaces declared.

## Candidate call signature (the `--call` input)

```
/invocation-discipline-lint --spec notes/load-bearing-fullread-skill-brief.md --call '/load-bearing-fullread --artifact content/rfc/0002.md --source-ids A1,A2' --mode advisory
```

Spec path + call signature + mode flag only. No caller verdict, no pre-filtered category, no caller interpretation, no attached spec body, no full-signature-when-one-knob bloat. Every declared OUT-bias / OUT-bloat surface is clean.

## Expected lint behavior

The lint walks all 3 bias + 2 bloat categories declared in its own contract; none fires. Every row is `pass` → `lint-self-application-passes` with envelope `verdict: "pass"`. The recursion guard holds: the enforcer honors the framework it enforces.
