# Tooling — optional scanners with auto-detect + graceful degradation

The semantic analysis is the **always-available floor**: the skill must produce a full report with zero external tools installed. Scanners, when present, add precision and let the report cite tool-confirmed findings alongside the semantic ones. Detect each; if missing, note it under "Coverage & limitations" and continue — never block on a missing binary, never silently skip.

## Detection (run once, up front)

```bash
for t in terraform tflint checkov trivy tfsec infracost az jq; do
  command -v "$t" >/dev/null 2>&1 && echo "FOUND $t" || echo "MISSING $t"
done
```

Record the FOUND/MISSING set; it goes in the report's coverage section.

## What each adds, and the safe way to run it

| Tool | Adds | Safe invocation | If missing |
|------|------|-----------------|-----------|
| `terraform validate` | Syntax/type errors, bad refs | `terraform -chdir=<stack> validate` (needs `init -backend=false`) | Semantic read for obvious ref errors |
| `terraform graph` | Dependency graph → orphan/SPOF detection | `terraform -chdir=<stack> graph` | Build dependency picture from `depends_on`/refs by reading |
| `tflint` | Provider-aware lint, deprecated args, naming | `tflint --chdir=<stack> --format=json` | Manual pattern checks |
| `checkov` | 1000+ policy checks, CIS/SOC2 mapping | `checkov -d <repo> --compact -o json` (read-only) | `azure-checks.md` semantic checks |
| `trivy` / `tfsec` | Misconfig + secret scanning | `trivy config <repo> --format json` | Semantic secret + misconfig read |
| `infracost` | Cost deltas / monthly estimate (Financial Leakage) | `infracost breakdown --path <stack> --format json` (needs a pricing API — hosted free key, or **self-hosted for zero egress**, see [`infracost-self-host.md`](infracost-self-host.md)) | SKU-tier reasoning from `azure-checks.md` |
| `az` | Live-state cross-check | see `state-verification.md` | Code-only; mark drift "not performed" |
| `az graph` (Resource Graph) | **Cost & inventory truth** — count/SKU of actually-deployed resources across ALL subs (`az graph query -q "Resources \| summarize count() by type"`), the basis for the Cost dimension | Falls back to per-sub `az resource list`; see [`cost-method.md`](cost-method.md) |
| `az costmanagement` / `az consumption usage` | **Actual spend** (the authoritative cost number) | If RBAC-denied, record "no cost visibility" as a finding and use inventory pricing |
| `terraform-mcp-server` (MCP, official HashiCorp) | **Live provider-doc grounding** — validate that an attribute/argument actually exists and its correct name/spelling for the provider version in use; discover registry/AVM modules; retrieve Sentinel policies | If the MCP is connected (ToolSearch for `terraform`/`provider`/`module` tools), use it to confirm any attribute-name-dependent finding before asserting it | Fall back to semantic reasoning, but **flag attribute-name findings as `partial` confidence** — see note below |

> **Anti-false-positive note (learned the hard way):** static greps for attribute names produce false "absent" findings when the arg has a different spelling than guessed (e.g. Redis uses `minimum_tls_version`, not `min_tls_version`). When `terraform-mcp-server` is available, **verify the canonical attribute name against live provider docs** before reporting "X is never set." When it's not, search BOTH plausible spellings and mark the finding `partial`.

## Rules of engagement

- **Read-only only.** Never `terraform apply`, `destroy`, or anything that mutates cloud or state. `init` must use `-backend=false` for offline validate; do not initialize against the real `azurerm` backend unless the user explicitly authorized state verification.
- **Triage, don't dump.** Scanner output is input to findings, not the finding itself. Convert each relevant scanner hit into the canonical finding shape (`gap-matrix.md`), deduping against semantic findings on `(file, line)`.
- **Tool says X, you verify X.** A scanner false-positive (e.g. flags a KV-referenced secret as hardcoded) must be down-graded by the semantic pass. The human-readable report reflects *your* verified judgment, with the scanner cited as corroboration.
- **No silent caps.** If you sample rather than scan every stack (standard depth), say which stacks were sampled and that patterns were confirmed repo-wide via Grep counts.
