---
title: Probe templates for /load-bearing-fullread
version: 1.0
status: locked
owners: [load-bearing-fullread]
consumers: [load-bearing-fullread]
---

# Probe templates v1.0

Locked at Stage 4 (load-bearing-fullread) of the research-pipeline skill family. Skill-scoped — sibling skills do NOT REUSE this lock at v1.0. The four registered templates exhaustively cover the framing-drift failure modes catalogued in research-docs PR-4 (2026-05-16) §LLM-review pipeline corrections. Each template defines the probe-question text the skill asks against the fetched source body, the expected paper-evidence shape it looks for, and the `check-name` value emitted on detected drift per `../citation-detail-verify/references/output-schema.md` v1.0 §Check-name vocabulary §load-bearing-fullread.

Per Decision 1 of `openspec/changes/load-bearing-fullread-skill/design.md`, the four probes are universal — all run against every source regardless of detected source-type. Per-source-type filtering is a possible future optimization, not a reserved schema surface.

## Template: framing-drift-relative-vs-absolute

`registered-probe-template`: framing-drift-relative-vs-absolute.

**Probe-question text** — asked against fetched source body:
> Does the paper report a relative metric (e.g., "+43.67% F1 via aggregation") without an absolute baseline alongside? If so, what is the absolute baseline and the final absolute value of the metric? Is the artifact's framing reliant on the relative number in a way that the absolute baseline reframes?

**Expected paper-evidence shape:**
- Abstract reports `+X%` improvement or `Nx` lift on a metric.
- Paper's Methods or Results section reports the absolute baseline (e.g., "baseline F1 = 15.25%") and the absolute final value (e.g., "F1 = 21.91%").
- If artifact's framing treats the relative lift as evidence of reliable performance, the probe surfaces drift: the absolute value materially changes the framing (risk-reduction, not reliability).

**Emitted check-name** on drift detected: `framing-drift-relative-vs-absolute`.

**Reference-source pattern.** PR-4 `[A8]` SWRBench shape — "+43.67% F1 via aggregation" is relative on 15.25% baseline; final absolute 21.91% reframes the artifact as risk-reduction rather than reliability.

## Template: framing-drift-domain-transfer

`registered-probe-template`: framing-drift-domain-transfer.

**Probe-question text** — asked against fetched source body:
> What domain does the paper explicitly state it measures (e.g., policy debate, code review, undergraduate programming education)? Is the artifact applying this finding to a different domain without flagging the transfer?

**Expected paper-evidence shape:**
- Paper's Abstract, Introduction, or Methods explicitly names the measurement domain.
- Artifact's citation context applies the finding to a different domain (e.g., paper measures policy-debate overconfidence; artifact cites it for general debate-framing overconfidence including code review).
- Probe surfaces drift when the domain difference is material to the finding's validity.

**Emitted check-name** on drift detected: `framing-drift-domain-transfer`.

**Reference-source pattern.** PR-4 `[A18]` shape — paper measures debate overconfidence in policy debates; artifact treats the finding as definitional for all debate framings including code review. Also `[A5]` shape — paper measures question-specific rubrics in undergraduate programming education; artifact uses for PR review without flagging the transfer.

## Template: framing-drift-flow-direction

`registered-probe-template`: framing-drift-flow-direction.

**Probe-question text** — asked against fetched source body:
> What direction does the paper measure (e.g., LLM as second-pass filter on SAST alarms is SAST→LLM; LLM as primary reviewer with SAST as verifier is LLM→SAST)? Is the artifact's citation context mapping the finding to the reverse direction?

**Expected paper-evidence shape:**
- Paper's Methods or System Design section explicitly names the direction of measurement (e.g., "SAST detects → LLM filters" or "LLM reviews → SAST verifies").
- Artifact's citation context maps the finding to the reverse direction.
- Probe surfaces drift because finding metrics (e.g., FP-reduction rate) apply to the measured direction, not the reverse.

**Emitted check-name** on drift detected: `framing-drift-flow-direction`.

**Reference-source pattern.** PR-4 `[A10]` Tencent shape — paper measures LLM as second-pass filter on SAST alarms (SAST→LLM); the 94-98% FP-reduction applies to this direction. Artifact initially mapped to LLM-reviewer-with-SAST-as-verifier (LLM→SAST), inverting the flow.

## Template: framing-drift-scope-mismatch

`registered-probe-template`: framing-drift-scope-mismatch.

**Probe-question text** — asked against fetched source body:
> What input scope or methodology scope does the paper explicitly test (e.g., single-function benchmark like HumanEval/MBPP; multi-file PR diffs; full-repo refactor)? Is the artifact generalizing the finding to a broader scope without flagging the gap?

**Expected paper-evidence shape:**
- Paper's Methods or Experimental Setup section explicitly names the input scope (e.g., "evaluated on HumanEval and MBPP single-function tasks").
- Artifact's citation context generalizes to broader scope (e.g., multi-file PR diffs, ensemble methodology) without flagging the gap.
- Probe surfaces drift when the transfer to broader scope is unmeasured by the paper.

**Emitted check-name** on drift detected: `framing-drift-scope-mismatch`.

**Reference-source pattern.** PR-4 `[A8]` Fix-guided Verification Filter shape — paper tests on single-function benchmark code (HumanEval/MBPP); artifact generalizes to multi-file PR diffs without flagging the input-scope limit. Distinct from `framing-drift-domain-transfer` (which addresses domain X vs Y) — scope-mismatch addresses methodology breadth within a domain.

## Probe-row mapping

Each probe template emits ONE row per (source × check-name) tuple per `../citation-detail-verify/references/output-schema.md` v1.0 §Row shape. Per-row fields:

| Row field | Value derivation |
|-----------|------------------|
| `citation-id` | The artifact's local identifier for the citation (e.g., `[A8]`). From `--source-ids`. |
| `check-name` | The template's emitted check-name (one of the four `framing-drift-*` values above). |
| `status` | `pass` if probe ran and no drift detected; `fail` if probe ran and drift detected; `unverifiable` if probe could not run. |
| `cited-value` | The artifact's current framing of the cited evidence for this check (e.g., "relative +43.67% framed as reliable performance"). |
| `actual-value` | The paper's framing per probe (e.g., "+43.67% relative on 15.25% baseline; absolute final 21.91%"). |
| `evidence-quote` | Verbatim paper excerpt grounding the drift finding. MUST be non-empty on `fail` rows; MAY be empty on `pass` / `unverifiable` rows. |
| `check-detail` (optional) | Skill-specific structured metadata (e.g., `{"section": "Results", "page": 4}`). |
| `confidence` (optional) | LLM-driven probes MAY emit `high` / `medium` / `low`. |

## Versioning

- Major (`2.0`) — breaking change to template count, probe-question semantics, or check-name vocabulary. Coordinated with a PR against `../citation-detail-verify/references/output-schema.md` §Check-name vocabulary §load-bearing-fullread (the check-names registered there are the wire identifiers consumers parse).
- Minor (`1.1`) — additive only. New probe templates (5th, 6th, ...), new optional row fields, new check-detail keys. Consumers ignore unknown templates gracefully.
- v1.0 is the locked Stage 4 contract.
