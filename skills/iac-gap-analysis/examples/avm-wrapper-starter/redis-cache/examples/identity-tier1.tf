# Example: the Identity Tier-1 Redis cache, done right.
#
# Contrast with the live finding (report §7): the current Identity stack ships a
# Basic C0 cache, no zones, no private endpoint, no diagnostics, and a Production
# block that was copy-pasted from Test (named "-tst"). One module call per env —
# parameterized, not copy-pasted — removes the whole class of defect.
#
# In the target model this lives in the Identity service's app repo under /infra,
# deployed by that service's pipeline. Per-environment values come from the
# pipeline (tfvars / workspace), NOT from a hand-cloned block.

module "identity_redis" {
  source = "../" # → the org redis-cache wrapper (in the tf-modules registry once graduated)

  name                = "PrePassIdentity-Redis-Cache-prd" # real per-env name; no "-tst" in prod
  location            = "West US"
  resource_group_name = "PrePassInfrastructure-rg-identity"

  criticality         = "tier1" # ⇒ Premium + zone-redundant + private (enforced)
  environment         = "prd"
  cost_center         = "identity"
  data_classification = "restricted" # identity/auth data

  # Tier-1 requires private networking (the wrapper's check block enforces this):
  allow_public_network = false
  private_endpoint = {
    subnet_resource_id            = var.identity_pe_subnet_id
    private_dns_zone_resource_ids = [var.redis_private_dns_zone_id]
  }

  # observability on by default:
  log_analytics_workspace_id = var.identity_law_id
}

# (declare the referenced inputs in the consuming stack)
variable "identity_pe_subnet_id" { type = string }
variable "redis_private_dns_zone_id" { type = string }
variable "identity_law_id" { type = string }
