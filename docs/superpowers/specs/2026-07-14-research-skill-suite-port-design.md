# Design: Port Wyatt's research-skill-suite into claude-config

- **Date:** 2026-07-14
- **Status:** approved, pending implementation plan
- **Author:** Ryan Anderson (via Claude Code brainstorming session)

## Goal

Port the remaining skills of [Wyatt Rupp's `research-skill-suite`](https://github.com/Wyatt-Rupp_prepass/claude-config/blob/main/docs/research-skill-suite.md) into Ryan's own `claude-config` repo, completing the pipeline that `survey-author` (already adopted 2026-06-09) was the first piece of. The end state: a working authoring → discover → draft → verify chain, orchestrated by `oq-resolver`, usable to research and land a real decision — starting with the Azure Resource Group naming/organization question that motivated this project.

## Background

`claude-config`'s `survey-author` skill was adopted from Wyatt's repo with two documented divergences: `refusal-record.md` was vendored locally (because its sibling, `citation-detail-verify`, wasn't ported), and `/criteria-validate` was skipped. Its own README note anticipated this moment: *"If you later port the rest of the suite, restore the relative-path REUSE."*

Wyatt's suite is 7 skills across three roles (per his `research-skill-suite.md`):
- **Authoring** (no recommendation): `survey-author` (have), `survey-refresh`
- **Verification chain** (ordered): `source-recency-probe` → `citation-detail-verify` → `load-bearing-fullread` → `adversarial-frame`
- **Orchestration**: `oq-resolver` (composes the whole pipeline into a research-docs PR)

Plus `invocation-discipline-lint`, an eighth enforcement-layer skill referenced by the suite doc but not in its main table.

Current state of the target environment:
- `research_docs` already has `content/survey/` seeded (3 surveys authored via `/survey-author`) but no `content/open-questions/`, `content/rfc/`, or `content/adr/` yet.
- Real Azure infrastructure exists across the org (`eng-site-systems-infra`, `dx-particular-serviceplatform`, `devops-terraform`, `poc_viewmodeldata`) with visibly inconsistent Resource Group naming already in production (`PrePassInfrastructure-rg-prd`, `prepass-rg-int`, `prepass-rg`, `${var.prefix}-rg-${var.env_suffix}`) — this is the real decision the ported pipeline will be used to resolve.
- `dx-prepass-meta` ships `bin/dxroot`, a sibling-repo path resolver, which substitutes cleanly for Wyatt's `DX_ARCH_META_ROOT` env-var convention.

## Scope

### In scope — 7 skills ported into `repos/claude-config/skills/`

| Skill | Port type |
|---|---|
| `citation-detail-verify` | Verbatim (lock owner: cache-contract, output-schema, refusal-record) |
| `source-recency-probe` | Verbatim |
| `load-bearing-fullread` | Verbatim |
| `adversarial-frame` | Verbatim |
| `survey-refresh` | Verbatim |
| `invocation-discipline-lint` | Verbatim |
| `oq-resolver` | Verbatim + one adaptation (below) |

Each verbatim port copies `SKILL.md`, `references/`, and `test-corpus/` unchanged. No path rewriting is needed for the six non-`oq-resolver` skills: every cross-reference to `citation-detail-verify`'s lock files (`../citation-detail-verify/references/{cache-contract,output-schema,refusal-record}.md`) resolves correctly once all skills are true siblings under `skills/`, and Wyatt's canonical lock files already list `survey-author` in their `consumers:` frontmatter.

**Also in scope:**
- **Un-vendor `survey-author`**: restore its `SKILL.md` references from `references/refusal-record.md` back to `../citation-detail-verify/references/refusal-record.md`; delete the vendored `skills/survey-author/references/refusal-record.md`; update its adoption note to reflect divergence #1 as resolved (divergence #2, `criteria-validate` not ported, still stands — see Out of scope).
- **`oq-resolver` adaptation**: edit the copied `SKILL.md`'s Step 0 prereq check and Step 1 invocation to resolve the target repo via `dxroot --check research_docs` / `--repo "$(dxroot research_docs)"`, replacing the `DX_ARCH_META_ROOT` env-var convention. Verified: `oq_select.py` accepts `--repo <path>` as an override (no code change needed there); `oq_flip.py` has zero repo-path assumptions (verified via source read — takes `--file` directly).
- **Seed `content/open-questions/` in `research_docs`** (currently unseeded): `_index.md` (frontmatter schema: `status`, `unblock-by`, `build`, `promoted-to`), `_template.md`, a README taxonomy-table row flip to Seeded ✅, and **one real seed OQ**: the Azure RG naming/organization question, framed with neutral `unblock-by` items (e.g. external precedent for Azure RG naming/scoping conventions; current-state inventory of existing RG names across PrePass subscriptions; CI/CD naming-assumption constraints in `devops-terraform`). This is not a synthetic fixture — it's the actual research question this whole project exists to unblock.
- **Deployment**: symlink each new skill into `~/.claude/skills/<name>`, matching the existing pattern.
- **Documentation**: add a row per new skill to `repos/claude-config/README.md`'s skills table; add a trimmed `docs/research-skill-suite.md` to `claude-config` covering the authoring role, the 4-stage verify chain, and `oq-resolver` as orchestrator (matching Wyatt's composition diagram), with `invocation-discipline-lint` noted as a one-line optional enforcement layer rather than given its own section, and a pointer to Wyatt's original doc for full detail.
- **Final step — run the pipeline for real**: once ported, invoke `/oq-resolver --oq <seed-id>` against the seeded OQ. This researches the Azure RG question end to end (discovery → draft → full verify chain) and opens a real PR against `research_docs` proposing a disposition, which becomes the actual deliverable for the RG naming/organization decision. This folds what would have been a separate sub-project (research the RG plan) into this project's final step, since seeding the OQ already requires framing the RG question, and running `oq-resolver` on it is the natural next action rather than a second brainstorming cycle.

### Out of scope

- **`criteria-validate`** — not a real port target. Every reference to this name in Wyatt's repo is dx-aicentral OpenSpec/exocortex archive content, unrelated to the research-pipeline suite. A skill of this exact name already exists in Ryan's environment (dx-aicentral), serving a different purpose (validating exocortex brief `success_criteria`, not verifying research artifacts). `survey-author`'s existing divergence #2 (this skill not ported) stands unchanged.
- Any other skill in Wyatt's `claude-config` repo not part of the research-pipeline suite (`run-pr-test-plan`, `waf-library-*`, `work-audit`, `work-pattern`, `openspec-*`).
- Adapting or trimming the ported skills' tone/provenance pointers beyond what's functionally necessary (`oq-resolver`'s `dxroot` substitution). Deferred unless real usage surfaces friction.

## Validation / acceptance criteria

1. **Byte-diff check**: the 6 non-`oq-resolver` skills are byte-identical to Wyatt's source. `oq-resolver`'s diff shows only the Step 0/Step 1 `dxroot` substitution.
2. **Cross-skill smoke test**: run `citation-detail-verify` and `source-recency-probe` against an existing survey in `content/survey/`; confirm valid envelopes and an observed cache hit when the second skill re-fetches a URL the first already cached at `~/.claude/skills/citation-detail-verify/cache/<key>/`.
3. **`invocation-discipline-lint` smoke test**: lint one real invocation's call signature (e.g. `citation-detail-verify`'s) against its own `SKILL.md`'s "Invocation discipline" section in `advisory` mode; confirm a clean parse and pass.
4. **`oq-resolver` end-to-end acceptance**: with the seed OQ in place, run `/oq-resolver --oq <id>` for real. Confirm: a worktree spins up off `research_docs` main; the skill researches external evidence; drafts a disposition; runs the full verify chain (`source-recency-probe` → `citation-detail-verify` → `load-bearing-fullread` → `adversarial-frame`); opens a real PR against `research_docs` with an evidence summary, verifier verdicts, and a `## Human decision` section; and does **not** merge it. This step creates a real, externally-visible artifact (a GitHub PR) autonomously — confirm with the user immediately before this specific step runs, even though the skill itself never auto-merges.

## Risks / considerations

- `oq-resolver` is the only ported skill with real infrastructure prerequisites beyond a file copy (open-questions folder/schema, `dxroot`-based path resolution, live `gh auth`). If seeding or path resolution is wrong, the skill fails closed (aborts, no PR) rather than misbehaving — but it's worth a dry Step-0/Step-1 check before the full run.
- The seed OQ commits this project to actually running the RG research as its last step. If the user wants to review the seed OQ's framing before `oq-resolver` fires on it, that's a natural checkpoint in the implementation plan.
