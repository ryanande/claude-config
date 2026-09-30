# Gap matrix — the master rubric

The analysis evaluates the codebase across **seven dimensions** at once. The first five are the Azure Well-Architected pillars (the org's stated bar via principle #3); the last two cover IaC engineering health and how faithfully the code expresses the PrePass principles. A thorough review never collapses to "just security."

## The seven dimensions

| Key | Dimension | Rooted in | Core question |
|-----|-----------|-----------|---------------|
| `reliability` | **Reliability & Resiliency** | WAF Reliability | Will it survive a zone/region/dependency failure? |
| `security` | **Security & Compliance** | WAF Security + CIS/SOC2/ISO | Is it exposed, unencrypted, over-permissioned, or non-compliant? |
| `cost` | **Cost Optimization (Financial Leakage)** | WAF Cost | Is it provisioned beyond need, on legacy/expensive SKUs, or idle? |
| `operations` | **Operational Excellence** | WAF Operational Excellence | Can we observe, deploy, and recover it safely and repeatably? |
| `performance` | **Performance Efficiency** | WAF Performance | Is it sized and configured to meet load efficiently? |
| `structural` | **Structural / IaC Health** | Engineering hygiene | Is the code modular, DRY, secret-clean, and free of dead/orphaned blocks? |
| `architecture` | **Architecture Alignment** | PrePass 14 principles | Does the infra express choreography, async, autonomy, observability, vertical slices? |

`--dimensions` can restrict to any subset; default is all seven.

## What each dimension checks

Resource-specific checks live in `references/azure-checks.md`. This is the dimension-level intent.

### reliability
- Zone redundancy / Availability Zones / multi-AZ on stateful and gateway resources.
- Multi-region or documented single-region acceptance; failover/replication for data stores.
- Autoscaling vs fixed capacity; health probes; retry/DLQ on messaging.
- **Single points of failure** — a resource whose loss takes down a critical path with no redundancy.
- Backup/restore + RPO/RTO posture for data tiers.

### security
- Public network exposure (`public_network_access_enabled = true`, open NSGs, blob public access).
- Private endpoints / VNet integration where the data tier warrants it.
- Encryption in transit (min TLS) and at rest (CMK vs platform key for Tier-1).
- Identity: managed identity vs connection strings/keys; least-privilege RBAC vs broad roles.
- **Secret hygiene** — literal secrets vs Key Vault references (semantic, not keyword — see below).
- CIS Azure / SOC2 / ISO control mapping, with the bar set by criticality tier.

### cost
- **Price the deployed inventory, not the sampled code** (see `cost-method.md`): actuals from Cost Management if permitted, else Azure Resource Graph across all subs/envs × public retail prices. A code-sampled slice is *not* the estate total — anchor on VM fleet / App Service Plans / Container Apps / Databricks, not data-tier Basic SKUs.
- Legacy/over-priced SKUs where a cheaper equivalent exists (Azure analog of the gp2→gp3 example: e.g. older VM series, Premium where Standard suffices, oversized App Service plans, un-tiered storage).
- Provisioned-but-idle or orphaned resources (also a structural finding when never referenced).
- Always-on vs consumption where bursty; over-provisioned throughput (Cosmos RU/s, Event Hub TUs).
- Missing autoscale-to-zero / dev-env shutdown.

### operations
- **Observability** (principle #12): App Insights, `azurerm_monitor_diagnostic_setting`, Log Analytics wiring, alerts.
- Tagging completeness/consistency for ops + cost allocation; the `Creation Date = timestamp()` perpetual-diff antipattern.
- IaC repeatability: pinned `required_version`/provider versions; remote state with locking; no manual drift.
- Deployment safety: per-service pipelines, plan-before-apply, no destroy-prone patterns.

### performance
- Right-sized compute/throughput for stated load; caching (Redis) where appropriate.
- CDN/Front Door for edge; connection pooling; partitioning strategy on data stores.
- Synchronous chains that add latency where async would serve (overlaps `architecture`).

### structural
- **Modularization / DRY** — copy-pasted resource blocks vs reusable modules. Quantify (e.g. `module` block count vs stack count).
- **Dead code & orphans** — declared variables never referenced, commented-out blocks, locals never used, stacks no longer wired to anything.
- Hardcoded values that should be variables/locals; magic strings; deeply nested conditionals.
- State hygiene — monolithic state spanning many services; missing locking.
- Consistency — divergent patterns for the same resource type across services.

### architecture
- **Four Planes alignment** (via `references/future-state-model.md`): classify each stack into Engagement / FLINT / ONYX / Core, and verify connections flow **downward only**. An upper-plane stack with a direct path (connection string, private endpoint, NSG rule, app setting) to a Core back-office system (CRM*, GP.Server, AGRSQL14, D365, payments) — i.e. bypassing ONYX — is a **headline plane violation**.
- **The six Rules of the Road** (via `references/future-state-model.md`): FLINT golden-path baseline, FLINT→ONYX-only, messaging-first, services-own-their-data (no shared DB / no multi-service state file), versioned contracts, design-for-failure (DLQs, retries, health probes, structured logging). Score each explicitly.
- The 14 principles via `references/principles-map.md`: choreography vs orchestration, async vs sync, autonomous services, coarse-vs-granular boundaries, vertical slices, make-old-depend-on-new, business-aligned grouping.
- Flag both directions: distributed monolith (too coupled) and god-stack (too coarse).

## Beyond regex — the semantic floor

Keyword matching produces false positives. Read for meaning:

- A `password`/`connection_string`/`access_key` token is **only** a finding if it resolves to a **literal** value. If it's `data.azurerm_key_vault_secret...`, a variable, or a KV reference, it's adherence — note it as a strength.
- A single region is **only** a SPOF if the workload's criticality demands more — a sandbox in one region is fine.
- A large `locals.tf` is **only** a smell if it encodes branching/env logic that a module + tfvars would express more safely — size alone isn't the finding.

## Canonical finding shape

Every finding (from inline scan or a subagent) uses this shape so they merge cleanly:

```
{
  "id": "SEC-007",                  // DIM-### where DIM ∈ {REL,SEC,COST,OPS,PERF,STRUCT,ARCH}
  "dimension": "security",
  "title": "Cosmos account allows public network access",
  "file": "Cosmos.DB/Sagas/Cosmos.tf",
  "line": 42,
  "evidence": "public_network_access_enabled = true",
  "stack": "Cosmos.DB/Sagas",
  "criticality_tier": 1,            // from intent-inference
  "severity_raw": "high",           // before intent weighting
  "principle_refs": [7, 12],        // PrePass principles implicated, if any
  "waf_pillar": "Security",
  "recommendation": "Disable public access; add a private endpoint + VNet integration.",
  "effort": "M",                    // S/M/L
  "accepted_tradeoff": false,       // true ⇒ pragmatism guard fired; report as note, not gap
  "source": ["CIS-Azure-3.1", "Rahman2019-SS"],  // optional — Tier-1 control + Tier-2 study (see references/evidence-base.md)
  "confidence": "verified"          // verified | partial | self_reported (see scale below)
}
```

## Confidence scale (required on every finding)

Signals how the finding was corroborated, so the reader can weight it. Maps from source-tier + tool evidence:

| Level | When |
|-------|------|
| `verified` | Tier-1 control **and** a Tier-2 study (or live-state cross-check) **and** tool corroboration — or the gap is directly visible in `path:line` and tool-confirmed. |
| `partial` | A single corroborating leg — e.g. a Tier-1 control with a `path:line` read but no scanner/state confirmation. |
| `self_reported` | Semantic read only — no Tier-1 control mapped, no scanner/state confirmation (e.g. a principle-alignment judgment). |

A `verified` finding at lower severity may rank above a `self_reported` one at higher severity when the reader is triaging — surface confidence next to severity in the report.

Subagents return an array of these. The parent dedupes by `(file, line, title)` and re-scores with intent weight per `references/scoring.md`.
