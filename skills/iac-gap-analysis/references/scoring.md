# Scoring — severity, intent weight, stack-rank, maturity

The point of scoring is to make the report **actionable and honest**: the worst, most-exposed problems float to the top; defensible trade-offs don't masquerade as defects; and a single maturity number per dimension lets leadership track movement over time.

## 1. Raw severity

Assign each finding a raw severity from its blast radius and likelihood, independent of where it lives:

| Raw | Meaning |
|-----|---------|
| Critical | Exploitable exposure, data-loss risk, or guaranteed outage on failure |
| High | Serious weakness; likely incident or compliance failure under stress |
| Medium | Real gap; degrades a pillar but not imminently dangerous |
| Low | Hygiene / polish; minor risk |

## 2. Intent weight

Multiply raw severity by the criticality tier from `intent-inference.md`:

| Tier | Weight | Effect |
|------|--------|--------|
| Tier 1 (critical: prod payment/identity/DMZ/regulated) | ×1.5 | Medium→High, High→Critical |
| Tier 2 (standard prod) | ×1.0 | unchanged |
| Tier 3 (lower env) | ×0.5 | High→Medium, Medium→Low (secret hygiene never drops below Medium) |

This is the mechanism behind "stricter bar for production-payment-gateway than sandbox." Apply it per finding — never average severities across tiers.

## 3. Pragmatism guard

Before a principle-deviation becomes a gap, ask: is this a **defensible trade-off**? (Their principle #13.) If yes — single region for a genuinely region-local workload, a coarse service that's coarse by design — set `accepted_tradeoff: true` and render it as a noted trade-off, not a gap. Document the rationale. This keeps the report credible; over-flagging is how a critical review loses its audience.

## 4. Stack-rank (both columns)

- **Gaps**, worst-first: sort by weighted severity, then by number of principles/pillars implicated, then by blast radius. Ties broken by lower effort (quick high-impact wins rank up).
- **Strengths**, best-first: sort by how load-bearing the strength is (how much risk it's currently absorbing) and how widely it's applied. Leadership needs to know what *not* to break.

Present both as numbered lists. The reader should be able to stop after the top 5 of each and still know the story.

## 5. Maturity score (per dimension, 1–5)

| Score | Band | Meaning |
|-------|------|---------|
| 5 | Optimized | Consistently strong; few/no findings; patterns enforced |
| 4 | Managed | Mostly strong; isolated Medium gaps |
| 3 | Defined | Patterns exist but unevenly applied; several Medium/High |
| 2 | Developing | Significant gaps; reactive; High findings common |
| 1 | Initial | Largely unaddressed; Critical findings present |

Compute per dimension from the weighted finding distribution. Then a **weighted overall** — by default weight `security` and `reliability` highest (×1.5), others ×1.0 — and state the weighting in the report so it's reproducible. Tie the bands to the org's "Architecture Maturity Strategy" framing where it exists.

## 6. Roadmap sequencing inputs

Each gap carries `effort ∈ {S,M,L}` and `impact` (= weighted severity × breadth). The roadmap (`output-template.md`) orders by **dependency first** (you can't add zone redundancy before modularizing the resource if that's the precondition), then by impact-to-effort ratio within a phase. Quick high-impact wins are called out explicitly as a "do first" set.
