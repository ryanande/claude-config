# Fixture: mode-advisory

Exercises `--mode advisory` (default): the SAME violating call signature as `mode-enforce.md`, but advisory mode logs the violation as telemetry AND lets the target skill fire.

## Synthetic spec stub (the `--spec` input)

> ## Invocation discipline
>
> **Per-skill bias surfaces (forbidden):**
> - Caller's belief about the correct value.

## Candidate call signature (the `--call` input)

```
/citation-detail-verify --artifact content/survey/x.md --expected-year 2023   # --mode advisory
```

## Expected lint behavior

In advisory mode the skill produces `emitted-telemetry-in-advisory-mode`: it writes the violation report to `~/.claude/telemetry/invocation-discipline/<run-id>.json` (the same `verdict: "fail"` envelope shape as the enforce fixture, wire `"version": "1.0"`). It then produces `ran-target-skill-in-advisory-mode`: `/citation-detail-verify` IS allowed to fire despite the violation. Advisory never blocks — the report is a signal, not a gate.
