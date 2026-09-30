# Intent inference — classifying stacks by environment + criticality

Static analysis is blind without intent. The same finding is trivial in a sandbox and critical in a production payment gateway. This step assigns every stack an `{environment, criticality}` pair that drives the **intent weight** in scoring (`references/scoring.md`).

## Signals to read (in priority order)

1. **Backend resource group / storage account** (`backend.tf`) — the strongest signal. Suffixes like `-rg-prd`, `-prod`, `saprd` ⇒ production. `-int`, `-dev`, `-stg`, `sandbox` ⇒ lower environments. A backend pointing at a shared `PrePassInfrastructure-rg-prd` means changes here touch production state.
2. **`terraform.workspace` + environment lookup maps** (`locals.tf`) — many stacks here select config by `terraform.workspace` against a `generate_environment_values` map. Enumerate the workspace keys (e.g. `Integration`, `Production`) to know which environments a single stack provisions, and infer that prod keys raise the bar.
3. **Directory + resource naming** — `production-*`, `*-prd`, `payment`, `pmt`, `identity`, `sts`, `dmz` signal both environment and sensitivity. DMZ/STS/payment/identity ⇒ elevated criticality regardless of environment.
4. **Tags** — `Environment`, `Project`, `Description` tags (when present) confirm or contradict the naming. A mismatch (prod backend, `dev` tag) is itself a finding.
5. **Data classification hints** — Cosmos/SQL/Key Vault stacks tied to identity, payments, PII, or compliance domains get elevated criticality and stricter SOC2/ISO/CIS bars.

## Criticality tiers

| Tier | Examples | Severity bar |
|------|----------|--------------|
| **Tier 1 — Critical** | production payment, identity/STS, DMZ-facing, anything with regulated data | Strictest. CIS + SOC2 + ISO controls are pass/fail. A missing private endpoint or public exposure is High/Critical. |
| **Tier 2 — Standard prod** | other production services | Standard prod bar. WAF pillars expected; deviations are Medium+ unless justified. |
| **Tier 3 — Lower env** | int/dev/stg/sandbox stacks | Relaxed. Security gaps that would be Critical in prod are Low/Medium here — but secret hygiene and "lower env mirrors prod" still matter. |

## Output of this step

A table the scan and scoring steps consume:

```
stack (dir) | environment(s) | criticality tier | evidence (backend RG / tag / name) | notes
```

Record contradictions (e.g. a Tier-1 name with no diagnostic settings) as candidate findings immediately — intent mismatches are some of the highest-signal gaps.
