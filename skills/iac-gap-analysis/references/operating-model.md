# Target operating model & governance — the "where do we go" layer

A gap analysis that only lists defects and a fix-roadmap stops one altitude short of what an architect needs. This reference defines the **forward-looking operating model**: where IaC should live, who owns it, how it's governed, how the team modernizes, and how everyone works after the gaps are closed. Produce this as §9 of the report (`output-template.md`). Anchor every recommendation to the org's own principles — the strongest argument is "your stated future state already implies this."

## 0. Organize the whole delivery as tactical + strategic

Findings are not all the same altitude, and neither is the team's capacity to absorb them. **Split every recommendation into two tracks and say which is which** — this is the organizing premise of the report, not an afterthought:

- **Tactical (this repo, weeks):** stop the bleeding and remove toil *now* — the security blockers, the drift defects, the perpetual-diff noise. Things one or two people can land without reorg. These buy the team back time and credibility.
- **Strategic (the operating model, quarters):** the durable change — repo strategy, module registry, policy-as-code, team capability, automation + AI. This is where "modernize the team" lives.

The tactical track must visibly *create the slack* that funds the strategic track. Sequence accordingly.

## 1. Reflect on what the team is actually dealing with (read the codebase as evidence of the human system)

Before prescribing, infer the operating reality from code signals — the report should say this out loud, with empathy and evidence. Conway's law runs both ways: the IaC is an artifact of the team's constraints. Read for:

- **Toil/scaling-by-duplication** — zero modules + heavy copy-paste means the team ships by cloning stacks. That is what a **capable but under-resourced** team does with no platform-engineering capacity and delivery pressure — not incompetence.
- **Legacy weight** — old product/OS/db versions (e.g. CRM-2013/2016-era servers, SQL-2014, ERP boxes, "legacy" suffixes) signal a team carrying a decade-plus of systems-of-record alongside modern work. Modernization must respect that load, not ignore it.
- **Right instincts, inconsistent reach** — adoption of good patterns (managed identity, Key Vault refs, a messaging spine) *somewhere* but not *everywhere* means the team knows the target; they lack the **mechanism** (modules, automation) to apply it uniformly.
- **Manual/fragile ops markers** — `timestamp()` tags, workspace-switch mega-`locals`, secrets slipping into lower envs, default/Basic SKUs → little automation headroom, much firefighting.

The conclusion this usually supports: **relieve toil first (give time back), then build the paved road** — do not pile more process on a stretched team. State the team's likely reality and let the strategy follow from it.

## 2. Where IaC should live — the repo-strategy decision

Frame it as three tiers of ownership, not one monorepo:

| Tier | What it is | Where it lives | Owner |
|------|-----------|----------------|-------|
| **Platform / Landing Zone** | Networking, DNS, shared gateways/WAF, shared Key Vaults, Log Analytics, subscriptions, RBAC, policy | **Central platform repo** | Platform / DevOps team |
| **Service / App IaC** | A service's *own* compute, data store, messaging, cache, config | **Co-located in the app's repo** (`/infra`), deployed by the app's pipeline | Product / service team |
| **Modules** | Reusable, hardened building blocks (TLS floor, diagnostics, tags, identity, zone-redundancy) | **Versioned module registry** — *prefer adopting/wrapping published verified modules over building from scratch* | Platform team (maintain), product (contribute) |

> **Don't build the registry from zero — adopt verified modules.** For Azure, **Azure Verified Modules (AVM)** (`Azure/avm-res-*/azurerm` on the Terraform Registry, Microsoft-maintained) ship Well-Architected best practices *by default* — availability zones, private endpoints, Entra-ID auth, RBAC, diagnostics. For AWS, the `terraform-aws-modules` family is the equivalent. An under-resourced team should **wrap** these (thin org-defaults layer) rather than author and maintain its own — it closes the zero-modules root cause *and* the security/resiliency findings at the module layer simultaneously, with far less build/maintain cost.

**The principled argument for co-locating service IaC with app code:** if the org espouses **Vertical Slices** (a feature owns its full stack down to data) and **Autonomous Services** (independently developed/deployed), then a service's infrastructure *is part of its slice*. A central infra-monorepo holding every service's infra is **coupling dressed up as centralization** — a service can't change or deploy without a PR in someone else's repo.

**Counter-balance (don't over-rotate):** truly shared, blast-radius-wide infra (networking, DNS, shared gateways, identity foundation) **stays central**. Test: *"if this resource changed, whose blast radius?"* One service → app repo; many services / the platform → central.

## 3. Migration path — incremental, never big-bang

1. **Stand up the module layer first** — adopt verified modules (AVM / `terraform-aws-modules`) + a thin org-defaults wrapper, rather than authoring from scratch. Closes the zero-modules finding and is the precondition for everything else.
2. **New services born right** — the **golden-path service template** ships with an `/infra` dir consuming the modules; new service infra never enters the central monorepo. *(Name the platform's template generically — the concept, not a specific product name.)*
3. **Backfill opportunistically** — migrate a service's infra into its app repo when the team is already working that service. No mass migration.
4. **Central repo contracts** to platform/landing-zone + a shrinking legacy holding pen.

## 4. Modernize the team — automation + AI + capability (the strategic core)

"Modernize the team" is concrete, and it is mostly about **removing toil so a stretched team can do higher-value work**:

- **Automation that pays the team back first:** module registry (stop cloning), policy-as-code gates (stop manual review catching the same issues), scheduled drift detection (stop portal-archaeology), CI plan-on-PR/apply-on-merge (stop heroic deploys).
- **AI leverage:** an **audit skill** (this one) for periodic gap analysis; a **generation skill** for authoring IaC well (pairs as the paved-road guardrail — see the generation-vs-audit complementarity); the **official `hashicorp/terraform-mcp-server`** in the dev/agent loop for live provider-doc lookup, registry/AVM module discovery, config validation, and Sentinel-policy retrieval (grounds both authoring and this audit in current provider schemas — kills attribute-name hallucinations); AI-assisted PR review and `terraform test` generation. The goal is the team *operating with AI in the loop*, not more dashboards.
- **Capability / org shape:** stand up a small **platform-engineering** function (even 1–2 people) to own the paved road; shift the rest from *infra-authoring* to *service-ownership*. **Platform-as-a-product**, internal teams as customers.
- **Skills uplift:** Terraform modules + policy-as-code + the AI workflow are learnable; pair the legacy-maintenance load with explicit modernization time so the team isn't only firefighting.

## 5. Governance — encode the findings as preventive gates (shift-left)

Every recurring gap becomes a **policy-as-code gate** so it can't recur:

- **PR gates in every IaC pipeline:** `terraform validate` + `tflint` + **checkov** + **OPA/Conftest** (or **Sentinel**, discoverable via `terraform-mcp-server`) for org rules (no public access on data tiers; Tier-1 zone-redundant; secrets only via Key Vault; diagnostics required; required tags). Adopting verified modules (AVM) means many of these pass *by construction*, so the gates mostly police hand-rolled exceptions.
- **Cost feedback on PR:** `infracost` diff (self-hosted if egress-sensitive — see `infracost-self-host.md`).
- **Plan on PR, apply on merge**, required reviews; no manual portal changes to managed resources.
- **Scheduled drift detection** on Tier-1 stacks — catches code≠live defects.

## 6. Ownership / RACI

| Concern | Responsible | Accountable | Consulted |
|---------|-------------|-------------|-----------|
| Landing zone / shared infra | Platform team | Platform lead | Architecture, Security |
| Service infra (`/infra` in app repo) | Product/service team | Service owner | Platform (module owners) |
| Module registry | Platform team | Platform lead | Product (contributors) |
| Policy-as-code / guardrails | Platform + Security | Architecture | All teams |
| Drift remediation | Owning team of the stack | per above | Platform |

## 7. Ways of working — after the change

- **Developers:** own their service's `/infra`, assemble from paved-road modules, get security + cost feedback on every PR, deploy via their own pipeline. *"You build it, you run it"* → *"you provision it — from the paved road."*
- **DevOps / Platform team:** shifts from *writing all the infra* to *owning the paved road* — modules, landing zone, policy gates, drift monitoring, golden-path templates, AI tooling. Platform-as-a-product.
- **Architecture:** owns the principles **and the policy-as-code that encodes them** — alignment enforced by CI, not review vigilance.

## How to render this in the report

§9 must be **decision-grade** and organized tactical-vs-strategic (§0). Give: (a) the team reflection (§1) — what they're dealing with, with evidence; (b) repo-strategy with rationale specific to this estate (name the actual stacks that move vs stay central); (c) the incremental migration sequence; (d) the team-modernization plan (automation + AI + capability); (e) policy-as-code gates derived from *this run's* findings; (f) a RACI; (g) the ways-of-working delta. Do **not** name specific internal product/template brands — refer to "the platform's golden-path template" generically. Fold the do-first governance moves into the §7 roadmap so model and fixes are one plan.
