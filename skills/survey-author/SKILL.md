---
name: survey-author
description: Author a new external-evidence survey doc (literature review, landscape scan, state-of-the-art) — scaffold the frontmatter and section structure AND run the evidence walk that fills it, with source-tier classification and refresh-in-place cadence convention. Refuses caller-supplied recommendations / per-source interpretations / expected verdicts. Counters failure modes #3 selection-bias and #7 verdict-creep by separating "describe the landscape" (survey) from "decide what to do" (RFC). Trigger with /survey-author --question <claim> --tags <topic-tags> --target-repo <path>, "scaffold a survey on <topic>", or "start a literature review on <topic>". Runs at survey-creation time AND at refresh time.
user-invocable: true
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch, Bash, Write
---

# /survey-author — author a new external-evidence survey doc

> **Adopted from [Wyatt Rupp's claude-config](https://github.com/Wyatt-Rupp_prepass/claude-config) `skills/survey-author/`** (2026-06-09), faithfully.
> 1. ~~`refusal-record.md` vendored~~ — **resolved 2026-07-14**: `citation-detail-verify` and the rest of the verify chain are now ported as true siblings, so this skill's refusal-record references were restored to shared relative-path REUSE via `../citation-detail-verify/references/refusal-record.md`, matching Wyatt's original.
> 2. **`/criteria-validate` is not ported** — the DSL rows in §Success criteria are validation-time only; the skill *runs* without it. (Note: the `/criteria-validate` referenced here is NOT the same skill as the dx-aicentral `criteria-validate` already present in this environment — this one is Wyatt's fixture-verification runner and was never a real port target; see the research-skill-suite port design doc.)
> 3. **LOCAL DIVERGENCE — the walk runs in the same invocation** (2026-07-30). Wyatt's original scaffolds shape only and leaves content to a later human pass. In practice the invoking agent *is* the author, so scaffold-only produced an empty template four consecutive times and the walk never happened. This copy adds §Evidence walk (workflow steps 7–9; the former steps 7–8 renumber to 10–11) and `WebSearch` to `allowed-tools`. The anti-recommendation guard, the tier rubric, the refusal surfaces, and both output locks are UNCHANGED — this divergence adds a phase, it does not relax a contract.
>
> Provenance pointers below to `~/dx-arch-meta/repos/research-docs/...` are Wyatt's originating briefs — historical context, not runtime dependencies. `--target-repo` should point at your own research-docs (`repos/research_docs`).

External-evidence syntheses (literature reviews, landscape scans, state-of-the-art surveys) have a distinct decay model and authorship discipline from the other content types in a typical decision-records repo. Per the brief at `~/dx-arch-meta/repos/research-docs/content/notes/survey-author-skill-brief.md`, surveys describe the **external state of the world** at a point in time — they refresh in place rather than promote-or-die (notes), and they do not carry a verdict that supersedes (evals). Without a typed scaffold, surveys end up in `notes/` (rotting because they look like working drafts) or shoehorned into `evals/` (with a fake verdict). The skill packages the `survey/` content type introduced in research-docs PR-4 (2026-05-16) so future external-evidence syntheses in any research-docs-shaped repo carry the same schema, decay model, source-tier rubric, and anti-recommendation discipline.

External-evidence syntheses (literature reviews, landscape scans, state-of-the-art surveys) have a distinct decay model and authorship discipline from the other content types in a typical decision-records repo. Per the brief at `~/dx-arch-meta/repos/research-docs/content/notes/survey-author-skill-brief.md`, surveys describe the **external state of the world** at a point in time — they refresh in place rather than promote-or-die (notes), and they do not carry a verdict that supersedes (evals). Without a typed scaffold, surveys end up in `notes/` (rotting because they look like working drafts) or shoehorned into `evals/` (with a fake verdict). The skill packages the `survey/` content type introduced in research-docs PR-4 (2026-05-16) so future external-evidence syntheses in any research-docs-shaped repo carry the same schema, decay model, source-tier rubric, and anti-recommendation discipline.

## When to invoke

- Author is about to start a new external-evidence synthesis — a literature review, landscape scan, or state-of-the-art writeup.
- Topic is broader than a single eval (which compares X vs Y with a verdict) but narrower than a design doc (which describes how a system works).
- A future RFC or ADR will need to cite this body of external evidence.

**Don't invoke when:**
- The deliverable is a recommendation. Surveys describe; they do not decide. Use an RFC that cites a survey.
- The deliverable is an internal experiment ("we tried X vs Y, here's the verdict"). Use `evals/`.
- The topic is a single open question. Use `open-questions/`.

## Input

```
/survey-author --question <falsifiable-claim> --tags <topic-tag-list> --target-repo <path> [--seed-urls <url-list>]
```

Three required arguments + one optional data input. No behavior knobs. Per Decision 2 of `openspec/changes/survey-author-skill/design.md`, refresh-cadence-hint is NOT accepted; seed-URLs is optional data (not a knob), required only by the tier-classification fixtures.

- `--question <falsifiable-claim>` — one-sentence claim the survey will describe evidence for / against. Drives the `scope:` frontmatter field and the body's §Scope section.
- `--tags <topic-tag-list>` — comma-separated topic tags. Drives the `tags:` frontmatter field. Corpus-navigation only — as of `source-recency-probe` v2.0 the probe derives its venue set from `sources[]` and never reads `tags:`.
- `--target-repo <path>` — absolute-or-repo-relative path to the research-docs-shaped repo where the scaffolded survey lands.
- `--seed-urls <url-list>` (optional) — comma-separated URL list. When supplied, each URL is classified via the two-pass tier-classifier per `references/source-tier-rubric.md` and written into the scaffolded `sources:` table with its tier label. Empty / unsupplied → scaffolded `sources:` table is empty and the author populates it later.

## Workflow

1. **Parse input** — extract question + tags + target-repo + (optional) seed-URLs. Refuse if any required arg is missing.
2. **Detect anti-recommendation surface** — scan the input for caller-supplied conclusion, per-source author interpretation, expected verdict, or explicit Recommendation/Verdict section request. Any match → emit refusal-record per `../citation-detail-verify/references/refusal-record.md` v1.1 and short-circuit. Per Decision 6 of `openspec/changes/survey-author-skill/design.md`.
3. **Classify each seed URL** (two-pass per Decision 9):
   - **Pass 1 (URL-pattern)** — match the URL against the tier-1 / tier-2 pattern sets in `references/source-tier-rubric.md` §URL-pattern catalog. No match → tier-3 candidate (default).
   - **Pass 2 (WebFetch content-probe)** — for tier-1 / tier-2 candidates, fetch the URL one-shot via WebFetch (no shared cache participation — scaffold-time is one-off per Decision 4) and sniff for the tier-specific vocabulary per `references/source-tier-rubric.md` §Content-probe sniff vocabulary. Confirmed → tier-1 / tier-2; unconfirmed → re-tier to tier-3.
   - **Unverifiable fallback** — WebFetch failure (paywall, non-HTML mirror, network error, HTTP ≥4xx) → tier label `unverifiable` for that source. Per `references/output-schema.md` §Status semantics, this surfaces as `unverifiable` in the Stage 3 driver row.
4. **Assemble scaffolded frontmatter** — emit YAML frontmatter conforming to `references/output-schema.md` §Scaffolded-survey-doc shape. Required fields: `title`, `scope` (from `--question`), `status: active`, `date` (today), `last-refreshed` (today), `authors`, `sources` (tier-classified table from step 3), `tags` (from `--tags`), `related-rfcs: []`, `related-adrs: []`, `related-oqs: []`, `related-principles: []`, `supersedes: []`, `superseded-by: []`.
5. **Assemble scaffolded body** — emit the required section structure per `references/output-schema.md` §Required section structure: `## Scope`, `## Method`, `## Landscape`, `## Comparison`, `## Open questions`, `## Sources`, `## Refresh log`. Each section carries a one-sentence prompt for the author. The body MUST NOT contain any section titled `Recommendation`, `Verdict`, `Decision`, or any synonym — corpus-wide invariant per Decision 6.
6. **Write scaffolded survey doc** — write the assembled frontmatter + body to `<target-repo>/content/survey/<slugified-question>.md`. Slug derives from the `--question` value (lowercased, non-alphanumerics replaced with `-`). At this point the body carries section prompts, not content.
7. **Run the evidence walk** — per §Evidence walk below. NOT optional and NOT deferred to a later invocation. A survey that ships with placeholder sections is an incomplete invocation, not a completed scaffold.
8. **Re-classify the discovered source set** — every source the walk surfaced goes through the same two-pass classifier as step 3, and lands in both the frontmatter `sources:` list and the `## Sources` table with matching ids.
9. **Rewrite the body from the walk** — replace every section prompt with authored content per §Evidence walk §Writing discipline. Re-check the forbidden-section invariant on the finished body, not just on the template.
10. **Emit Stage 3 driver check-row JSON** — one row per classified source (seed-supplied or walk-discovered) conforming to `references/output-schema.md` §Stage-3-driver-check-row shape `(criterion-id, status, evidence-quote)`. Each row's `status` is `pass` (tier classified), `fail` (tier classification missing on a URL the rubric should have caught), or `unverifiable` (WebFetch could not probe).

   **Before any tier row, run the walk post-condition.** Re-read the survey file from disk — not from what this invocation believes it wrote — and emit exactly one `ran-evidence-walk` row: `pass` when no template prompt survives and `## Method` names the query families actually run; `fail` when any section is delivered still carrying its prompt, with the surviving prompt quoted verbatim as the evidence.

   This check lives at step 10, not inside the walk, **deliberately and load-bearingly**. An invocation that skips the walk skips steps 7, 8 and 9 together — a guard emitted from inside that phase would be skipped along with it, and the invocation would proceed to tier rows that all pass and an aggregate `pass`, which is the exact silent failure this row exists to close. Step 10 runs on every non-refused invocation, so the guard fires whether or not the walk did. See §Success criteria §Local addendum and `test-corpus/placeholder-body.md`.
11. **Compute aggregate verdict** — per `references/output-schema.md` §Verdict computation: all rows pass + no unverifiable → `pass`; any unverifiable + no fail → `unverifiable`; any fail → `fail`.

## Evidence walk

Steps 7–9. The scaffold is the container; this is the work. Run it in the same invocation that wrote the scaffold — never hand a placeholder body back to the caller and never offer to "run the walk next" as a follow-up.

**Query-family fan-out.** Derive four to six *distinct* query families from `--question` + `--tags` before searching, and record them in `## Method`. A family is a distinct angle, not a rephrasing. Cover, where the topic admits them:

1. The primary claim stated in the topic's own vocabulary.
2. The academic framing — venue-shaped terms, `arxiv`, named conferences, "empirical study", "controlled trial", "randomized".
3. The counter-case — the strongest evidence *against* the framing the question implies.
4. The measurement layer — how outcomes in this domain are quantified, and by whom.
5. The adjacent-role or downstream-effect angle the question's framing would otherwise miss.
6. An explicit probe for the **join the question assumes exists**. If no source makes that join, that absence IS a finding — record it in `## Open questions` as an unmeasured gap, never as an absence of searching.

**Fetch-before-cite.** Never cite from a search-result snippet. Every source cited MUST be fetched and reduced to a specific number, finding, or short verbatim phrase. Prefer `arxiv.org/abs/` over `/html/` or `/pdf/` so pass-1 tier matching works. A PDF that WebFetch cannot parse is often readable via `Read` with a `pages` range — the fetch tool saves the binary locally and reports the path; try that before giving up on a source.

**Disposition of anything that will not reduce.** Three outcomes, all recorded, none silent:

- Fetch fails (HTTP ≥4xx, paywall, network) → tier `unverifiable`. Flagged in `sources:`, cited for NO claim, and named in `## Open questions` as a resolve-on-next-refresh item.
- Fetch succeeds but yields no extractable specifics → **exclude**, and say so in `## Method` with the reason.
- A claim is widely repeated but untraceable to a primary source → **exclude**, and name it in `## Method` as excluded-untraceable. Repeated-in-many-places is not a source.

**Tier honesty.** Apply the mechanical rubric, then say where it under-reads. A peer-reviewed paper on a non-matching domain is tier 3 *by URL pattern* — label it tier 3 and note in `## Method` that the label is the domain default, not a quality judgment. Never hand-promote a tier.

### Writing discipline

- **Numbers over adjectives.** Every Landscape claim carries the figure, the n, and the source id. "Lead time roughly halved (12→5 days, n=10,804)" — not "significantly faster".
- **Quote short and attributed.** Prefer the number; reach for a verbatim phrase only when the source's exact wording is the evidence. Never reproduce substantial passages.
- **Carry the caveat with the number, not in a footnote.** Confounds, single-site designs, undisclosed sample sizes, and temporal artifacts belong in the same paragraph as the figure they qualify.
- **Read past the abstract for the qualifier.** Where a source's own data undercuts its headline, surface that — it is the highest-value thing a survey does.
- **Mark every inference as yours.** When two sources are joined into a claim neither makes, say so inline and log it in `## Open questions`.
- **Contradictions stay contradictions.** Where sources disagree, present both with their populations and constructs, and state that no source reconciles them. Do not average, adjudicate, or pick a winner — that is verdict-creep, and it is the failure mode this skill exists to prevent.
- **`## Comparison` compares evidence, not options.** Each cell reports what a source measured in its own setting; add the row-scope caveat under the table.

## Invoke at refresh cadence

The survey `last-refreshed:` frontmatter field is the canonical refresh trigger. When an author refreshes an existing survey (re-walks sources, updates the Landscape and Comparison sections), the `last-refreshed:` bump SHOULD be accompanied by a `/survey-author --update` invocation that re-runs the scaffold-shape check against the live doc (sources still tier-classifiable, body still free of Recommendation section, refresh-log appended). Per `references/refresh-cadence.md`, surveys refresh in place rather than promote-or-die.

Canonical copy-paste invocation line for the survey's refresh footer:

```
<!-- Last refresh scaffold-checked via /survey-author --update --target-repo <repo-path> --artifact <this-survey-path> -->
```

`--update` is reserved at v1.0 (NOT shipped this PR — Decision 8 promoted the refresh companion to its own brief in research-docs). The comment line is documented here so future-author conventions stay consistent when the companion ships.

## Proposal-time candidate capture

The scaffold is empty of sources; the author fills `sources[]` from gather and
gap-find subagent proposals (research-docs `llm-review-pipeline-methodology`
Stage 1a / 1c), and the Stage 1c WebFetch is where fabricated candidates die
unrecorded — the reason EVAL-0001 / EVAL-0002 in research-docs found no
denominator. So, at the moment a subagent's proposal list arrives and BEFORE
that WebFetch, record it:

```
python3 ~/.claude/skills/citation-detail-verify/scripts/candidates.py append --repo <target-repo> --artifact content/survey/<slug>.md --from-json <proposals.json>
```

The re-read drop and the commit-time landing sweep are `append-disposition`
calls with `--stage survey-author`. Which values, which labels, and why
`--seed-urls` are not recorded:
[`../citation-detail-verify/references/candidates-contract.md`](../citation-detail-verify/references/candidates-contract.md) v1.0
§Who writes what.

## Anti-recommendation guard

Surveys describe the landscape; they do not decide. Recommendations belong in an RFC that cites the survey. The skill enforces this at two layers per Decision 6:

1. **Invocation-time refusal** — when the caller's input explicitly requests a `Recommendation`, `Verdict`, or `Decision` section (or any synonym), or contains a preferred conclusion / expected verdict, the skill emits a refusal-record per `../citation-detail-verify/references/refusal-record.md` v1.1 with `refusal.rule` = "Surveys describe; they do not decide. Recommendations belong in an RFC that cites the survey." See the §Invocation discipline bullet below for the verbatim refusal-record bullet.
2. **Corpus-wide invariant** — no scaffolded survey body EVER contains a recommendation statement. Even on otherwise-valid invocations, the scaffolded body terminates at `## Open questions` + `## Sources` + `## Refresh log` per the survey schema. This guards against silent recommendation-section leakage in the scaffold template itself.

## Success criteria (DSL primitives quoted verbatim from brief)

The brief at `~/dx-arch-meta/repos/research-docs/content/notes/survey-author-skill-brief.md` declares the property set the skill MUST exhibit. Quoting all 14 DSL rows verbatim:

- `detect applied-tier-1-rubric in ~/.claude/skills/survey-author/test-corpus/tier-1-source.md count >=1`
- `detect applied-tier-2-rubric in ~/.claude/skills/survey-author/test-corpus/tier-2-source.md count >=1`
- `detect applied-tier-3-rubric in ~/.claude/skills/survey-author/test-corpus/tier-3-source.md count >=1`
- `detect registered-source-tier in ~/.claude/skills/survey-author/references/source-tier-rubric.md count >=3`
- `detect refresh-in-place-cadence-statement in ~/.claude/skills/survey-author/references/refresh-cadence.md count >=1`
- `absent promote-or-die-cadence-marker in ~/.claude/skills/survey-author/test-corpus/`
- `detect emitted-refusal-on-recommendation-section in ~/.claude/skills/survey-author/test-corpus/recommendation-attempted.md count >=1`
- `absent recommendation-statement-in-survey-body in ~/.claude/skills/survey-author/test-corpus/`
- `detect emitted-verdict-pass in ~/.claude/skills/survey-author/test-corpus/pass-shape.md count >=1`
- `detect emitted-verdict-fail in ~/.claude/skills/survey-author/test-corpus/fail-shape.md count >=1`
- `detect emitted-verdict-unverifiable in ~/.claude/skills/survey-author/test-corpus/unverifiable-shape.md count >=1`
- `detect output-row-with-all-required-fields in ~/.claude/skills/survey-author/test-corpus/pass-shape.md count >=1`
- `absent output-row-missing-required-field in ~/.claude/skills/survey-author/test-corpus/`
- `detect emitted-refusal-record in ~/.claude/skills/survey-author/test-corpus/bad-invocations.md count >=5`

Added by the candidates-capture change (back-propagate to the brief on its next edit):

- `detect recorded-candidate-before-fetch in ~/.claude/skills/survey-author/test-corpus/candidate-capture.md count >=1`

The `/criteria-validate` runner that turns these DSL rows into PASS / FAIL verdicts ships at a later stage in the family build per the runbook at `~/dx-arch-meta/repos/research-docs/content/runbooks/how-to-coordinate-skill-family-build.md`.

### Local addendum (not from the brief)

Two further rows, added 2026-07-30 with local divergence 3. They are **not** part of the 14 quoted above and have no upstream counterpart — the brief predates the walk phase, so it declares no property covering it. Without them the divergence is prose-only: a scaffold delivered with placeholder sections emits nothing but `pass` rows and computes an aggregate `pass`, which is what let the failure recur four times undetected.

- `detect emitted-verdict-fail-on-placeholder-body in ~/.claude/skills/survey-author/test-corpus/placeholder-body.md count >=1`
- `absent unfilled-section-prompt-in-delivered-survey in ~/.claude/skills/survey-author/test-corpus/`

The two rows are different gate kinds and should not be read as a pair:

- The `detect` row is an **emitted-row property**. It is grounded by `test-corpus/placeholder-body.md` and corresponds to the `ran-evidence-walk` row emitted at step 10.
- The `absent` row is an **author-time corpus grep invariant**, the same shape as `absent recommendation-statement-in-survey-body`. Its token is reserved for the gate and MUST NOT appear in any fixture. It drives no emitted row and cannot fire against a real delivered survey.

Declaring `ran-evidence-walk` did require a lock edit: v1.0's §Required row fields admitted only identifiers "the brief listed", which excluded local rows by construction. `references/output-schema.md` is bumped to v1.1 to widen that field and register the row as mandatory. The envelope's wire `version` field stays `"1.0"` — per §Versioning the two are independent.

## Load-when table

| Step | Reference | Why load |
|------|-----------|----------|
| 3 | [`references/source-tier-rubric.md`](references/source-tier-rubric.md) | Three tier definitions, URL-pattern catalog, content-probe sniff vocabulary. Skill-scoped v1.0 lock. |
| 6 (refresh-log) | [`references/refresh-cadence.md`](references/refresh-cadence.md) | Refresh-in-place cadence statement, comparison to other content types, refresh-log convention. Skill-scoped v1.0 lock. |
| 4, 5, 9, 10, 11 | [`references/output-schema.md`](references/output-schema.md) | Scaffolded-doc frontmatter + section structure; Stage 3 driver check-row shape; mandatory `ran-evidence-walk` row; verdict computation; row-vs-refusal distinguishing convention. Skill-scoped v1.1 lock (NOT REUSE of `../citation-detail-verify/references/output-schema.md` per Decision 3). |
| §Proposal-time candidate capture (before the Stage 1c WebFetch; re-read; commit sweep) | [`../citation-detail-verify/references/candidates-contract.md`](../citation-detail-verify/references/candidates-contract.md) | `candidates.jsonl` record shape, sidecar location, `append` / `append-disposition` refusals, who-writes-what table. Shared v1.0 lock; REUSED via relative path. |
| 2, anti-recommendation refusal | [`../citation-detail-verify/references/refusal-record.md`](../citation-detail-verify/references/refusal-record.md) | Refusal-record shape (`refusal: {category, rule, evidence}`). Stage 1 v1.1 lock; REUSED unchanged via relative path. The 1.0 → 1.1 minor bump amends `consumers:` to include `survey-author` (additive; no wire-shape edit). |

References load when the workflow needs them, not at skill startup. Per progressive disclosure, the SKILL.md does NOT restate tier definitions, refresh-log table shape, scaffolded section structure, or refusal-record fields — each lives in its own reference file.

## Invocation discipline

Dominant concern per brief: **bias**. Anti-recommendation rule holds at output-time; the corresponding input discipline keeps the caller's preferred conclusion out of the scaffold prompt. Bloat secondary — scaffold-time prompt is small. Forbidden surfaces — each bullet is the verbatim rule the skill SHALL paste into `refusal.rule` when an invocation triggers refusal per `../citation-detail-verify/references/refusal-record.md`:

- Bias — Caller's preferred conclusion or recommendation.
- Bias — Per-source author interpretation.
- Bias — Expected verdict on the research question.
- Bloat — Full text of seed sources.
- Bloat — Prior research-docs body text.
- Anti-recommendation — Surveys describe; they do not decide. Recommendations belong in an RFC that cites the survey.

Rule rationale (NOT part of the verbatim rule; reference-only context for reviewers): recommendation in the scaffold prompt biases section structure toward defending it (bias 1); per-source author interpretation frames the survey before the author has read the source (bias 2); expected verdict short-circuits the discovery the survey is supposed to ground (bias 3); caller-pasted seed-source full text biases synthesis before the walk has run, and framing-verification of that text belongs at `/load-bearing-fullread` time — the refusal covers *caller-supplied* body text, not skill-initiated fetching, which §Evidence walk now requires at step 7 (bloat 1); prior research-docs body text biases the new scaffold toward existing framings (bloat 2); the anti-recommendation rule is the corpus-wide invariant (Decision 6).

Good brief: `/survey-author --question "What does the evidence say about LLM-based code-review effectiveness across PR-review and code-review contexts?" --tags llm-review,code-quality --target-repo research-docs`. Pointers + question only; no caller-side conclusion.

Bad brief: `/survey-author "Scaffold a survey on agentic SDLC tools — I think CodeRabbit is going to dominate."` Encodes conclusion as premise; refuses with refusal record.

## Out of scope

- ~~Auto-generating survey content.~~ **Amended 2026-07-30 (local divergence 3).** The skill authors content via §Evidence walk in the same invocation. What remains out of scope is *unsourced* content: every Landscape/Comparison claim traces to a fetched, tier-classified source, and the skill never writes a claim it could not reduce to a number or a verbatim phrase. Post-authoring verification stays a separate chain (see below).
- Hugo theme customization. Scaffold output is Hugo-shaped (drops into Hextra-themed repos), but theme work is out of scope.
- Auto-refresh. Refresh is an authored action (bump `last-refreshed:`, edit body, commit), not an LLM-driven loop. The `--update` invocation reserved at §Invoke at refresh cadence ships in a separate brief per Decision 8.
- Source-list verification. `/citation-detail-verify` (Stage 1) verifies citation integrity; `/load-bearing-fullread` (Stage 4) verifies framing. Survey-author defers to those skills; running them is the author's responsibility post-scaffold per Decision 7.

## Cross-skill compatibility

This skill is the FIRST consumer that does NOT REUSE the full Stage 1 lock triple. Brief-explicit: output-schema and cache-contract are skill-specific (scaffold-time, different output shape). Only `refusal-record.md` is REUSED via relative path. The same PR amends that lock additively from v1.0 to v1.1 by appending `survey-author` to `consumers:` — no wire-shape edit per Decision 5.

Bumping the refusal-record lock from v1.x to v2.x requires a coordinated PR across all consumers (`citation-detail-verify`, `load-bearing-fullread`, `adversarial-frame`, `source-recency-probe`, `survey-refresh`, `invocation-discipline-lint`, `survey-author`) — as of 2026-07-14 all are present as true siblings under `skills/`, so this coordination requirement is now live rather than deferred.
