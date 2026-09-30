# Azure checks — concrete per-resource-type rules

The dimension intent in `gap-matrix.md` becomes pass/fail here, mapped to the actual Azure resource types this repo provisions. These are the `azurerm` attributes to look for. Absence of a setting is as meaningful as a bad value. Severity is the *raw* severity; intent weight is applied later.

> Refresh against current Azure guidance when in doubt: `microsoft_docs_search` (Microsoft Learn MCP) or the Azure WAF service guides. CIS Azure Foundations Benchmark is the compliance backbone for the `security` dimension.

## Cross-cutting (every stack)

| Check | Good | Gap (raw severity) |
|-------|------|--------------------|
| Diagnostic settings | `azurerm_monitor_diagnostic_setting` → Log Analytics on each resource | Missing (Medium; High for Tier-1) |
| Managed identity | `identity { type = "SystemAssigned" }` + RBAC | Connection strings / access keys in app settings (High) |
| Min TLS | `min_tls_version = "1.2"`+ | Unset or < 1.2 (High) |
| Version pinning | `required_version` + pinned `required_providers` | Unpinned (Medium — repeatability risk) |
| Tags | Stable ownership/env/cost tags | Missing, or `timestamp()` in tags = perpetual diff (Medium) |
| Public exposure | `public_network_access_enabled = false` + private endpoint | `true` on a data/internal tier (High/Critical Tier-1) |

## Front Door / WAF
- WAF policy in **Prevention** mode (not Detection) for prod; managed rule sets current; custom rules for known abuse.
- HTTPS-only + min TLS; HTTP→HTTPS redirect; health probes configured.
- Origin not directly publicly reachable (locked to Front Door via header/IP).

## Function Apps / App Services
- Plan SKU appropriate (Consumption/Premium vs idle Always-On); zone-redundant plan for prod.
- HTTPS-only; FTPS disabled; min TLS 1.2; `public_network_access` controlled.
- Managed identity to Key Vault/storage rather than keys; App Insights wired.
- VNet integration for internal-facing apps.

## Container Apps / ACE
- Min replicas > 0 for latency-critical; autoscale rules defined; not pinned to placeholder images (`mcr.microsoft.com/k8se/quickstart` left in prod = finding).
- Ingress scope (external vs internal) matches intent; managed environment zone-redundant for prod.
- Secrets via Key Vault references, not inline env values.

## Cosmos DB
- `public_network_access_enabled = false` + private endpoint for Tier-1.
- Geo-redundancy / multi-region writes per criticality; automatic failover.
- Consistent backup policy; RU/s autoscale vs fixed over-provisioning (cost).
- CMK for regulated data.

## Redis Cache
- Non-default ports / `enable_non_ssl_port = false`; TLS 1.2.
- Zone redundancy + appropriate tier (Standard/Premium) for HA; private endpoint.

## Service Bus / Event Hub
- Premium (zone-redundant) for prod-critical messaging; **dead-letter** handling and retry.
- Network rules / private endpoints; managed identity auth not SAS keys.
- Presence at all = positive signal for choreography/async (principles #4/#5).

## Key Vault
- `purge_protection_enabled = true`; soft-delete; RBAC or tight access policies.
- Network ACLs default-deny + private endpoint for Tier-1; diagnostic logging on.
- This is where secrets *should* live — references to KV secrets elsewhere are adherence.

## SQL / VM-hosted databases (Virtual.Machines/*SQL*)
- Multi-AZ / availability set / zone; backup + geo-replication; TDE.
- Legacy OS/SQL versions (e.g. SQL14, Server 2016 images) = modernization + support-risk finding (principle #9).
- Public IP on a DB VM = Critical.

## Storage Accounts
- `allow_nested_items_to_be_public = false`; `min_tls_version`; HTTPS-only.
- Redundancy SKU (LRS vs ZRS/GRS) matches criticality; legacy/over-provisioned tiers (cost).
- Network rules default-deny for Tier-1.

## Resiliency quick-scan (repo-wide)
A fast structural signal: count files containing `zone_redundant`, `zones =`, `availability_zone`, geo/failover settings. **Zero across a large prod estate is a headline Reliability finding** — quantify it.
