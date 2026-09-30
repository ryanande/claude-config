---
name: study-design
description: Turn one research-docs open question into ONE pre-registered, runnable local study when its unblock-by items need evidence nobody has published. Classifies each unblock-by item on the evidence-strength ladder, selects a design from a fixed three-design catalog (D1 retrospective adjudication, D2 planted-defect corpus, D3 prospective A/B) by matching question shape, and emits a study document to research-docs content/evals/ or content/benchmarks/ carrying a frozen pre-registration block — design, metric, sample, stopping-rule, resolution, negative-result, protocol. Emits an infeasibility rationale instead when no design's envelope can separate the outcomes the question cares about; that rationale is the ONLY legitimate input to a park. Refuses caller-supplied expected results, caller-supplied metrics, caller-chosen designs, an author-chosen evidence scope, more than one open question per invocation, inventing a fourth design shape, and firing when the research-docs checkout does not resolve. Trigger with /study-design --oq <path>, "design a study for OQ-NNNN", or "what would measure this open question". PROPOSES ONLY — runs nothing, scores nothing, and never writes results; execution is /study-run.
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash, Write
---

# /study-design — one open question in, one pre-registered study out

Some open questions stall not because nobody has looked, but because nobody has
measured. `oq-resolver`'s `measure` disposition exists for exactly that gap: the
evidence available is insufficient, and a study is achievable. `study-design` is
what `measure` calls — it reads the OQ's `unblock-by` items, classifies each on
the evidence-strength ladder, and matches the ones still unresolved against a
fixed catalog of three local study designs.

A design is only useful if it can tell the outcomes apart. When none of the three
designs' envelopes can separate what the question actually asks — not "is a study
expensive" but "would any study's result change the answer" — this skill emits an
infeasibility rationale and writes nothing. That rationale is the only input the
disposition table accepts for a `park`; a park that only says "unmeasured" is not
a valid disposition.

## When to invoke

- `oq-resolver` Step 6 reaches the `measure` row of the disposition table for one
  open question.
- A human wants to know what a specific OQ-NNNN would take to actually measure,
  independent of the orchestrator.

**Don't invoke when:**
- The OQ's `unblock-by` items are already at `direct-external` or
  `measured-local` — nothing to design, the evidence already exists.
- The caller wants the study run and scored. That's `/study-run`; this skill
  proposes and never executes.
- More than one open question is in scope for the call. One OQ per invocation.

## Refusals

Refuses, per the suite's refusal discipline:
- A caller-supplied expected result for the study.
- A caller-supplied metric, overriding the one the matched design requires.
- A caller-chosen design, bypassing the catalog match in Workflow Step 4.
- More than one open question passed to a single invocation.
- A fourth design shape the caller invents — the catalog in
  `references/study-catalog.md` is fixed at three, and the config-sweep shape
  considered and excluded there is not reintroduced by request.
- An author-chosen evidence scope — D1's `protocol.evidence-scope` is derived
  by the extractor, never picked to include or exclude a remote by hand.
- A `protocol` key outside the matched design's key set — a D1-only key in a
  D2 or D3 block, or D3's adjudication keys present while `outcome.adjudicated`
  is false.
- A D2 block whose `blind-scope` carries the publication remote or an entry that
  is not path-scoped and ref-pinned, or whose `defect-classes` has an entry with
  `planted: 0`.
- A D3 arm token under four characters or on the common-word denylist — the
  blinding gate scans for it literally, so a common word fails every label.
- Firing when the `research-docs` checkout does not resolve (Step 0) — the
  skill never guesses a path or falls back to the CWD.

## Workflow

0. **Resolve the `research-docs` checkout first.** This skill writes into a
   different repository than the one it runs in, and must not guess it. Follow
   the rule `oq_select.py:179-186` establishes (`_resolve_research_docs()`):
   resolve the checkout and require it to be a directory. In THIS workspace the
   first rung is `dxroot research_docs` (`DX_ARCH_META_ROOT` is unset
   here; see `docs/research-skills-upstream.md` divergence 4); upstream's
   `$DX_ARCH_META_ROOT/repos/research-docs` is the fallback. Accept an explicit `--repo <path>` override, as
   `oq_select.py` does. When neither resolves, REFUSE with the shape
   `oq_select.py:225` emits — `"research-docs
   not resolvable (set DX_ARCH_META_ROOT or --repo)"` — and stop. Never fall
   back to the CWD or to whatever the canonical checkout happens to have
   checked out; a worktree off `origin/main` is the expected environment.
1. Resolve the `--oq <path>` argument. Refuse if more than one was passed.
1a. **Liveness.** `python3 ~/.claude/skills/study-run/scripts/recheck.py liveness --repo <R>`
    over the full `main` history fetched from the publication URL. Refuse if
    any live document names this OQ as subject. Report every
    `study-run/<id>-*` branch on the publication remote for this OQ with no
    results commit, with its reconstructed partial disposition.
2. Read the OQ's `unblock-by` items. Refuse if the caller supplied a metric, an
   expected result, or a chosen design alongside them.
3. Classify each item on the ladder per
   `~/.claude/skills/oq-resolver/references/evidence-strength.md` — rung and,
   where relevant, the six transfer axes.
4. For each item not already at `direct-external` or `measured-local`, match
   its question shape against `references/study-catalog.md`.
4a. **D1 sample pre-scan** (D1 only) per [`references/sample-prescan.md`](references/sample-prescan.md):
    run the enumerator at the pinned sample commit, derive owners, fetch the
    repo map, run the extractor, run the screen, compute cap and spawn
    budget. Commit `enumerate.py`, `repo-map.json` and the identity report
    under `assets/evals/<id>/`.
4b. **D2** — commit the manifest under `assets/benchmarks/<id>/` in the
    PUBLICATION repository (never in the corpus), pin the corpus by
    `{remote, ref, sha, path}`, and assert four invariants inline before
    emitting: the sha256 of the manifest's BYTES matches what the block records,
    no `defect-classes` entry has `planted: 0`, every `blind-scope` entry is
    path-scoped and ref-pinned, and the publication remote is absent from
    `blind-scope`. A parametrised flagger emits one study document per evaluable
    value, never a contrast inside one block.
4c. **D3** — no census exists yet, so pin RULES: the `arm-assignment` mode over
    a pre-existing identifier (no salt field — the HMAC is keyed on the study's
    own freezing commit, because an author-generated salt is both publishable and
    grindable), `enrolment` with its eligibility rule, target, deadline and
    ledger PATH, and `outcome` with its measure, source and `adjudicated` flag.
    Refuse an arm token under four characters or on `recheck.py`'s common-word
    denylist. Carry the seven adjudication keys when and only when
    `outcome.adjudicated` is true.
5. If no design's envelope separates the outcomes, OR (D1) the pre-scan's
   C exceeds the cap per `sample-prescan.md` §The infeasibility test, emit an
   infeasibility rationale and STOP. Do not emit a study document.
6. Otherwise compute the seven-field block per `references/pre-registration.md`
   — every `protocol` value is derived or pinned, never chosen — including the
   effective sample size. `protocol`'s key set is PER DESIGN: D1's fourteen
   plus `primary-value` when parametrised, D2's twelve, D3's three plus the
   conditional seven. A key outside the matched design's set is refused, not
   emitted.
7. Write the study document — `content/evals/<slug>.md` for D1 and D3,
   `content/benchmarks/<slug>.md` for D2 — and report its path and provisional
   EVAL/BENCH id. Copy the destination's own `_template.md` frontmatter
   (`content/evals/_template.md` or `content/benchmarks/_template.md`) into the
   new document verbatim, including its `build: render: never / list: never`
   block — that block is what keeps the study document off the Hugo site.
   Place the `pre-registration:` block per `references/pre-registration.md`
   §Emission shape in the document BODY, never merged into that frontmatter.
   Note that
   `content/benchmarks/_template.md` carries its own `metric:` frontmatter key
   (`p95-ms | accuracy | $/1k-tokens | ...`) — a different field and vocabulary
   than the pre-registration block's `metric:`; do not conflate the two.

## Invocation discipline

Framework: skill-invocation-discipline (`~/dx-arch-meta/repos/research-docs/content/design/skill-invocation-discipline.md`). (Upstream path, unresolvable here — `~/dx-arch-meta/repos/research-docs` is an uninitialized checkout on this machine and the doc is not mirrored into `research_docs`. Historical provenance, not a runtime dependency; the invocation-discipline rules the skill enforces are restated in this file's own §Invocation discipline.) The skill is generative — it selects a design and computes a pre-registration block — so bias control IS the design center: any caller-supplied result, metric, or design collapses the generative surface into a confirmation surface.

**IN-contract (required):**
- `--oq <path>` — the open question to design a study for.

**IN-contract (optional):**
- `--repo <path>` — explicit `research-docs` checkout override, when neither `dxroot research_docs` nor `DX_ARCH_META_ROOT` resolves one.

**Per-skill bias surfaces (forbidden — refusal-record emitted per `refusal-record.md` v1.1):**
- Caller's expected result for the study. Pre-committing an answer makes the pre-registration block a formality, not a commitment.
- Caller-chosen design, bypassing the catalog match in Workflow Step 4. The match is what makes the design defensible against the question shape, not caller preference.
- Caller-supplied metric, overriding the one the matched design's yield determines.
- Caller interpretation of the OQ — a paraphrase that pre-narrows which `unblock-by` items get classified.

**Per-skill bloat surfaces (forbidden — refusal-record emitted):**
- Attached OQ body. The skill reads the OQ from its resolved path; an attached full body invites the caller to underline a preferred passage.
- More than one open question per invocation. One OQ, one study or one infeasibility rationale — never a batch.

## Load-when table

| Step | Reference | Why load |
|------|-----------|----------|
| 1a | [`../study-run/scripts/recheck.py`](../study-run/scripts/recheck.py) `liveness` | Refuses proposal over a live document or an abandoned same-OQ attempt. |
| 3 | [`../oq-resolver/references/evidence-strength.md`](../oq-resolver/references/evidence-strength.md) | The four-rung ladder and six transfer axes, canonical there — cite, don't paraphrase. |
| 4, 5 | [`references/study-catalog.md`](references/study-catalog.md) | The fixed three-design catalog, the eval-vs-benchmark routing rule, and the recorded config-sweep exclusion. |
| 4a, 5 | [`references/sample-prescan.md`](references/sample-prescan.md) | D1's sample pre-scan report shape, the extractor pipeline, and the infeasibility test C computes against. |
| 4b, 4c, 6 | [`references/pre-registration.md`](references/pre-registration.md) (seven fields) | The seven-field block, the PER-DESIGN `protocol` key tables for D1/D2/D3, its types, and the mandatory effective-sample-size rule. |

## Self-check

Before reporting done, confirm:
- Exactly one OQ was in scope, and its path resolved.
- Every `unblock-by` item was classified on the ladder before any catalog match
  was attempted.
- Either a study document was written with all seven pre-registration fields
  present, or an infeasibility rationale was emitted and no document exists —
  never both, never neither.
- The selected design, if any, is one of D1/D2/D3 — never an invented fourth.
- `spawn-budget`, `primary-value` (when `metric: precision-contrast`),
  `population`, `stratum`, `evidence-scope`, `repo-owners`, `repo-map` hash,
  `unresolved-identities`, `clause-set` coverage (a row per census type;
  contains `screen.py` `CLAUSES` for every structural type present), the
  `cap` formula, the `screen` value, and the `precision-contrast` trigger —
  each re-derived and compared before emission, never taken from the
  pre-scan's first pass unverified.

## Success criteria

- `detect design-d1-retrospective-selected in ~/.claude/skills/study-design/test-corpus/d1-retrospective.md count >=1`
- `detect design-d2-planted-defect-selected in ~/.claude/skills/study-design/test-corpus/d2-planted-defect.md count >=1`
- `detect design-d3-prospective-ab-selected in ~/.claude/skills/study-design/test-corpus/d3-prospective-ab.md count >=1`
- `detect refusal-infeasible-envelope in ~/.claude/skills/study-design/test-corpus/refusal-infeasible.md count >=1`
- `absent pre-registration in ~/.claude/skills/study-design/test-corpus/refusal-infeasible.md`
- `detect sample-prescan-strata-declared in ~/.claude/skills/study-design/test-corpus/d1-retrospective.md count >=1`
- `detect flag-rate-forces-contrast in ~/.claude/skills/study-design/test-corpus/d1-contrast-metric.md count >=1`
- `detect negative-result-unreachable-by-inaccessible-remote in ~/.claude/skills/study-design/test-corpus/refusal-infeasible.md count >=1`
- `detect clause-set-covers-census-types in ~/.claude/skills/study-design/test-corpus/refusal-clause-set-incomplete.md count >=1`
- `detect liveness-blocks-proposal-full-history in ~/.claude/skills/study-design/test-corpus/liveness-full-history.md count >=1`

## Out of scope

- Running the study, collecting data, or scoring a result — that's `/study-run`.
- Choosing a disposition for the OQ (promote / drop / park / measure) — that's
  `oq-resolver`'s Step 6 and `references/disposition.md`.
- Inventing a fourth design shape. `references/study-catalog.md` names the one
  considered and excluded (config-sweep) and why re-adding it collapses into a
  variant of D2 once a labeled corpus exists.
- Re-deriving the evidence-strength ladder or transfer axes. Cited from
  `oq-resolver`, never copied.
