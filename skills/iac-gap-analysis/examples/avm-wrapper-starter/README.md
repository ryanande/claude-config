# AVM-wrapper starter — the "paved-road module" pattern

> Draft deliverable from the IaC gap analysis (§S2 "module layer first — adopt, don't build"). This is a **seed**, not a finished module library. It should graduate into a dedicated, versioned **`tf-modules`** repo (semver-tagged), per the operating model — it lives here only as a worked example alongside the report.

## What this is

A **thin org-defaults wrapper** around an **Azure Verified Module** (AVM). The team does **not** author or maintain the resource logic — Microsoft does, in the AVM. The wrapper adds only:

1. A **`criticality` tier** input (`tier1`/`tier2`/`tier3`) that maps to secure, resilient SKU/zone defaults.
2. **Org security defaults** baked in: TLS 1.2 floor, non-SSL port off, public network access **off by default**, system-assigned identity.
3. **Observability by default**: diagnostic settings wired to Log Analytics.
4. A **static org tag schema** (no `timestamp()` — kills the perpetual-diff finding).
5. A `check` block enforcing Tier-1 hardening (private + no public access) as a belt-and-suspenders to the CI policy gate.

## Why this is the keystone (maps to the report)

A single ~80-line wrapper closes, **by construction**, findings that today exist in 129 hand-copied places:

| Report finding | Closed by |
|---|---|
| Reliability — all Redis Basic C0, no zone-redundancy | `tier1` → Premium + `zones` |
| Security — data tiers public, no private endpoints | `public_network_access_enabled = false` default + `private_endpoints` |
| Operations — zero diagnostic settings | `diagnostic_settings` → Log Analytics default |
| Operations — `timestamp()` perpetual-diff tags | static `local.tags` |
| Operations — no version pinning | `versions.tf` pins `required_version` + provider |
| Structural — 0 modules / copy-paste | this *is* the module; consumers call it, don't clone |
| Live-drift — Identity `-tst`/`-prd` copy-paste defect | one module call per env, parameterized — no block to mis-copy |

## Layout

```
avm-wrapper-starter/
├── README.md                  ← this file
└── redis-cache/               ← the wrapper module (one resource type)
    ├── versions.tf
    ├── variables.tf
    ├── main.tf
    ├── outputs.tf
    └── examples/
        └── identity-tier1.tf  ← the Identity Tier-1 Redis, done right
```

Redis is the first wrapper because it's the highest-leverage given the findings (8× Basic C0, the Identity defect, no diagnostics, public access). The **same pattern** then repeats for `service-bus` (with DLQ defaults), `function-app`, `cosmos`, `storage`, `front-door-domain`, `vm` — each wrapping its AVM module (`Azure/avm-res-*/azurerm`).

## Before using

- **Pin the AVM module version** in `main.tf` (`version = "..."`) to a tested release and **verify the input names against that version** — AVM modules evolve. Confirm via `registry.terraform.io/modules/Azure/avm-res-cache-redis/azurerm` or `hashicorp/terraform-mcp-server`.
- Adopting AVM entails the **azurerm 4.x** provider uplift (the estate is on `~> 3.0` today) — that uplift is itself part of the modernization track.
- Run it behind the CI policy gates from §S3 (checkov / OPA / gitleaks).
