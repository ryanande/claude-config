# Cost — price the deployed inventory, not the sampled code

> **Hard lesson (why this file exists).** An early run priced the Terraform stacks the scan happened to sample — 9 of the estate's 111 VMs, a single environment — and reported ~$1.8K/mo. The real estate was **~$45–90K/mo** — off by ~30–50×. Cost must be derived from **what is actually deployed, across all subscriptions and environments**, never from the HCL the scan read.

## Method — in order of authority

### 1. Authoritative: Azure Cost Management (the actual bill)
If the operator has **Cost Management Reader / Billing Reader**, this is the number to report:
- Per subscription, `az rest --method post --url ".../providers/Microsoft.CostManagement/query?api-version=2023-11-01"` with body `{"type":"ActualCost","timeframe":"TheLastMonth","dataset":{"granularity":"None","aggregation":{"totalCost":{"name":"PreTaxCost","function":"Sum"}},"grouping":[{"type":"Dimension","name":"ServiceName"}]}}` — total + by service.
- Or `az consumption usage list` (built-in Consumption API — **different RBAC**, may work where Cost Management is denied).
- If both are `AccessDenied`, **say so and record it as a finding**: no architect-level cost/FinOps visibility.

### 2. Fallback: inventory-priced estimate (when actuals are blocked)
Price the **real deployed inventory**, not the code:
1. Enumerate across **all** accessible subscriptions with **Azure Resource Graph** (one query spans the tenant):
   - Magnitude: `az graph query -q "Resources | summarize n=count() by type | order by n desc" --first 80`
   - Cost-driver SKUs, e.g.:
     - VMs — `Resources | where type=='microsoft.compute/virtualmachines' | summarize n=count() by tostring(properties.hardwareProfile.vmSize)`
     - App Service Plans — `microsoft.web/serverfarms | summarize n=count() by tostring(sku.name), tostring(sku.tier)`
     - then Container Apps env, Databricks, APIM, Redis, Cosmos, SQL, storage, gateways.
2. Price each `(sku × count)` via the **public Azure Retail Prices API** (`prices.azure.com/api/retail/prices`, keyless): `monthly = retailPrice × 730` for hourly meters; exclude `Spot`/`Low Priority`; use the Linux rate as a floor and note Windows/SQL licensing adds to it.
3. **Counts come from Resource Graph (already all-environments, all-subs)** — do NOT price a single instance from one workspace and call it the total.
4. **Flag what you can't inventory-price** and give a range, not false precision: Databricks DBUs, Container Apps consumption, Log Analytics / App Insights ingestion ($/GB), Windows/SQL licensing, egress.

## Dominant cost drivers (price these first)
VM compute + disks + SQL-VM licensing → App Service Plans (dedicated tiers) → Container Apps → Databricks → APIM (Premium) → gateways (Bastion/NAT/App Gateway/VPN) → Log Analytics ingestion. **Data-tier Basic SKUs (Redis/Cosmos) are usually a rounding error** — don't anchor the cost story on them; the story is usually the legacy VM fleet + multi-env sprawl.

## Report it honestly (in §3a)
State plainly whether the figure is **actual (Cost Management)** or an **inventory-priced list-price estimate**; name the subscriptions/environments covered; list the categories that are bounded-not-priced. **Never present a sampled-code slice as the estate total.**
