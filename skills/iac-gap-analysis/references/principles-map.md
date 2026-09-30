# Principles map — PrePass Architecture Guiding Principles → IaC-observable signals

The PrePass future state is defined by two aligned sources: the **Platform Architecture — Future State Guide** (the target topology — see `references/future-state-model.md` for the Four Planes + Rules of the Road) and the **Architecture Guiding Principles** in the `arch` Confluence space (the beliefs, below). This file maps each principle to signals an IaC reviewer can actually observe in a Terraform repo, so adherence/violation is grounded in evidence rather than opinion. The guide restates these as 12 principles (folding the WAF-reading entry in and adding "Observable by Design"); they are the same family — score against the live sources, and treat `future-state-model.md` as primary where the two differ in resolution.

## Fetch live first

The principles evolve. **Before scoring, fetch the live page** so the analysis measures against the current statement of intent:

- Atlassian MCP → `getConfluencePage` with `pageId` = `principles_page` (default `10223624`), `contentFormat: markdown`, on cloud `prepass.atlassian.net`.
- If the fetch fails, fall back to the digest below and flag it under "Coverage & limitations" in the report.

The digest below is a point-in-time snapshot for offline fallback — **the live page wins** on any discrepancy.

## The 14 principles and their IaC tells

| # | Principle | What it means for infra | Adherence signals (good) | Violation signals (gap) |
|---|-----------|------------------------|--------------------------|-------------------------|
| 1 | **Business & Customer Needs First** | Tech serves strategy; resources trace to a business capability | Stacks named/tagged by business domain; clear ownership | Orphan resources with no owner/domain tag; infra with no traceable purpose |
| 2 | **Business Problem over Tech Trends (tech minimalism)** | Don't provision novelty; prefer suitable + cost-effective | Consistent, justified service choices; ADRs referenced | Redundant overlapping services; exotic SKUs with no rationale; "because it's new" |
| 3 | **Well-Architected Framework as a Guideline** | The 5 Azure WAF pillars are the bar | See `azure-checks.md` — pillars actively addressed | Pillars unaddressed (this is the whole gap matrix) |
| 4 | **Choreography over Orchestration** | Decentralized, event-driven control | Service Bus / Event Hub / Event Grid as the spine; pub-sub | Central orchestrator stacks; tight point-to-point chains; a hub all services route through |
| 5 | **Async over Sync** | Decouple via queues/streams | Service Bus queues/topics, Event Hub, durable functions | Direct synchronous coupling provisioned (e.g. only HTTP triggers where events fit); no DLQs |
| 6 | **Consumer-Driven Contracts** | Interfaces shaped by consumers | APIM products/versioning; explicit API surfaces | Unversioned shared endpoints; breaking-change-prone shared infra |
| 7 | **Autonomous Services** | Self-contained, own data, independent deploy | Per-service stacks with own state, own data store, own pipeline | Shared databases across services; one state file spanning many services; coupled deploys |
| 8 | **Coarser Services before Granular** | Avoid distributed monolith | Sensibly-sized service boundaries | Proliferation of tiny stacks with chatty interdependence; OR a single god-stack |
| 9 | **Make the Old Depend on the New** | Phased modernization | New services fronted by APIM/adapters; legacy calls into new | New code reaching back into legacy DBs/servers; modern depending on legacy |
| 10 | **Vertical Slices** | Feature owns its full stack | A service dir contains its compute + data + messaging + config together | Horizontal splits where one slice's resources are scattered across many dirs |
| 11 | **Build the Way the Business Works** | Infra mirrors business processes | Domain-aligned grouping (e.g. Tolls, Identity, OCR) | Tech-only grouping that obscures the business process; semantic coupling baked into infra |
| 12 | **Observable Services** | Logging/monitoring/tracing built in, not bolted on | App Insights + diagnostic settings + Log Analytics on every stack; alerts | Resources with no `azurerm_monitor_diagnostic_setting`; no App Insights; no alerts |
| 13 | **Pragmatism over Dogmatism** | Practical over rigid | Defensible trade-offs documented | (Use as a *guard* — don't flag a justified deviation as a gap; note it as accepted) |
| 14 | *(WAF reading links — folded into #3)* | — | — | — |

## How to use this map

- For each stack, note which principles it **honors** and which it **violates**, with evidence.
- Principle violations are findings in the **Architecture Alignment** dimension of the gap matrix (`references/gap-matrix.md`), and several map onto WAF pillars too (e.g. #12 Observable → Operational Excellence; #5 Async → Reliability).
- Principle #13 (Pragmatism) is a **meta-guard**: before logging a principle violation, ask whether the deviation is a defensible trade-off. If so, record it as an accepted trade-off in the report, not a gap.
- Repo-wide structural patterns (e.g. "zero modules across 547 files", "no zone-redundancy anywhere") are strong evidence for #7/#8/#10 and the Structural dimension — quantify them with Grep counts.
