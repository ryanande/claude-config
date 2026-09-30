---
name: invocation-discipline-lint
description: Mechanically lint a candidate invocation call signature against a spec's declared "Invocation discipline" section — surfaces OUT-bias / OUT-bloat violations (caller verdict, pre-filtered focus, caller interpretation, attached spec body, full-signature bloat) as output-schema rows before the target skill fires. Two modes — enforce (refuse + exit non-zero, CI fire path) and advisory (log + run anyway, default). Promotes the skill-invocation-discipline framework from author-time discipline to fire-time property across the skill-invocation and subagent-spawn surfaces. Trigger with /invocation-discipline-lint --spec <path> --call <signature>, "lint this invocation", or "check this call signature against its contract". Enforcement layer — does NOT validate spec quality (out of scope) or auto-correct violations.
user-invocable: true
allowed-tools: Read, Grep, Write
---

# /invocation-discipline-lint — fire-time enforcement of invocation discipline

The enforcement layer (skill #7) of the ADR-0004 research-pipeline family. Per the founding design note at `~/dx-arch-meta/repos/research-docs/content/notes/invocation-discipline-lint-skill-brief.md`, the [skill-invocation-discipline](file:///Users/wyatt.rupp/dx-arch-meta/repos/research-docs/content/design/skill-invocation-discipline.md) framework lives as author-time documentation today. Author-time discipline decays. This skill checks every candidate call signature against the spec's declared §"Invocation discipline" section at fire time — promoting the framework from a discipline (decays) to a property (holds).

## When to invoke

- A caller (human or the RFC-0002 continuous worker) is about to invoke a sibling skill and wants the call signature checked against the target skill's contract first.
- A parent agent is about to spawn a subagent and wants the Agent-tool payload checked against the subagent contract (`skill-invocation-discipline` §"Application to subagent-spawn surface").
- In CI (`--mode enforce`) ahead of any continuous-worker skill fire.

**Don't invoke when:**
- You want to validate the *spec itself* — that's out of scope (spec-quality validation is a different surface).
- You want the violations auto-fixed — the skill surfaces violations + suggested corrections; the caller fixes them.
- The spec has no §"Invocation discipline" section — the skill returns `unverifiable`; fix the spec first.

## Input

```
/invocation-discipline-lint --spec <spec-path> --call <call-signature> [--mode enforce|advisory] [--format markdown|json]
```

- `--spec <spec-path>` (required) — a skill brief (`notes/<name>-skill-brief.md`) OR a SKILL.md. Read from disk; the skill resolves the §"Invocation discipline" section itself.
- `--call <call-signature>` (required) — the invocation about to fire: slash-command args, parsed kwargs, attached files, or an Agent-tool spawn payload.
- `--mode enforce|advisory` (optional; default `advisory`) — terminal action per [`references/mode-contract.md`](references/mode-contract.md). Behavioral contract, not a bias knob.
- `--format markdown|json` (optional; default `markdown`) — rendering only (data-not-knob).

No bias knobs. The skill walks every OUT-bias / OUT-bloat category declared in the spec; a caller-directed focus, verdict, or interpretation is a forbidden surface (see §Invocation discipline) and is refused.

## Workflow

1. **Parse the spec** — Read `--spec`; extract the §"Invocation discipline" section via regex on the bolded heading lines (`**IN-contract (required):**`, `**IN-contract (optional):**`, `**Per-skill bias surfaces (forbidden):**`, `**Per-skill bloat surfaces (forbidden):**`) + the dominant-concern call-out. Collect the bullet list under each heading. A malformed / absent section → `verdict: "unverifiable"`.
2. **Parse the call signature** — `--call` into named args, free-text payload, and attached blobs.
3. **Run the three mechanical detectors** per [`references/bias-pattern-rubric.md`](references/bias-pattern-rubric.md): **string-pattern** (forbidden framing strings in free-text), **structural** (attached body / multi-spec / full-signature bloat), **knob-as-bias-hint** (`expected-*` / `looks-*` / `focus-on-*` / `worry-about-*` knob names). One row per (declared OUT-bias / OUT-bloat rule, firing).
4. **Assemble the envelope** — JSON per [`../citation-detail-verify/references/output-schema.md`](../citation-detail-verify/references/output-schema.md) §invocation-discipline-lint: `citation-id` = `violation_class` (`bias.*` / `bloat.*`); `check-name` = the declared rule bullet; `cited-value` = declared rule; `actual-value` = `evidence_in_call`; `evidence-quote` = `suggested_correction`. Compute `verdict` per the lock §Verdict computation.
5. **Mode-dispatch** per [`references/mode-contract.md`](references/mode-contract.md): `enforce` → on any `fail` / `unverifiable`, refuse + emit report + exit non-zero; `advisory` → emit report as telemetry + run the target skill anyway.
6. **Refuse forbidden self-invocations** — if `--call` (or the invocation of *this* skill) carries a forbidden bias / bloat surface, emit a refusal record per [`../citation-detail-verify/references/refusal-record.md`](../citation-detail-verify/references/refusal-record.md) and do not proceed.

## Success criteria (DSL primitives quoted verbatim from brief)

- `detect parsed-out-bias-categories in ~/.claude/skills/invocation-discipline-lint/test-corpus/spec-parse.md count >=1`
- `detect parsed-out-bloat-categories in ~/.claude/skills/invocation-discipline-lint/test-corpus/spec-parse.md count >=1`
- `detect emitted-refusal-in-enforce-mode in ~/.claude/skills/invocation-discipline-lint/test-corpus/mode-enforce.md count >=1`
- `detect emitted-violation-report in ~/.claude/skills/invocation-discipline-lint/test-corpus/mode-enforce.md count >=1`
- `detect emitted-telemetry-in-advisory-mode in ~/.claude/skills/invocation-discipline-lint/test-corpus/mode-advisory.md count >=1`
- `detect ran-target-skill-in-advisory-mode in ~/.claude/skills/invocation-discipline-lint/test-corpus/mode-advisory.md count >=1`
- `detect surfaced-string-pattern-violation in ~/.claude/skills/invocation-discipline-lint/test-corpus/string-pattern-violation.md count >=1`
- `detect surfaced-structural-violation in ~/.claude/skills/invocation-discipline-lint/test-corpus/structural-violation.md count >=1`
- `detect surfaced-knob-as-bias-hint in ~/.claude/skills/invocation-discipline-lint/test-corpus/knob-bias-hint.md count >=1`
- `detect lint-self-application-passes in ~/.claude/skills/invocation-discipline-lint/test-corpus/self-application.md count >=1`
- `detect emitted-verdict-pass in ~/.claude/skills/invocation-discipline-lint/test-corpus/pass-shape.md count >=1`
- `detect emitted-verdict-fail in ~/.claude/skills/invocation-discipline-lint/test-corpus/fail-shape.md count >=1`
- `detect emitted-verdict-unverifiable in ~/.claude/skills/invocation-discipline-lint/test-corpus/unverifiable-shape.md count >=1`
- `detect output-row-with-all-required-fields in ~/.claude/skills/invocation-discipline-lint/test-corpus/pass-shape.md count >=1`
- `absent output-row-missing-required-field in ~/.claude/skills/invocation-discipline-lint/test-corpus/`
- `detect emitted-refusal-record in ~/.claude/skills/invocation-discipline-lint/test-corpus/bad-invocations.md count >=5`
- `detect registered-detector in ~/.claude/skills/invocation-discipline-lint/references/bias-pattern-rubric.md count >=3`
- `detect mode-contract-clause in ~/.claude/skills/invocation-discipline-lint/references/mode-contract.md count >=2`

The `test-corpus/` fixtures these rows resolve against ship in this change; `/criteria-validate` turns the rows into pass / fail verdicts at Gate 7.

## Load-when table

| Step | Reference | Why load |
|------|-----------|----------|
| 3 | [`references/bias-pattern-rubric.md`](references/bias-pattern-rubric.md) | The three registered detector classes + default pattern sets. v1.0 skill-scoped lock. |
| 5 | [`references/mode-contract.md`](references/mode-contract.md) | enforce / advisory terminal actions. v1.0 skill-scoped lock. |
| 4 | [`../citation-detail-verify/references/output-schema.md`](../citation-detail-verify/references/output-schema.md) | Envelope + row shape, verdict computation, §invocation-discipline-lint check-name mapping. frontmatter v2.0 lock; REUSED via relative path. |
| 6 | [`../citation-detail-verify/references/refusal-record.md`](../citation-detail-verify/references/refusal-record.md) | Refusal-record shape for forbidden-surface invocations. v1.x lock; REUSED via relative path. |

No `cache-contract.md` REUSE — this skill has no WebFetch surface; it reads the spec from disk and the call signature from the payload. References load on demand, not at startup; each is self-contained per progressive disclosure.

## Invocation discipline

Framework: [skill-invocation-discipline](file:///Users/wyatt.rupp/dx-arch-meta/repos/research-docs/content/design/skill-invocation-discipline.md). **Dominant concern: recursion-bias** — this skill enforces the framework on others; its OWN invocation MUST honor it or the enforcement is rubber-stamping. Strictest discipline of any skill in the family.

**IN-contract (required):** spec path; call signature.
**IN-contract (optional):** `--mode enforce|advisory` (default advisory); `--format markdown|json`.

**Per-skill bias surfaces (forbidden)** — refuse with a refusal record:
- Caller's belief about whether the call signature passes. A pre-determined verdict IS the recursion failure — the skill would confirm it from extracted patterns.
- Pre-filtered violation category to check. The lint walks all declared OUT-bias + OUT-bloat categories; caller-directed focus invalidates the universal-pass guarantee.
- Caller's interpretation of the call signature's intent. The lint reads what's there mechanically; intent is the spec's to declare, not the caller's to assert.

**Per-skill bloat surfaces (forbidden):**
- Attached spec body. The lint reads §"Invocation discipline" from disk by spec path; a pasted body bypasses the content-key.
- Full call signature when only one knob is in question. v0 lints whole-signature only.

**Bad:** `/invocation-discipline-lint --spec notes/x-skill-brief.md --call '...' "I think this leaks — flag if so."` — pre-determined verdict; refuse.
**Good:** `/invocation-discipline-lint --spec notes/x-skill-brief.md --call '/x --artifact ... "I cited [A18], check the framing"' --mode advisory` — spec + call + mode only.

## Pipeline composition

Sits **upstream of every other skill at the invocation surface** — it fires before the target skill receives input, gating the call. Concretely, in the research-then-decide chain (`/source-recency-probe → /citation-detail-verify → /load-bearing-fullread → /adversarial-frame`) and at the highest-stakes verdict surface (`/criteria-validate`), this lint runs against each skill's call signature *before* that skill fires — not as a chain stage between siblings, but as a per-invocation gate wrapping each of them. In `enforce` mode it is the RFC-0002 continuous-worker's pre-fire check; in `advisory` mode it is a passive telemetry tap that never blocks.

At the **subagent-spawn surface** the same gate wraps `Agent.spawn`: the parent agent lints the Agent-tool payload against the subagent contract before the spawn fires (per `skill-invocation-discipline` §"Application to subagent-spawn surface").

```
caller call signature ─► /invocation-discipline-lint ─► (enforce+violation: refuse) | (advisory or clean: target skill fires)
parent Agent payload  ─► /invocation-discipline-lint ─► (refuse | proceed) ─► Agent.spawn
```

Counters silent contract drift at fire time across both surfaces — promoting the framework from author-time discipline to fire-time property.

## Out of scope

- Auto-correcting violations — surfaces the violation + suggested correction; the caller fixes it.
- Validating spec quality — checks invocations against a spec, not the spec itself.
- Inferring which knobs are bias hints in general — reads the spec's declaration + the default rubric; cross-spec inference is a follow-on.
- Hard harness-surface enforcement of subagent spawns when the parent doesn't call this skill — a separate, larger spec.
