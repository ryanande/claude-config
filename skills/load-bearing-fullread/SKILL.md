---
name: load-bearing-fullread
description: Mechanically probe every cited source's full text for abstract-survived framing drift in a decision artifact (RFC / ADR / design doc / scorecard) before the artifact lands. Runs four universal probes per source — relative-vs-absolute lift, domain-transfer scope, flow-direction reversal, single-vs-ensemble methodology-scope mismatch — and emits an envelope-shaped JSON report with pass/fail/unverifiable rows. Refuses caller-supplied framing, pre-named probe targets, attached source bodies. Cheap pre-filter; runs after /citation-detail-verify, before /adversarial-frame. Trigger with /load-bearing-fullread --artifact <path> --source-ids <ids>, "verify the framing of cited sources in <artifact>", or "load-bearing fullread on <draft>". Mechanical only — does NOT replace the citation-integrity gate (that's /citation-detail-verify) or generate alternatives (/adversarial-frame).
user-invocable: true
allowed-tools: Read, Grep, Glob, WebFetch, Bash, Write
---

# /load-bearing-fullread — probe cited sources for abstract-survived framing drift

Citation integrity is usually checked by URL liveness + verbatim-quote match. Both checks pass while the **framing** of the cited evidence is wrong — abstract reports relative lift but the paper's absolute baseline reframes the finding; abstract reports a domain-specific result but the artifact uses it as cross-domain evidence; abstract states a directional measurement but the artifact maps it to the reverse direction; abstract reports a single-scope methodology result but the artifact generalizes to a broader scope without flagging the gap.

The LLM-review pipeline pass (research-docs PR-4, 2026-05-16) touched five sources and forced material corrections on all five. `/load-bearing-fullread` packages that pass as a reusable defensive primitive between the draft and the decision: complements `/citation-detail-verify`'s citation-integrity gate, fires before `/adversarial-frame` Stage 5 generates alternatives.

## When to invoke

- Author has drafted an RFC / ADR / design doc / scorecard with N cited sources.
- `/citation-detail-verify` has already passed (URLs live, quotes verbatim, anchors resolve).
- Author wants a mechanical pass on the **framing** of cited evidence before the artifact's critic-gate fires or merges.

**Don't invoke when:**
- The artifact has zero cited external sources. There's nothing to probe.
- The intent is to generate alternative interpretations of cited evidence. Use `/adversarial-frame` Stage 5.
- The intent is to discover missing citations. Use `/source-recency-probe` Stage 2.

## Input

```
/load-bearing-fullread --artifact <decision-artifact-path> --source-ids <comma-separated-ids>
```

Two required arguments. No optional flags. Per Decisions 5-6 of `openspec/changes/archive/2026-05-20-load-bearing-fullread-skill/design.md`, `--probe-template` override and `--source-domain-hint` are NOT accepted; auto-extraction of source IDs from the artifact body via `\[A\d+\]` grep is NOT performed at v1.0.

- `--artifact <path>` — absolute or repo-relative path to the decision artifact under probe. The artifact MUST declare its `sources[]` citation list in a form the skill can parse — either a YAML frontmatter `sources:` array or a `## Sources` section enumerating ID → URL pairs, the same two forms `../adversarial-frame/SKILL.md` accepts — with each entry carrying both `id` and `url`.
- `--source-ids <ids>` — comma-separated identifier list (e.g., `A8,A10,A17,A18,A28`). Each identifier is matched against the artifact's declared `sources[]` and resolved to that entry's declared `url` per [`references/source-resolution.md`](references/source-resolution.md). URLs are NOT derived from the shape of the identifier; that rule resolves no URL for the `[Axx]` identifier form this skill documents, and §Why this file exists of that reference records why it was replaced.

An artifact that declares no `sources[]` block at all cannot be probed: its identifiers take the no-entry branch and emit `unverifiable` rows. That is not hypothetical — six `[Axx]`-using research-docs artifacts have no `sources[]` block, `content/rfc/0001-llm-review-strategy.md` (the artifact the good brief below and several `test-corpus/` fixtures name) among them. See §Coverage limit in the resolution reference.

## Source-ID input

Required at v1.0. The brief's alternative ("or a method to extract them from the artifact's body via grep") is rejected per Decision 6: the `\[A\d+\]` regex is research-docs-specific and silent extraction in other artifact shapes would emit zero `parsed-source-id-list` entries and run zero probes — silent failure mode. Future versions may add automatic extraction with explicit `--id-format` declaration; not reserved as a schema surface.

## Workflow

1. **Parse input** — extract `--artifact` + `--source-ids`. Refuse if either required arg is missing.
2. **Detect invocation-discipline violations** — scan the input for caller's interpretation of cited evidence, pre-named framing issues, author's prose excerpt, attached source full-texts, or full artifact body. Any match → emit refusal-record per `../citation-detail-verify/references/refusal-record.md` v1.4 and short-circuit. Per Decision 5 of `openspec/changes/archive/2026-05-20-load-bearing-fullread-skill/design.md`.
3. **Resolve URLs from the artifact's declared sources** — for each `--source-ids` entry, match it against the artifact's `sources[]` and take that entry's declared `url`, applying the arXiv HTML-mirror upgrade, per [`references/source-resolution.md`](references/source-resolution.md) §Resolution rule. An identifier with no matching `sources[]` entry, or a matching entry carrying no `url`, emits one `unverifiable` row per registered probe template with `check-detail` naming which of the two conditions applied. This AMENDS Decision 8's ID-shape derivation rule, which could not fire for the `[Axx]` identifier form documented above; the reference file records the amendment and what of Decision 8 is preserved.
4. **Cache-aware WebFetch** — fetch each resolved URL through the shared cache per `../citation-detail-verify/references/cache-contract.md` v1.4 §Read protocol (text-read rule: `body.txt` when present, else `body`), including its §Liveness fetch fallback ladder on failure. Cache hits surface in envelope `cache.hits` telemetry.
5. **Classify full-text availability** — per [`references/source-resolution.md`](references/source-resolution.md) §Full-text availability classification, classify each fetched body `full-text-unsectioned`, `full-text`, or `abstract-only` — route first, then content. A body that classifies `abstract-only` MUST then go through that file's §Full-text mirror hop before the classification stands — an abstract-serving landing page may still resolve to a full-text mirror elsewhere. That hop is a requirement of this skill, modeled on `cache-contract.md` §Liveness fetch fallback step 3 but NOT that ladder firing: the ladder is failure-path only, and an abstract-only landing page returns a healthy `200`. Its cost is additive to the lock's stated worst case. A body still `abstract-only` after the hop MUST then take that file's §Full-text mirror hop step 5 (PDF extraction route) before the classification stands.
6. **Run four universal probes per source** — for each fetched source body, run the four probe templates per `references/probe-templates.md` v1.0: relative-vs-absolute, domain-transfer, flow-direction, scope-mismatch. Each probe emits one row per (source × check) tuple. Per Decision 1, the four probes are universal — all four are attempted against every source regardless of detected source-type, and every one emits its row.
7. **Per-row status assignment** — per row, status is:
   - `pass` — probe ran, no drift detected (paper framing matches artifact framing for this check-name).
   - `fail` — probe ran, drift detected. `evidence-quote` MUST be non-empty (verbatim paper excerpt). Per Decision 9.
   - `unverifiable` — probe could not run (WebFetch failure, paper section missing, PDF body with no extracted text — `check-detail.reason` names why). `evidence-quote` MAY be empty.

   On an `abstract-only` body, whether a probe *ran* is decided by that template's own locked expected-evidence section, per [`references/source-resolution.md`](references/source-resolution.md) §Per-probe availability: `framing-drift-domain-transfer` lists the abstract as a grounding section, so it runs and takes `pass` or `fail` unmodified; the other three locate their evidence in Methods / Results / Experimental Setup / System Design, which an abstract does not carry, so they could not run and emit `unverifiable` with `check-detail` naming the availability class and the routes attempted. No status semantics are added or overridden here — this is `output-schema.md` §Status semantics applied per template.

   On a `full-text-unsectioned` body all four probes run over the whole body per §Per-probe availability; each row's `check-detail` carries `{"section": "unsectioned", "route": "pdf-extract"}`. `evidence-quote` on a `fail` is verbatim text from `body.txt`, matched under `cache-contract.md` v1.4 §Extracted text match key.
8. **Compute aggregate verdict** — per `../citation-detail-verify/references/output-schema.md` v2.0 §Verdict computation: any `fail` → envelope `verdict: fail`; otherwise any `unverifiable` → `verdict: unverifiable`; otherwise `verdict: pass`. Then, for every source with ≥ 1 `fail` row, disposition its proposal-time record when one exists: `python3 ~/.claude/skills/citation-detail-verify/scripts/candidates.py append-disposition --repo <root> --artifact <path> --record-id <id> --disposition corrected-at-fullread --stage load-bearing-fullread --label Minor`, resolving `<id>` via `candidates.py list --repo <root> --artifact <path>`; no matching `proposed` record → write nothing. Per `../citation-detail-verify/references/candidates-contract.md` v1.0.
9. **Emit JSON envelope** — per `../citation-detail-verify/references/output-schema.md` v2.0 §Envelope. Wire `version` field equals `"1.0"` (unchanged from lock §Shape; the locks' frontmatter versions — output-schema 2.0, cache-contract 1.4, refusal-record 1.4 — are lock-document metadata, not wire payload). Each row SHOULD carry the optional `source-url` field naming the URL the check actually ran against.

## Success criteria (DSL primitives quoted verbatim from brief)

The brief at `~/dx-arch-meta/repos/research-docs/content/notes/load-bearing-fullread-skill-brief.md` declares the property set the skill MUST exhibit. Quoting all 15 DSL rows verbatim:

- `detect framing-drift-relative-vs-absolute in ~/.claude/skills/load-bearing-fullread/test-corpus/relative-vs-absolute.md count >=1`
- `detect framing-drift-domain-transfer in ~/.claude/skills/load-bearing-fullread/test-corpus/domain-transfer.md count >=1`
- `detect framing-drift-flow-direction in ~/.claude/skills/load-bearing-fullread/test-corpus/flow-direction.md count >=1`
- `detect framing-drift-scope-mismatch in ~/.claude/skills/load-bearing-fullread/test-corpus/scope-mismatch.md count >=1`
- `detect finding-includes-paper-evidence-quote in ~/.claude/skills/load-bearing-fullread/test-corpus/relative-vs-absolute.md count >=1`
- `absent finding-missing-paper-evidence-quote in ~/.claude/skills/load-bearing-fullread/test-corpus/`
- `detect emitted-verdict-pass in ~/.claude/skills/load-bearing-fullread/test-corpus/pass-shape.md count >=1`
- `detect emitted-verdict-fail in ~/.claude/skills/load-bearing-fullread/test-corpus/fail-shape.md count >=1`
- `detect emitted-verdict-unverifiable in ~/.claude/skills/load-bearing-fullread/test-corpus/unverifiable-shape.md count >=1`
- `detect output-row-with-all-required-fields in ~/.claude/skills/load-bearing-fullread/test-corpus/pass-shape.md count >=1`
- `absent output-row-missing-required-field in ~/.claude/skills/load-bearing-fullread/test-corpus/`
- `detect cache-hit-on-shared-fetch in ~/.claude/skills/load-bearing-fullread/test-corpus/shared-cache.md count >=1`
- `detect emitted-refusal-record in ~/.claude/skills/load-bearing-fullread/test-corpus/bad-invocations.md count >=5`
- `detect parsed-source-id-list in ~/.claude/skills/load-bearing-fullread/test-corpus/pass-shape.md count >=1`
- `detect registered-probe-template in ~/.claude/skills/load-bearing-fullread/references/probe-templates.md count >=4`

Added by the candidates-capture change (back-propagate to the brief on its next edit):

- `detect corrected-at-fullread in ~/.claude/skills/load-bearing-fullread/test-corpus/candidate-disposition.md count >=1`

The `/criteria-validate` runner that turns these DSL rows into PASS / FAIL verdicts ships at a later stage in the family build per the runbook at `~/dx-arch-meta/repos/research-docs/content/runbooks/how-to-coordinate-skill-family-build.md`.

## Load-when table

| Step | Reference | Why load |
|------|-----------|----------|
| 3, 5, 7 | [`references/source-resolution.md`](references/source-resolution.md) | Declared-URL resolution rule, arXiv HTML-mirror upgrade, full-text availability classes, per-probe availability on `abstract-only` bodies, full-text mirror hop, per-venue fetch notes. Skill-scoped, `status: unlocked` — venue behaviour is revised in place. |
| 6 | [`references/probe-templates.md`](references/probe-templates.md) | Four registered probe templates + probe-question text + expected paper-evidence shape + check-name mapping. Skill-scoped v1.0 lock. The expected-evidence section named per template is also what decides per-probe availability at step 7. |
| 4 | [`../citation-detail-verify/references/cache-contract.md`](../citation-detail-verify/references/cache-contract.md) | Shared on-disk cache key derivation, meta.json shape, session-scope freshness, read protocol, §Liveness fetch fallback ladder. Stage 1 lock, frontmatter v1.4; text-read rule for `body.txt`; REUSED unchanged via relative path. |
| 8, 9 | [`../citation-detail-verify/references/output-schema.md`](../citation-detail-verify/references/output-schema.md) | Envelope + row shape, four `framing-drift-*` check-names registered under §Check-name vocabulary §load-bearing-fullread, status semantics, verdict computation, distinguishing-from-refusal convention. Stage 1 lock, frontmatter v2.0; REUSED unchanged via relative path. |
| 8 (per failing source) | [`../citation-detail-verify/references/candidates-contract.md`](../citation-detail-verify/references/candidates-contract.md) | `candidates.jsonl` record shape, `append-disposition` refusals, cross-session `--record-id` rule. Shared v1.0 lock; REUSED via relative path; helper at `~/.claude/skills/citation-detail-verify/scripts/candidates.py`. |
| 2 | [`../citation-detail-verify/references/refusal-record.md`](../citation-detail-verify/references/refusal-record.md) | Refusal-record shape (`refusal: {category, rule, evidence}`). Stage 1 lock, frontmatter v1.4; REUSED unchanged via relative path. Wire `version` field still `"1.0"` per lock §Shape (the frontmatter version is lock-document metadata). |

References load when the workflow needs them, not at skill startup. Per progressive disclosure, the SKILL.md does NOT restate probe-question text, cache key derivation, envelope shape, refusal-record fields, or per-venue fetch behaviour — each lives in its own reference file.

## Invocation discipline

Dominant concern per brief: **bias**. Direct counter to failure mode #4 synthesis-without-grounding — caller-supplied framing IS abstract-survived framing drift at the invocation surface. Skill re-derives framing from primary source; caller hint collapses the probe into confirmation of that framing. Bloat secondary — full source bodies + full artifact body are both context-window-expensive AND bias-inducing (body-level context biases framing inference toward the author's narrative).

Forbidden surfaces — each bullet is the verbatim rule the skill SHALL paste into `refusal.rule` when an invocation triggers refusal per `../citation-detail-verify/references/refusal-record.md`:

- Bias — Author's interpretation of cited evidence.
- Bias — Pre-named framing issues to check for.
- Bias — Author's prose excerpt surrounding the citation.
- Bloat — Attached source full-texts.
- Bloat — Full artifact body.

Rule rationale (NOT part of the verbatim rule; reference-only context for reviewers): caller-supplied framing of cited evidence collapses the probe into confirmation (bias 1); pre-named focus invalidates the other probes' outputs (bias 2); author's prose excerpt is the artifact-side framing the skill is independently verifying (bias 3); attached source full-texts duplicate the WebFetch the skill is doing (bloat 1); full artifact body biases framing inference toward the author's narrative (bloat 2).

Bloat rule 2 forbids the **caller attaching** the artifact body; it does not forbid the skill reading the artifact's own frontmatter `sources[]` to resolve a declared URL at step 3. That read is bounded to the citation list, is not caller-supplied, and carries none of the author's surrounding prose — the framing surface the rule exists to keep out. `../adversarial-frame/SKILL.md` sets the same precedent: it requires a parseable `sources[]` declaration and parses it, while independently forbidding a full-artifact-body attachment.

Good brief: `/load-bearing-fullread --artifact content/rfc/0001-llm-review-strategy.md --source-ids A8,A10,A17,A18,A28`. Pointer + ID list only; skill runs full probe set per source independently.

Bad brief: `/load-bearing-fullread --artifact content/rfc/0001-llm-review-strategy.md "I cited [A18] for ensemble overconfidence in §3 of the RFC, check the framing — I'm worried about relative-vs-absolute on [A8] too."` Caller's framing + pre-named probe targets; skill emits refusal record.

## Out of scope

- Auto-applying corrections to the artifact. Author applies per finding (brief §Out of scope).
- OCR of image-only PDFs. A PDF with no text layer extracts to near-zero words and classifies `abstract-only` by the word floor in `references/source-resolution.md` §Full-text availability classification. Text-layer PDFs are **in** scope from cache-contract v1.4 (§Delivered in that file); a source with an abstract-only landing page, no arXiv mirror, and no extractable PDF is probed to the extent its abstract permits — one live probe, three recorded `unverifiable` rows naming the route that failed.
- Replacing the citation-integrity gate. Both passes are needed; they catch different things. `/citation-detail-verify` verifies abstract supports claim; `/load-bearing-fullread` verifies abstract is not hiding claim's structure.
- Probing for sources NOT cited in the artifact. Defensive pass on chosen evidence, not a discovery pass. Discovery is `/source-recency-probe` Stage 2.
- Generating alternative interpretations of cited evidence. That's `/adversarial-frame` Stage 5.

## Cross-skill compatibility

This skill is the third consumer (after `/source-recency-probe` Stage 2) that REUSES all three Stage 1 locks UNCHANGED via relative path. No Stage 1 lock edits at Stage 4, and none by the declared-URL resolution change either — resolution, availability classification, and per-probe availability are all skill-scoped, and the `source-url` row field the change populates is already registered in `output-schema.md` §Optional row fields. `references/probe-templates.md` v1.0 is likewise untouched: it names no venue and no fetch route, so the availability classes read its expected-evidence sections rather than amending them.

Current lock frontmatter versions, as read at the time of this change: output-schema `2.0` (6 consumers), cache-contract `1.4` (5 consumers), refusal-record `1.4` (8 consumers). The wire `version` field this skill emits is still `"1.0"` per each lock's §Shape.

Bumping any of the three Stage 1 locks from v1.x to v2.x requires a coordinated PR across all consumers (`citation-detail-verify`, `load-bearing-fullread`, `adversarial-frame`, `source-recency-probe`, `survey-refresh`, `invocation-discipline-lint`, and — for the refusal-record lock — additionally `survey-author` and `criteria-validate`).

## Local-extractor note (dx-llm-sidecar overlay)

When `llm` is on PATH, bounded extraction sub-steps in this skill — pulling
title/author/year/quote-presence from an already-fetched source body,
clustering result rows, first-pass text matching — SHOULD run via the FREE
local sidecar (`llm --json <schema> "<extraction>" < <fetched-body>`) instead
of burning paid context on the raw text. The extraction output feeds this
skill's own mechanical checks unchanged; verdict computation, status
semantics, and row schemas are NOT delegated — the local model is an
extractor behind the contract, never a verdict author. Skip silently when
`llm` is absent.
