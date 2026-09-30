---
title: Mode contract for /invocation-discipline-lint
version: 1.0
status: locked
owners: [invocation-discipline-lint]
consumers: [invocation-discipline-lint]
---

# Mode contract v1.0

Locked at the ADR-0004 skill #7 build. Defines the two operating modes the skill exposes via `--mode`. The mode changes only the **terminal action** taken after the violation report is assembled — it never changes which rows are surfaced (that would be a bias knob; see SKILL.md §Invocation discipline). Both clauses below assemble the identical output-schema envelope first.

## mode-contract-clause: enforce

- **Trigger:** `--mode enforce` (the RFC-0002 continuous-worker fire path; CI flips advisory → enforce).
- **On any `fail` row:** refuse to run the target skill, emit the violation report (output-schema envelope with `verdict: "fail"`), and exit non-zero.
- **On a clean signature (`verdict: "pass"`):** allow the target skill to fire; exit zero.
- **On `verdict: "unverifiable"`:** refuse to run the target skill and exit non-zero — an unparseable contract is not a pass; the operator must fix the spec's §"Invocation discipline" section first.
- **Terminal guarantee:** a violating invocation NEVER reaches the target skill in enforce mode.

## mode-contract-clause: advisory

- **Trigger:** `--mode advisory` (default; the human-author adoption path during framework rollout).
- **On any `fail` row:** emit the violation report as telemetry at `~/.claude/telemetry/invocation-discipline/<run-id>.json`, log the violations, and **run the target skill anyway**.
- **On a clean signature:** run the target skill; write the clean report as telemetry.
- **On `verdict: "unverifiable"`:** surface the unverifiable report as telemetry and run the target skill (advisory never blocks).
- **Terminal guarantee:** the target skill ALWAYS fires in advisory mode; the report is a signal, not a gate.

## Versioning

- Major (`2.0`) — breaking change to mode semantics (renamed mode, changed terminal action). Consumers fail closed.
- Minor (`1.1`) — additive: a new mode clause, a new telemetry field. Consumers ignore unknown additions gracefully.
- v1.0 is the locked contract. Skill-scoped — no sibling skill REUSES this file.
