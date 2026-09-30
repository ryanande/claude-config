# Architectural Lens

> The one-pager every routine references. Written by the Chief Architect, used as the **filter** for daily PR / meeting / chat digests. Re-read quarterly; update whenever a principle, plane rule, or strategic priority shifts.

## Role and scope

Chief Architect at PrePass. Authoring authority on the Architecture Guiding Principles and General Coding Guidance in Confluence's `arch` space. Owns the Future-State Platform Strategy (the Four-Plane architecture). Approves all ADRs in [PrePass/ADRs](https://github.com/PrePass/ADRs) on behalf of the Architecture Team.

**Daily PR-review scope: all ~197 PrePass repos.** The lens (not the scope) does the filtering.

## Source-of-truth documents

Routines should link to these when explaining "why this matters." The lens below is a working filter that **summarizes and angles** these for PR review — when the source changes, update the lens.

| Source | Covers |
|---|---|
| [Architecture Guiding Principles](https://prepass.atlassian.net/wiki/spaces/arch/pages/10223624/Architecture+Guiding+Principles) | The 13 principles below |
| [General Coding Guidance](https://prepass.atlassian.net/wiki/spaces/arch/pages/12025876/General+Coding+Guidance) | Do's / Don'ts / Considerations across CSharp, testing, source control, distributed design, PR formatting, conventional commits |
| Future-State Platform Strategy ([arch-platform](https://github.com/PrePass/arch-platform) Pages site) | Four-Plane architecture, FLINT / ONYX, modular monolith rationale, CDC + read models |
| [PrePass/ADRs](https://github.com/PrePass/ADRs) | Architectural decisions, categorized: API · Bypass · DevOps · Enterprise · Global · Mobile · UI |
| [dx-aicentral/ARCHITECTURE.md](https://github.com/PrePass/dx-aicentral/blob/main/ARCHITECTURE.md) | Three-class information model, progressive disclosure, passport schema |
| [arch-rover reports/](https://github.com/PrePass/arch-rover/tree/main/reports) | Daily org-wide scanned facts (template inventory, NuGet drift, gh-pages audit) |

### Confluence child pages worth referencing in digests

**Distributed design** (under General Coding Guidance):
- Designing Features in a Message-Based, Eventually Consistent World
- Explaining Message-Based Systems & Eventual Consistency
- The 11 Fallacies of Distributed Computing
- Replicated View Models for Fast Reads
- Three-Plane Architecture Overview
- From Batch → Distributed Messaging (NServiceBus)
- Validation in a Distributed World

**Testing**: Key Principles for Testing · Good vs Bad Tests · Code Coverage · Test Fakes · Assertion Libraries · Test Suite Health · Integration test patterns · Test Plan and Strategy

**Process**: Reviewing Pull Requests · PR Formatting · Conventional Commits Standard · CSharp · Source Control

---

## Owned domains

**Architectural standards & decisions** — the four sources above.

**The three-class information architecture** (per [dx-aicentral/ARCHITECTURE.md](https://github.com/PrePass/dx-aicentral/blob/main/ARCHITECTURE.md)):

| Class | Owner | Holds |
|---|---|---|
| 1 — Scannable facts | [arch-rover](https://github.com/PrePass/arch-rover) | Template lineage, package versions, gh-pages, contract paths |
| 2 — Contextual knowledge | Per-repo `CLAUDE.md` passport | Bounded context, contracts, non-obvious behavior |
| 3 — Cross-repo relationships | [dx-prepass-meta/docs/](https://github.com/PrePass/dx-prepass-meta) | Domain choreography, library dependency chain, ADRs spanning multiple repos |

**AI tooling & developer experience** — dx-aicentral (skills via APM), dx-prepass-meta (workspace), arch-rover (automated reporting).

---

## The Four-Plane architecture

Every change should be classifiable into a plane. PRs that violate plane rules go straight to **NEEDS MY EYES**.

| Plane | Role | Template |
|---|---|---|
| **1 — Engagement** | Customer touchpoints (mobile, web, customer APIs) | — |
| **2 — Experience (FLINT)** | Product features, workflow orchestration, journey isolation | FLINT |
| **3 — Platform (ONYX)** | Core business capabilities, DDD service envelopes; owns business rules + data + messaging | ONYX · DDD |
| **4 — Back Office** | ERP, CRM, D365, Payments — wrapped by ONYX, never touched directly above | (systems of record) |

### The non-negotiables

- **Dependencies flow downward only.** Never upward, never sideways.
- **Engagement must be replaceable** without FLINT or ONYX needing to change.
- **FLINT is API-only.** No UI, no direct DB access to another FLINT service's database, no direct ERP / CRM access.
- **No layer above ONYX ever calls ERP / CRM / D365 / Payments directly.** All access goes through ONYX.
- **202 Accepted for async commands.** Sync HTTP between services for write operations is a smell.
- **Modular monolith first; split only with evidence** (load, autonomy, team boundary). We earn complexity, we don't start with it.

---

## Architectural patterns — celebrate vs. flag

For each principle, what a good PR looks like (✓) and what to escalate (⚠).

### Choreography over Orchestration
✓ New service publishes domain events; downstream services subscribe.
⚠ Central orchestrator added; sync chains of `A → B → C`.

### Async over Sync
✓ NServiceBus command for mutations; 202 Accepted at the API edge.
⚠ New synchronous HTTP call between services for writes; "I'll just poll B's API."

### Consumer-Driven Contracts
✓ Provider change accompanied by Pact contract test update on the consumer side.
⚠ Provider changes API shape unilaterally; no contract test exercised.

### Autonomous Services
✓ New service owns its data; clear contract entry/exit points.
⚠ Cross-service direct DB read; shared schema; co-edited tables.

### Coarser Services before Granular
✓ Capability added inside an existing ONYX service envelope.
⚠ Premature microservice split with no ADR justifying it.

### Make the Old Depend on the New
✓ Adapter / API / abstraction added so legacy depends on the new code.
⚠ New code calls directly into legacy with no buffer.

### Vertical Slices
✓ PR delivers a complete feature top-to-bottom (UI / API / handler / data) for one capability.
⚠ Horizontal-only PR that requires N follow-ups to be usable.

### Build Apps the Way the Business Works
✓ Domain language matches business terms; aggregate boundaries match real ownership.
⚠ Technical naming dominates; entities cross natural domain seams.

### Observable Services
✓ Structured logs / metrics / traces ship with the feature.
⚠ `println` style logs; new code path with no instrumentation.

### Pragmatism over Dogmatism
✓ Deviation from a principle is documented in an ADR with rationale.
⚠ Strict pattern enforcement that doesn't fit reality, or — the inverse — deviation with no ADR.

### Business / Customer Needs First
✓ PR description names the business or customer problem.
⚠ Pure technical change with no stated business value.

### Business Problem over Tech Trends
✓ Tech choice has an ADR linking it to the problem.
⚠ "Let's adopt $shiny" — library upgrade or rewrite with no ADR.

### Well-Architected Framework
✓ Op excellence / security / reliability / cost / performance considered together.
⚠ Single-pillar optimization that compromises another (perf change that weakens security model, etc.).

---

## Anti-patterns → automatic NEEDS MY EYES

Any of these in a PR escalates regardless of size:

- **Layer violation** — code calling sideways or upward across planes
- **Direct ERP / CRM / D365 / Payments access** from anything other than ONYX
- **Sync HTTP between services for mutations** (use NServiceBus + 202)
- **Cross-service DB read or shared schema** between autonomous services
- **New microservice without an ADR** justifying the split
- **Provider contract change without consumer contract test update**
- **New code path with no logging / metrics / tracing**
- **PR touching `src/Contracts/`** (commands or events) — cross-team contract change
- **PR with no description / no business context** (violates "business needs first")
- **Hand-maintained data that arch-rover scans** (template versions, package versions, CI shape) — Class 1 drift into Class 2
- **Non-trivial architectural decision with no ADR link**
- **New repo with `src/` but no `CLAUDE.md` passport**
- **Engagement-layer code referencing FLINT or ONYX internals** — replaceability violation

---

## Cross-team contracts to watch

A PR touching any of these is a candidate for NEEDS MY EYES:

- `src/Contracts/Commands/**` — NServiceBus commands
- `src/Contracts/Events/**` — NServiceBus events
- `tests/ContractTests/**` — Pact contract tests
- HTTP API surface (changes that propagate into `swagger.yaml`)
- `dx-prepass-meta/docs/domains/{context}/GLOSSARY.md` — domain language
- `dx-prepass-meta/docs/SERVICE_ARCHITECTURE.md` — service patterns
- `dx-prepass-meta/docs/platform-libraries.md` — library dependency chain
- `PrePass/ADRs/**/*.md` — new or modified ADR (Architecture Team approval)
- Per-repo `CLAUDE.md` — passport identity

---

## Repo categories (for org-wide PR scanning)

PrePass org has ~197 repos. Default behavior:

- **Scan:** all repos
- **Down-rank** (still surface, but lower priority): `aux-*`, `poc-*`, anything under the `Innovation/` group
- **Soft-exclude**: anything explicitly marked `experimental` or `sandbox` (configured in `routines/pr-intelligence/config.yaml`)
- **Treat as critical:** repos under the four-plane templates (Onyx-based services, FLINT-based services), `lib-core-*`, `dx-aicentral`, `arch-rover`, `arch-platform`, `dx-prepass-meta`, anything under `api-public-*`

---

## Current strategic priorities

> Update often. Last updated: 2026-05-06.
>
> Tied to engineering leadership's 2026 SMART goals (G1–G5). 2026 is the year ONYX becomes real: G2 and G5 build the first ONYX services in earnest; G1 stress-tests plane discipline as ERP arrives; G3 and G4 are classification forks. The lens biases attention toward this throughline.

### 1. ONYX foundation patterns (G2 + G5)

The first ONYX services — Auth, Account / Customer, Truck / Vehicle, Device — establish the precedent every future ONYX service will copy. Patterns set now ripple for years. Be extra stingy on these PRs.

**Flag in PRs:**
- Touches `plfm-auth`, `plfm-customer`, `plfm-truck`, `plfm-device`, or `lib-core-*`
- Premature service splitting (stay coarse-grained per "Coarser before Granular")
- Cross-context coupling that suggests wrong aggregate boundaries
- Deviation from the FLINT-calls-ONYX pattern in surrounding code

### 2. Distributed messaging maturity (G2 messaging arm)

G2 explicitly mandates messaging for all create / update / soft-delete operations. Every team's first NServiceBus exposure happens in this work — errors here become the patterns everyone copies. Watch ferociously.

**Flag in PRs:**
- New NServiceBus contracts (`src/Contracts/Commands/**`, `src/Contracts/Events/**`)
- Sync HTTP calls between services for mutations (should be NSB + 202 Accepted)
- Missing 202 Accepted on command endpoints
- CQRS / read-model implementations — the first ones set the pattern
- Retreat to sync batch-style work where strategy says async

### 3. Back-office containment (G1 + G3 + G4 supporting)

ERP is arriving (G1). The four-plane non-negotiable says nothing above ONYX touches ERP / CRM / D365 / Payments. Enforce **before** ERP integration work piles up shortcuts. G3 (toll savings to InformTolls) and G4 (OCR violations) are early tests — both involve back-office data; both must route through ONYX.

**Flag in PRs:**
- Any direct ERP, CRM, D365, or payments call from non-ONYX code
- InformTolls / Engagement work wanting to "just query back office directly"
- OCR work (G4) — confirm it's an ONYX capability, not leaky automation
- New ADRs proposing ERP integration patterns — Architecture Team review required

---

## Noise budget

- **Each digest = 10 items max.** Force prioritization.
- **Exclude before ranking:**
  - Dependabot / Renovate / GitHub Actions bots (unless touching a critical dep)
  - Pure docs / typo / formatter-only PRs
  - `experimental` / `sandbox` repos and `Innovation/` POCs
  - Authors / titles in `routines/<routine>/config.yaml` exclusion lists
- **Architectural relevance trumps code quality.** This lens is the architect's filter, not a general code review.
