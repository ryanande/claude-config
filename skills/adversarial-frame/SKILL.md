---
name: adversarial-frame
description: Generate devil's-advocate framings of a draft decision artifact (RFC / ADR / design doc / scorecard) over its own cited evidence base, surfacing alternative interpretations, alternative weightings, and alternative compositions the author hasn't considered. Runs three frame templates per contested claim — alternative-interpretation, alternative-weighting, alternative-composition — and emits an envelope-shaped JSON report with pass/fail/unverifiable rows. Every alternative MUST be grounded in a source the artifact already cites; ungrounded contrarianism is refused. Skips settled claims via a structural rubric to prevent false-balance. Refuses caller-supplied alternative framings, biased-direction hints, per-claim confidence levels, domain-expertise hints, attached source bodies, full artifact body. Runs after /source-recency-probe + /load-bearing-fullread, before the critic gate. Trigger with /adversarial-frame --artifact <path>, "generate adversarial frames against <draft>", "devil's-advocate pass on <RFC>", or "adversarial frame on <design doc>". Generative primitive — does NOT verify what the author claimed (that's the critic gate) and does NOT discover missing citations (that's /source-recency-probe).
user-invocable: true
allowed-tools: Read, Grep, Glob, WebFetch, Bash, Write
---

# /adversarial-frame — surface alternative framings of an artifact's own evidence base

The critic pattern as practiced in this corpus catches claims the author made that the evidence does not support. It does not catch claims the author did not make that the evidence equally supports. Two failure modes survive the critic gate: **#3 selection bias** (the author chose framing A over framing B; the critic verifies A is well-supported; B is never surfaced) and **#4 synthesis-without-grounding** (the author composed five sources into one story; the critic verifies each citation supports its sentence; the composition itself is never challenged).

`/adversarial-frame` is the named generative primitive that surfaces alternative interpretations, alternative weightings, and alternative compositions of the artifact's own cited evidence. Output is a structured alternative-frames report the author MUST engage with (refute / incorporate / dismiss-with-reason) before the critic gate fires.

## When to invoke

- Author has drafted an RFC / ADR / design doc / scorecard with a stable `sources[]` citation list.
- `/source-recency-probe` and `/load-bearing-fullread` have already run — the source list and per-source framing are stable.
- Author wants the generative pass on alternative framings BEFORE the critic verifies what the artifact says.

**Don't invoke when:**
- The artifact's `sources[]` is incomplete. Use `/source-recency-probe` Stage 2 first.
- The per-source framing has not been verified for abstract-survived drift. Use `/load-bearing-fullread` Stage 4 first.
- The intent is to verify what the artifact claims is well-supported. Use the critic gate (cavecrew-reviewer) downstream.
- The intent is to discover missing citations. Use `/source-recency-probe` Stage 2.

## Input

```
/adversarial-frame --artifact <decision-artifact-path>
```

One required argument. No optional flags. Per Decision 6 of `openspec/changes/adversarial-frame-skill/design.md`, `--focus <section>`, `--stance <enum>`, and `--settled-claims <ref>` are NOT accepted at v1.0:
- `--focus <section>` is a bias surface (narrowing the input window squeezes the generative surface).
- `--stance <enum>` is a behavior knob (Decision 1's grounded-in-cited-source invariant subsumes stance calibration).
- `--settled-claims <ref>` is data-as-config NOT data-as-flag (the structural rubric in `references/frame-templates.md` §Settled-claim recognition replaces it).

- `--artifact <path>` — absolute or repo-relative path to the decision artifact under probe. The artifact MUST declare its `sources[]` citation list in a form the skill can parse (either YAML frontmatter `sources:` array OR a `## Sources` section enumerating ID → URL pairs).

## Workflow

1. **Parse input** — extract `--artifact`. Refuse if missing.
2. **Detect invocation-discipline violations** — scan the input for caller-supplied alternative framing, biased-direction hints, per-claim confidence levels, domain-expertise hints, attached source full-texts, or full artifact body when only a section is in focus. Any match → emit refusal-record per `../citation-detail-verify/references/refusal-record.md` v1.1 and short-circuit.
3. **Extract artifact claims + sources[]** — parse the artifact's `sources[]` list and enumerate the major claims under probe. Each claim is associated with its primary cited source IDs.
4. **Cache-aware WebFetch** — for each source ID in `sources[]`, fetch through the shared cache per `../citation-detail-verify/references/cache-contract.md` v1.4 §Read protocol. Cache hits surface in envelope `cache.hits`.
5. **Consult §Settled-claim recognition rubric per claim** — per `references/frame-templates.md` §Settled-claim recognition. Settled claims emit NO envelope row; the rubric short-circuits before the frame templates run. The internal-trace marker `settled-claim-skipped` is fixture-extractor target only; it is never a wire `check-name` value (the Stage 1 lock §Check-name vocabulary §adversarial-frame registers ONLY the three `surfaced-alternative-*` names).
6. **Run three frame templates per CONTESTED claim** — for each contested claim, run `alternative-interpretation`, `alternative-weighting`, `alternative-composition` per `references/frame-templates.md`. Each template emits one row per (claim × check-name) tuple.
7. **Enforce grounded-in-cited-source invariant** — every emitted `fail` row MUST carry a non-empty `evidence-quote` resolving to a citation already in `sources[]`. A frame whose alternative requires evidence NOT in `sources[]` is refused (not emitted); the discovery surface for missing evidence is `/source-recency-probe`.
8. **Per-row status assignment** — per row, status is:
   - `pass` — frame-generation ran AND no defensible alternative was found grounded in the cited evidence, OR the rubric flagged the claim settled.
   - `fail` — frame-generation ran AND surfaced a defensible alternative grounded in the cited evidence. `evidence-quote` MUST be non-empty (the verbatim source quote anchoring the alternative).
   - `unverifiable` — the cited source could not be fetched (WebFetch failure, paywalled, non-HTML mirror). `evidence-quote` MAY be empty. `actual-value` carries `<source-unfetchable>`.
9. **Compute aggregate verdict** — per `../citation-detail-verify/references/output-schema.md` (lock document frontmatter v2.0) §Verdict computation. Any `fail` → envelope `verdict: fail`. Otherwise any `unverifiable` → `verdict: unverifiable`. Otherwise `verdict: pass`.
10. **Emit envelope** — JSON conforming to `output-schema.md` §Envelope. Wire `version: "1.0"` per the lock's §Envelope.

## Success criteria

Brief `success_criteria` DSL rows verbatim (from `~/dx-arch-meta/repos/research-docs/content/notes/adversarial-frame-skill-brief.md`):

- `detect surfaced-alternative-interpretation in ~/.claude/skills/adversarial-frame/test-corpus/alternative-interpretation.md count >=1`
- `detect surfaced-alternative-weighting in ~/.claude/skills/adversarial-frame/test-corpus/alternative-weighting.md count >=1`
- `detect surfaced-alternative-composition in ~/.claude/skills/adversarial-frame/test-corpus/alternative-composition.md count >=1`
- `detect frame-grounded-in-cited-source in ~/.claude/skills/adversarial-frame/test-corpus/alternative-interpretation.md count >=1`
- `absent frame-ungrounded-in-cited-source in ~/.claude/skills/adversarial-frame/test-corpus/`
- `detect settled-claim-skipped in ~/.claude/skills/adversarial-frame/test-corpus/settled-claim.md count >=1`
- `absent adversarial-output-on-settled-claim in ~/.claude/skills/adversarial-frame/test-corpus/settled-claim.md`
- `detect emitted-verdict-pass in ~/.claude/skills/adversarial-frame/test-corpus/pass-shape.md count >=1`
- `detect emitted-verdict-fail in ~/.claude/skills/adversarial-frame/test-corpus/fail-shape.md count >=1`
- `detect emitted-verdict-unverifiable in ~/.claude/skills/adversarial-frame/test-corpus/unverifiable-shape.md count >=1`
- `detect output-row-with-all-required-fields in ~/.claude/skills/adversarial-frame/test-corpus/pass-shape.md count >=1`
- `absent output-row-missing-required-field in ~/.claude/skills/adversarial-frame/test-corpus/`
- `detect cache-hit-on-shared-fetch in ~/.claude/skills/adversarial-frame/test-corpus/shared-cache.md count >=1`
- `detect emitted-refusal-record in ~/.claude/skills/adversarial-frame/test-corpus/bad-invocations.md count >=6`
- `detect registered-frame-template in ~/.claude/skills/adversarial-frame/references/frame-templates.md count >=3`

## Invocation discipline

Framework: skill-invocation-discipline (`~/dx-arch-meta/repos/research-docs/content/design/skill-invocation-discipline.md`). The skill is inherently generative; bias control IS the design center because any caller-supplied alternative framing collapses the generative surface into a confirmation surface.

**IN-contract (required):**
- `--artifact <path>` — decision artifact under probe.

**Per-skill bias surfaces (forbidden — refusal-record emitted per `refusal-record.md` v1.1):**
- Caller's own alternative framing (e.g., `"I think the alternative is X"`). Caller-supplied alternative makes X the only one the skill produces.
- Caller's belief that the artifact is biased toward a specific direction. Frames the adversary; produces opposite-of-named-direction, missing orthogonal alternatives.
- Author's confidence level per claim (e.g., `"I'm sure about claim 1, check claim 3"`). Pre-narrows the surface; equally-contestable claims must be equally probed.
- Domain-expertise hints (e.g., `"the field has settled on X"`). Per-domain rubric is config, not per-invocation flag.

**Per-skill bloat surfaces (forbidden — refusal-record emitted):**
- Attached source full-texts. Skill fetches via WebFetch; shared cache with `/citation-detail-verify` + `/source-recency-probe` + `/load-bearing-fullread`.
- Full artifact body when only a section is in focus. Section-focus is forbidden as a bias surface (Decision 6); the skill operates on the whole artifact at v1.0.

## Load-when

| Workflow step | Reference loaded |
|---------------|------------------|
| Step 2 (refusal record) + Step 8 (per-row contract) | `../citation-detail-verify/references/refusal-record.md` v1.1 |
| Step 4 (cache read/write protocol + telemetry) | `../citation-detail-verify/references/cache-contract.md` v1.4 |
| Step 5 (settled-claim rubric) + Step 6 (frame templates) + Step 7 (grounded-in-cited-source invariant) | `references/frame-templates.md` v1.0 |
| Step 9 (aggregate verdict) + Step 10 (envelope shape) | `../citation-detail-verify/references/output-schema.md` (lock document frontmatter v2.0; wire `"1.0"`) |

## Outputs

JSON envelope per `../citation-detail-verify/references/output-schema.md` §Envelope. Wire `version: "1.0"`. `skill: "adversarial-frame"`. Rows carry exactly one of the three `surfaced-alternative-*` check-names registered at Stage 1 in `output-schema.md` §Check-name vocabulary §adversarial-frame. Rubric-flagged settled claims contribute NO envelope row; the internal-trace marker `settled-claim-skipped` is fixture-extractor target only (success-criteria grep gate), not a wire `check-name` value. Aggregate `verdict` per the lock's §Verdict computation.

## Composability

| Upstream | Pass requires |
|----------|---------------|
| `/source-recency-probe` | Source list is complete (no obvious recency gaps the discovery surface would close). |
| `/load-bearing-fullread` | Per-source framing has no abstract-survived drift. |

| Downstream | Consumes |
|------------|----------|
| Author | Engages with each `fail` row before the critic gate fires (refute / incorporate / dismiss-with-reason). **A dismiss-with-reason MUST be passed into the critic gate's brief as a named claim to attack.** Otherwise it is re-tested by nothing: the gate verifies what the artifact *claims*, so the strongest output of this skill can be argued away with no downstream check. Empirical anchor: 2026-07-28 (fmp-fleet-mgmt-planning#42) — the author dismissed a round-1 frame, and it was the verdict the artifact landed on two rounds and ~13 blocking findings later. |
| Critic gate (cavecrew-reviewer) | Verifies the adversarial-frame-engaged artifact, NOT the original draft — including any dismissed frames the author supplied per the row above. |
| Stage 6 `/criteria-validate` | Driver harness consumes the envelope's `verdict` + `rows` per the locked schema. |
