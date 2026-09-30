# Output template — the gap-analysis report

Render this structure to the `/tmp` scratch file, then publish it to the **arch Confluence space** (the deliverable — never a repo). Keep it scannable: an executive can read §1–§3 in five minutes; an engineer can act from §5–§7. Every finding cites `path:line`. This maps cleanly to the branded page handed to `prepass-branded-documentation`.

---

```markdown
# IaC Gap Analysis — <repo name>
**Date:** <YYYY-MM-DD> · **Scope:** <scope> · **Analyst:** <user> · **Baseline:** PrePass Platform Architecture Future State Guide (arch-platform, v<X.X>) + Architecture Guiding Principles (live, page 10223624) + Azure WAF + CIS Azure

## 1. Executive summary
- 3–5 sentences: the headline. Overall maturity, the single biggest risk, the single biggest strength, and the one thing to do first.
- **Overall maturity: <X.X>/5** (weighting: security & reliability ×1.5, others ×1.0)

## 2. Maturity scorecard
| Dimension | Score (1–5) | Trend | One-line verdict |
|-----------|-------------|-------|------------------|
| Reliability & Resiliency | | — | |
| Security & Compliance | | — | |
| Cost Optimization | | — | |
| Operational Excellence | | — | |
| Performance Efficiency | | — | |
| Structural / IaC Health | | — | |
| Architecture Alignment | | — | |

## 3. What's good (stack-ranked)
> The load-bearing strengths. Do not disturb these without cause.
1. **<strength>** — why it matters, where it's applied, the risk it absorbs. `path` / Grep evidence.
2. …

## 4. What's bad (stack-ranked)
> Worst-first by intent-weighted severity. Top 5 carry the story.
1. **[<SEV>] <gap title>** (`DIM-###`, conf: <verified/partial/self_reported>) — `path:line`. Impact, principle/pillar implicated, intent tier, **source** (e.g. `CIS-Azure-3.1` / `Rahman2019-SS`). One-line fix.
2. …

## 5. Gap matrix
| Dimension | Critical | High | Medium | Low | Headline finding |
|-----------|:---:|:---:|:---:|:---:|------------------|
| Reliability | | | | | |
| Security | | | | | |
| Cost | | | | | |
| Operations | | | | | |
| Performance | | | | | |
| Structural | | | | | |
| Architecture | | | | | |

### 5a. Future-state & principle alignment
- **Four Planes:** per-plane classification of in-scope stacks + any downward-only violations (esp. paths to Core back-office systems that bypass the Platform plane). (Source: live arch-platform guide.)
- **Rules of the Road (6):** each rule — Honored / Partial / Violated — with one evidence line.
- **Guiding Principles:** for each principle — Honored / Partial / Violated / Accepted-trade-off, with one evidence line. (Source: live principles page.)

## 6. Live-state verification
> Present only if state_check resolved to `on`. Otherwise: "Drift detection NOT performed — <reason: state_check=off | no az/terraform auth>."
| Stack | Finding type | Resource | Code value | Live/state value | Severity | Fix |
|-------|--------------|----------|-----------|------------------|----------|-----|

## 7. Roadmap — critical path to close the gaps
Sequenced by dependency, then impact-to-effort. Three phases:

### Phase 1 — Stabilize (highest weighted-severity + quick wins)
| # | Action | Closes | Principle/Pillar | Effort | Impact | Depends on |
|---|--------|--------|------------------|--------|--------|------------|

### Phase 2 — Standardize (modularize, enforce patterns, remove drift)
| # | Action | Closes | Principle/Pillar | Effort | Impact | Depends on |

### Phase 3 — Optimize (cost, performance, maturity to 4–5)
| # | Action | Closes | Principle/Pillar | Effort | Impact | Depends on |

**Critical path:** <the ordered chain of must-precede items, e.g. "establish module library → migrate Tier-1 stacks → add zone redundancy → enable drift CI">.
**Do-first set:** <2–4 quick, high-impact items to start this week>.

## 8. Coverage & limitations
- Scanners present/absent: <from tooling detection>.
- State verification: <performed on N stacks / not performed>.
- Future-state source: <arch-platform guide fetched live, v<X.X> / offline fallback used>.
- Principles source: <live page fetched / offline fallback used>.
- Depth: <standard sampling / deep fan-out>; stacks sampled vs scanned exhaustively.
- Anything explicitly out of scope this run.

## 9. Target operating model & governance
> The forward-looking layer — see `references/operating-model.md`. Decision-grade for an architecture review board. **Organize the whole report tactical-vs-strategic; this section is the strategic anchor.** Refer to the platform's golden-path template generically — do not name internal product/template brands.
- **What the team is dealing with (reflection):** infer the operating reality from code signals (toil/copy-paste, legacy weight, right-instincts-inconsistent-reach, manual-ops markers) — with empathy and evidence. State it plainly; the strategy follows from it.
- **Tactical vs strategic split:** label every move. Tactical = stop the bleeding / remove toil now (buys slack); strategic = durable operating-model change (spends it).
- **Repo strategy:** platform/landing-zone central · service IaC co-located in app repos · versioned module registry — with principle-based rationale and **named** stacks that move vs stay central.
- **Migration path:** incremental (modules-first → new-services-born-right → opportunistic backfill → central repo contracts). No big-bang.
- **Modernize the team:** automation (modules, gates, drift, CI) + AI (audit + generation skills in the loop) + capability (a small platform-engineering function; shift from infra-authoring to service-ownership). Frame as toil-relief first.
- **Policy-as-code gates:** the CI checks that turn *this run's* findings into preventive guardrails.
- **RACI + ways of working:** ownership across layers, and the developer / DevOps deltas post-change (platform-as-a-product).

## Appendix — full findings
The complete canonical-shape findings list (all dimensions), for traceability — each row includes its `source` tag(s).

## References
The Tier-1 standards and Tier-2 studies actually cited by findings in this report (full citations per `references/evidence-base.md`). List only sources that appear in a `source` tag above.
```

---

## Rendering notes
- Numbers in §2/§5 must reconcile with the appendix — don't hand-wave counts.
- Severities shown are **intent-weighted** (post-tier); note the raw severity in the appendix if it differed.
- Keep recommendations to one actionable line in the body; detail belongs in the follow-up change, not this report (this skill analyzes; it does not implement).
- Always publish to Confluence: pass the rendered scratch file to `prepass-branded-documentation` (or Atlassian MCP `createConfluencePage`) with parent = `confluence_parent` (default arch **Research** `420872209`); search by title to update vs duplicate; confirm before creating/updating. Never write the report into a repo.
