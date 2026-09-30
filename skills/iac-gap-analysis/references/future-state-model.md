# Future-state model — the Four Planes + Rules of the Road

The canonical statement of PrePass's **target architecture** is the **Platform Architecture — Future State Guide** (currently v1.2, May 2026), published at the private GitHub Pages site backed by the **`PrePass/arch-platform`** repo. The gap analysis measures the IaC against this model, not just generic best practice. Where the Confluence Guiding Principles (page `10223624`) state *beliefs*, this guide states the *target topology and non-negotiable rules* — it is the higher-resolution future state.

## Fetching it (private Pages — do NOT use WebFetch)

The site is **private GitHub Pages** (`https://vigilant-dollop-g44q9q1.pages.github.io/`). WebFetch fails on it (302 → GitHub auth). Fetch the source through authenticated `gh` instead:

```bash
gh api repos/PrePass/arch-platform/contents/index.html --jq '.content' | base64 -d \
  | python3 -c "import sys,re,html;t=sys.stdin.read();t=re.sub(r'<(script|style).*?</\1>','',t,flags=re.S|re.I);t=re.sub(r'<[^>]+>',' ',t);print(html.unescape(re.sub(r'[ \t]+',' ',t)))"
```

Most substance lives in the landing `index.html`; deeper decks live under `talks/`. If `gh` is unauthenticated or the repo is unreachable, fall back to the model captured below and flag it under "Coverage & limitations" — but the **live repo wins** on any discrepancy (the version stamp moves).

## The Four Planes

The platform is four layers. **Dependencies flow downward only — never upward, never sideways.** This is the core invariant.

| Plane | Name | Owns | Example PrePass resources |
|-------|------|------|---------------------------|
| 1 | **Engagement** | Customer touchpoints; thin presentation only | Static.WebApps, Front.Door, Mobile app services, customer-facing APIs |
| 2 | **Experience (FLINT)** | Product features, workflow orchestration, journey isolation, UX resilience | FLINT-template services / feature APIs |
| 3 | **Platform (ONYX)** | Business capabilities, business rules, data, messaging — the source of truth | ONYX service envelopes, their own data stores + Service Bus/Event Hub |
| 4 | **Core / Back Office** | Systems of record, wrapped by ONYX as an anti-corruption layer | the legacy VMs — CRM* servers, GP.Server, AGRSQL14, D365, payment processors |

**The core rule:** the Engagement plane should be fully replaceable without any FLINT/ONYX change; **only ONYX** ever connects to Core (ERP/CRM/D365/payments).

## The six Rules of the Road (non-negotiable) → IaC tells

These are where the future state becomes checkable in Terraform. Map each to the `architecture` dimension; several also light up `security`, `reliability`, and `structural`.

| # | Rule (verbatim intent) | IaC-observable signal (good) | Violation in IaC (finding) |
|---|------------------------|------------------------------|----------------------------|
| 1 | New features start from the **FLINT golden-path template** (messaging, CI/CD, API publishing, observability built in) | New service stacks scaffolded consistently; CI_CD-Templates reused; observability + messaging wired by default | Bespoke/copy-pasted stacks missing the baseline wiring; drift from template |
| 2 | **FLINT→ONYX only; nothing calls ERP/CRM/D365/payments directly** except ONYX | Upper-plane resources have no network path / connection string / private endpoint to the Core VMs (CRM*, GP, AGRSQL14) | An Engagement/FLINT stack with a direct connection, NSG rule, private endpoint, or app-setting pointing at a Core back-office system = **plane violation (High+)** |
| 3 | **Messaging first** — commands over messaging, HTTP for queries only | Service Bus/Event Hub provisioned as the integration spine; ONYX writes to back-office **async** | Direct synchronous service-to-service coupling provisioned where a command/event belongs; no messaging tier for a write path |
| 4 | **Services own their data — no cross-service DB access** | Each service stack owns its own data store + its own state; reads come from event-built read models | A database referenced by more than one service; shared connection strings across stacks; one state file spanning multiple services = **autonomy violation** |
| 5 | **Message contracts versioned + published (NuGet)** | (Mostly app-layer) APIM versioning; no breaking shared endpoints | Unversioned shared endpoints provisioned as a single choke point |
| 6 | **Design for failure** — retry/backoff, circuit breakers, **dead-letter queues**, structured logging at every integration point | Service Bus/Event Hub with `dead_lettering_on_message_expiration`, sensible `max_delivery_count`; diagnostic settings everywhere; Front Door health probes | Queues/topics with no DLQ; no retry/health-probe config; integration points with no diagnostic logging = **resilience gap** |

## Vision tenets that bind IaC directly

From the guide's "Our Vision" — the ones an IaC reviewer can actually score:

- **Autonomous & Observable Services** → every stack instrumented (App Insights + diagnostic settings) and independently deployable. (= Confluence principle #12, guide principle #11.)
- **Messaging-Driven Integration** → Service Bus/Event Hub spine; no direct DB sharing; no hidden coupling.
- **Secure by Default** → "Security baked into **pipelines, IaC, and containers** from the start. DevSecOps is a first-class concern, not a checkbox." → Expect security scanning in `CI_CD-Templates`, hardened container definitions, private-by-default networking, managed identity. **Absence of DevSecOps in the IaC/pipeline layer is a direct future-state gap**, not just a security nit.
- **Measured, not Guessed** → DORA/SPACE. Less IaC-direct, but the observability infrastructure (Log Analytics, App Insights, diagnostic export) is the enabler — flag if the telemetry plumbing that DORA/SPACE depend on is absent.

## How to apply

- Add a **"Four Planes alignment"** read to the `architecture` dimension: classify each stack into a plane (Engagement/FLINT/ONYX/Core) and check that its network/data connections only flow downward. **Upward or sideways connections, and any non-ONYX path to a Core back-office system, are headline architecture findings.**
- Score the six Rules of the Road explicitly in §5a of the report alongside the 12/14 principles — they are the testable expression of the principles.
- The guide's current-state pains ("immature observability", "no modern DevOps baseline", "heavy backend dependencies") are the **gaps the future state exists to close** — if the IaC still exhibits them, say so plainly and tie each to the tenet it violates.
