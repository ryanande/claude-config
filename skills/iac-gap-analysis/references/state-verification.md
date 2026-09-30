# State verification — code vs live reality (optional, auto-detect)

Static code analysis is blind to what's actually running. This dimension cross-references the repo against live cloud state to find the three reality gaps:

1. **Cloud-but-not-code** — resources that exist in Azure (or in state) but have no Terraform declaration. Shadow infra, click-ops, drift.
2. **Code≠live** — a parameter in `.tf` that doesn't match the live/state value (someone changed it in the portal).
3. **Orphaned state** — state entries for resources that are gone or no longer referenced.

The state for this estate lives in a **remote `azurerm` backend** (Azure Storage, e.g. `ppinfrastructuresaprd` in `PrePassInfrastructure-rg-prd`) — there are no local `.tfstate` files to read. So this dimension requires cloud auth and is **off unless auth is present**.

## Resolving `state_check`

| Value | Behavior |
|-------|----------|
| `off` | Skip entirely. Report records drift detection as **not performed**. |
| `on` | Require auth; if absent, warn and fall back to code-only for this dimension. |
| `auto` (default) | Run the detection below; turn `on` only if it passes. |

### Detection

```bash
az account show >/dev/null 2>&1 && echo "AZ_AUTH_OK" || echo "AZ_AUTH_MISSING"
command -v terraform >/dev/null 2>&1 && echo "TF_OK" || echo "TF_MISSING"
```

`auto` → `on` only when both `AZ_AUTH_OK` and `TF_OK`. Otherwise → `off`, and say so.

## Procedure when `on` (read-only)

For each in-scope stack with a `backend.tf`:

1. **Read remote state, don't mutate it.**
   - `terraform -chdir=<stack> init` (real backend — read access only) then `terraform -chdir=<stack> state list` to enumerate managed resources.
   - **Never** run `apply`/`destroy`/`import`/`state rm`.
2. **Drift via plan (read-only).** `terraform -chdir=<stack> plan -refresh-only -lock=false` surfaces code≠live deltas without proposing changes. Capture the diff per resource → **Code≠live** findings.
3. **Cloud-but-not-code.** Enumerate live resources in the stack's resource group(s) with `az resource list -g <rg> -o json` and diff against `state list` + the declared resources. Anything live but unmanaged → **Cloud-but-not-code** finding (intent-weighted: an unmanaged resource in a Tier-1 prod RG is High+).
4. **Orphaned state.** Entries in `state list` with no corresponding declaration or live resource → **Orphaned state** finding.

## Output

A drift sub-section in the report:

```
stack | finding type | resource | code value | live/state value | severity | recommendation
```

If auth is partial (e.g. some RGs inaccessible), list which stacks were verified and which were skipped. **Declared partial coverage beats implied full coverage.**
