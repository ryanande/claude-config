---
name: survey-refresh
description: Walk an existing scaffolded survey's sources[] list, re-fetch each URL via the shared per-session cache, and emit a structured refresh-report sidecar surfacing URL-removed / URL-added / citation-stale / last-refreshed-bumped rows. Refuses caller's preferred refresh outcome / per-URL pre-classification / expected verdict / full-survey-body attachments / pre-attached source texts. Counters failure mode #5 stale-evidence-after-refresh-cycle by making refresh quality auditable. Trigger with /survey-refresh <survey-path>, "refresh this survey", "run the refresh probes on <path>", or after bumping a survey's last-refreshed. Output is sidecar-only; the survey body is never mutated.
user-invocable: true
allowed-tools: Read, Grep, Glob, WebFetch, Bash, Write
---

# /survey-refresh — refresh-report sidecar for an existing scaffolded survey

External-evidence surveys decay via refresh-in-place: bump `last-refreshed:`, edit the body, commit. The discipline assumes the author manually re-walks each `sources[]` row, re-checks each URL, and identifies stale citations. This is honor-system at exactly the moment evidence has decayed the most — months between events, the author re-loads the survey cold, and there is no record of what changed. Per the brief at `~/dx-arch-meta/repos/research-docs/content/notes/survey-refresh-skill-brief.md`, the skill walks the survey's `sources[]` and the `## Refresh log` table mechanically and surfaces a structured refresh-report sidecar an auditor (or the original author six months later) can verify. The skill produces INPUT to a refresh decision; the author drives the body edits.

## When to invoke

- An existing survey doc is about to be refreshed (`status: stale` per `~/dx-arch-meta/repos/research-docs/content/open-questions/0002-staleness-thresholds-per-type/` ≥ 6 months since last refresh).
- An author bumped `last-refreshed:` and wants the refresh-log table verified against the bump.
- An auditor wants to verify a past refresh's evidence — re-run after the fact on the survey at that commit SHA.

**Don't invoke when:**
- The survey has never been scaffolded — use `/survey-author` first.
- The deliverable is a rewritten survey body — refresh is an authored action; this skill produces report input, not the rewrite.
- The intent is to add brand-new sources from a fresh literature search — run `/source-recency-probe` directly against the survey; this skill surfaces the recommendation but does not execute it.

## Input

```
/survey-refresh <survey-path>
```

One required argument. No optional flags. Per Decision 2 of `openspec/changes/survey-refresh-skill/design.md`, the brief-listed `--since DATE` knob is DROPPED — the skill uses the survey's current `last-refreshed:` value as the refresh-window lower bound; a caller wanting a different window edits `last-refreshed:` first.

- `<survey-path>` — absolute-or-repo-relative path to the existing scaffolded survey doc (one authored under the survey schema per `/survey-author`).

## Workflow

1. **Parse input** — read the survey path. Refuse if missing.
2. **Detect bias / bloat surface** — scan input for caller preferred refresh outcome, per-URL pre-classification, expected refresh-report verdict, full-survey-body attachment, or pre-attached source texts. Any match → emit refusal-record per `../citation-detail-verify/references/refusal-record.md` v1.3 and short-circuit.
3. **Read survey frontmatter + refresh-log** — parse `sources[]`, `last-refreshed:` from frontmatter; locate the `## Refresh log` section's table.
4. **URL-removed / URL-stale probe** — for each URL in `sources[]`, fetch via the shared cache per `../citation-detail-verify/references/cache-contract.md` Read protocol. Classify:
   - HTTP ≥4xx, dead link, domain expired → emit `detected-url-removed` row (`status: fail`).
   - HTTP 200 → SHA256-of-body-compare against the prior-session body snapshot captured BEFORE the re-fetch per Decision 8 (re-fetch overwrites the cache entry atomically; the snapshot is the only way to preserve the prior body — see `references/refresh-report-schema.md` §SHA256-of-body-compare protocol). Different SHA → emit `detected-citation-stale` row (`status: fail`). Same SHA → no row (clean). No prior-session entry → no row (cache warms for next refresh).
   - WebFetch failure (network error, paywall, non-HTML mirror) → emit `detected-citation-stale` or `detected-url-removed` row with `status: unverifiable` depending on whether the URL is unreachable (`url-removed`) or reachable-but-unparseable (`citation-stale`).
5. **URL-added candidate surface (OQ-1 row-surface)** — per Decision 7, the skill does NOT invoke `/source-recency-probe` directly, and from `/source-recency-probe` v2.0 there is no venue catalog to infer from. It emits exactly **one** advisory `detected-url-added` row per invocation: `citation-id: advisory:source-recency-probe`, `cited-value: ""`, `actual-value: "run /source-recency-probe to surface post-cutoff candidates from the citation graph of sources[]"`, `evidence-quote` = the verbatim instruction in §OQ-1 row-surface composition, `status: pass` (informational; no in-survey defect).
6. **`last-refreshed:` bump verification** — per Decision 12: the `## Refresh log` table's most-recent row's date MUST be ≥ frontmatter `last-refreshed:`. Consistent → emit `detected-last-refreshed-bumped` row with `status: pass`. Mismatch → `status: fail`. Missing table → `status: unverifiable`.
7. **Assemble envelope** — collect rows into an envelope conforming to `../citation-detail-verify/references/output-schema.md` v2.0 §Envelope (wire `version: "1.0"`; `skill: "survey-refresh"`; `artifact: <absolute-survey-path>`; aggregate `verdict` per §Verdict computation; `cache: {hits, misses, writes}` populated per `../citation-detail-verify/references/cache-contract.md` §Cross-skill telemetry).
8. **Write sidecar** — per Decision 9, write the envelope as JSON within a code block plus a markdown row summary to `<survey-dir>/refresh-report-<YYYY-MM-DD>.md`. The skill DOES NOT mutate the survey body or its `## Refresh log` table — author manually adds a one-line entry referencing the sidecar.

## Author flow post-skill

Sidecar disposition (path pattern, JSON-in-fenced-code-block, markdown summary table) is owned by `references/refresh-report-schema.md` §Sidecar disposition rule. The skill never edits the survey body or its frontmatter — `last-refreshed:` bump is an authored event the skill verifies after the fact (Decision 12), not an event the skill triggers.

After the skill writes the sidecar: read it; reconcile each row against the survey body; manually append a one-line entry to the survey's `## Refresh log` table pointing at the sidecar filename + ISO date. The body edit is the authored event the survey schema requires.

## OQ-1 row-surface composition

Per Decision 7, `/survey-refresh` and `/source-recency-probe` are composable but independent. The URL-added surface is a single advisory `detected-url-added` row per invocation (venue inference was removed with the v1.x catalog); its `evidence-quote` is verbatim:

```
Run /source-recency-probe --artifact <survey-path> --authored-against <model>,<cutoff-date> to surface post-cutoff candidates from the citation graph of sources[].
```

The author runs `/source-recency-probe` as a follow-on invocation; the candidate paper / venue rows populate from that skill's own envelope. This keeps each skill's invocation independently auditable and avoids cross-skill cache-telemetry ambiguity.

## Success criteria (DSL primitives quoted verbatim from brief)

- `detect detected-url-removed in ~/.claude/skills/survey-refresh/test-corpus/url-removed.md count >=1`
- `detect detected-url-added in ~/.claude/skills/survey-refresh/test-corpus/url-added.md count >=1`
- `detect detected-citation-stale in ~/.claude/skills/survey-refresh/test-corpus/citation-stale.md count >=1`
- `detect detected-last-refreshed-bumped in ~/.claude/skills/survey-refresh/test-corpus/last-refreshed-bumped.md count >=1`
- `absent rewrote-survey-body in ~/.claude/skills/survey-refresh/test-corpus/`
- `absent promote-or-die-cadence-marker in ~/.claude/skills/survey-refresh/test-corpus/`
- `detect emitted-verdict-pass in ~/.claude/skills/survey-refresh/test-corpus/pass-shape.md count >=1`
- `detect emitted-verdict-fail in ~/.claude/skills/survey-refresh/test-corpus/fail-shape.md count >=1`
- `detect emitted-verdict-unverifiable in ~/.claude/skills/survey-refresh/test-corpus/unverifiable-shape.md count >=1`
- `detect output-row-with-all-required-fields in ~/.claude/skills/survey-refresh/test-corpus/pass-shape.md count >=1`
- `absent output-row-missing-required-field in ~/.claude/skills/survey-refresh/test-corpus/`
- `detect cache-hit-on-shared-fetch in ~/.claude/skills/survey-refresh/test-corpus/shared-cache.md count >=1`
- `detect emitted-refusal-record in ~/.claude/skills/survey-refresh/test-corpus/bad-invocations.md count >=5`

The `/criteria-validate` runner that turns these DSL rows into PASS / FAIL verdicts ships at Stage 6 of the family build (claude-config PR #38).

## Load-when table

| Step | Reference | Why load |
|------|-----------|----------|
| 2 | [`../citation-detail-verify/references/refusal-record.md`](../citation-detail-verify/references/refusal-record.md) | Refusal-record shape (`refusal: {category, rule, evidence}`). Stage 1 v1.3 lock; REUSED unchanged in wire shape via relative path. Wire `version: "1.0"` per §Shape. |
| 4, 7 | [`../citation-detail-verify/references/cache-contract.md`](../citation-detail-verify/references/cache-contract.md) | Shared per-session cache key derivation, on-disk layout, read protocol, session-scope freshness policy (used for prior-session body-compare per Decision 8), cross-skill telemetry. Stage 1 lock (now v1.4); REUSED unchanged via relative path. |
| 7, 8 | [`../citation-detail-verify/references/output-schema.md`](../citation-detail-verify/references/output-schema.md) | Envelope shape, row shape, status semantics, verdict computation, §Check-name vocabulary §survey-refresh registration. Stage 1 lock, frontmatter v2.0; REUSED unchanged via relative path. Wire `version: "1.0"`. |
| 4, 6, 8 | [`references/refresh-report-schema.md`](references/refresh-report-schema.md) | Skill-scoped v1.0 lock — check-name → row-field mapping per Decision 3, sidecar disposition rule per Decision 9, `last-refreshed:` verification rule per Decision 12, SHA256-of-body-compare protocol per Decision 8. |

References load when the workflow needs them, not at skill startup. Per progressive disclosure, this SKILL.md does NOT restate envelope shape, row shape, cache key derivation, refusal-record fields, or refresh-report check-name → row-field semantics — each lives in its own reference file.

## Invocation discipline

Dominant concern per brief: **bias**. A refresh primitive sits in the same trust position as the original scaffold; caller bias re-enters at refresh time if the contract leaks. Bloat secondary — input is one path. Forbidden surfaces — each bullet is the verbatim rule the skill SHALL paste into `refusal.rule` when an invocation triggers refusal per `../citation-detail-verify/references/refusal-record.md`:

- Bias — Caller's preferred refresh outcome.
- Bias — Per-URL pre-classification.
- Bias — Expected refresh-report verdict.
- Bloat — Full survey body attachment.
- Bloat — Full text of currently-cited sources.

Rule rationale (NOT part of the verbatim rule; reference-only context for reviewers): preferred outcome encodes refresh as confirmation-search (bias 1); per-URL pre-classification frames the check before the skill walks the URL (bias 2); expected verdict short-circuits the surface the refresh is supposed to discover (bias 3); the skill reads frontmatter + `## Refresh log` table only — body re-walking belongs in `/load-bearing-fullread`, so full-survey-body attachments inflate context without contract gain (bloat 1); the skill re-fetches each URL via the shared cache, so pre-attached source bodies bias the staleness sniff and short-circuit the SHA-compare surface (bloat 2).

Good brief: `/survey-refresh content/survey/llm-review-landscape.md`. Path only; skill derives the refresh window from frontmatter `last-refreshed:`.

Bad brief: `/survey-refresh content/survey/llm-review-landscape.md --i-think-source-S3-is-stale`. Names per-URL pre-classification — refuses with refusal record.

## Out of scope

- Rewriting the survey body. Refresh-report is sidecar-only per Decision 9; the brief invariant `absent rewrote-survey-body` enforces this corpus-wide.
- Auto-bumping `last-refreshed:`. The bump is an authored event the skill verifies after the fact (Decision 12).
- Promoting the survey to v2 or archiving the survey. Decay model is refresh-in-place per `/survey-author` §Cross-skill compatibility and `survey/_index.md` Conventions.
- Re-running tier classification on each URL. Tier ran at scaffold time per `/survey-author` `source-tier-rubric.md`; rerunning collapses scaffold-time and refresh-time. Refresh checks URL health, not tier reclassification.
- Scheduling. Manual-only at v1.0 per Decision 10; cron-style fire-at-staleness-threshold is harness concern (POSSIBLE FUTURE OPTIMIZATION, not reserved v1.1 schema surface).

## Cross-skill compatibility

This skill REUSES all three Stage 1 locks (output-schema frontmatter 2.0, cache-contract 1.4, refusal-record 1.4; wire `"1.0"`) via relative path. The same PR amends each lock additively (consumers-list amendment per Stage 3 / Stage 6 precedent; output-schema also gets §Check-name vocabulary §survey-refresh registration):

- output-schema `1.0 → 1.1` — append `survey-refresh` to `consumers:`; register §survey-refresh check-names. Envelope / row / status / verdict semantics unchanged; wire `version: "1.0"` in §Envelope example unchanged.
- cache-contract `1.0 → 1.1` — append `survey-refresh` to `consumers:`. Body byte-identical otherwise.
- refusal-record `1.2 → 1.3` — append `survey-refresh` to `consumers:`. Body byte-identical from v1.2. Wire `version: "1.0"` in §Shape unchanged.

Bumping any of the three locks from v1.x to v2.x requires a coordinated PR across all listed consumers.
