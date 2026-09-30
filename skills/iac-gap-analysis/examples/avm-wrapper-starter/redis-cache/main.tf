locals {
  # criticality → secure-by-default SKU + resilience profile.
  # This is where "Basic everywhere" becomes "right-sized by tier" for the whole estate at once.
  tier_profile = {
    tier1 = { sku_name = "Premium", capacity = 1, zones = ["1", "2", "3"] } # zone-redundant, has an SLA
    tier2 = { sku_name = "Standard", capacity = 1, zones = null }
    tier3 = { sku_name = "Basic", capacity = 0, zones = null } # non-prod only; no SLA
  }
  sel = local.tier_profile[var.criticality]

  # Static org tag schema — NO timestamp(). Closes the perpetual-diff finding
  # (report: Operations — "timestamp() in tags across 130 files").
  tags = merge({
    environment         = var.environment
    criticality         = var.criticality
    owner               = var.owner
    cost-center         = var.cost_center
    data-classification = var.data_classification
    managed-by          = "avm-wrapper/redis-cache"
  }, var.extra_tags)
}

module "redis" {
  source = "Azure/avm-res-cache-redis/azurerm"
  # TODO: pin to a tested release and verify input names against it
  # (registry.terraform.io/modules/Azure/avm-res-cache-redis/azurerm or terraform-mcp-server).
  version = ">= 0.4.0, < 1.0.0"

  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name

  # resilience comes from the tier, not from a hand-edited block
  sku_name = local.sel.sku_name
  capacity = coalesce(var.capacity, local.sel.capacity)
  zones    = local.sel.zones

  # --- org security defaults (close the estate's security findings by construction) ---
  minimum_tls_version           = "1.2"
  enable_non_ssl_port           = false
  public_network_access_enabled = var.allow_public_network
  managed_identities            = { system_assigned = true }

  # observability by default → Log Analytics (closes the zero-diagnostics finding)
  diagnostic_settings = var.log_analytics_workspace_id == null ? {} : {
    to_law = {
      name                  = "diag-to-law"
      workspace_resource_id = var.log_analytics_workspace_id
      metric_categories     = ["AllMetrics"]
    }
  }

  # private endpoint (org default posture for data tiers; required for tier1 below)
  private_endpoints = var.private_endpoint == null ? {} : {
    primary = {
      subnet_resource_id            = var.private_endpoint.subnet_resource_id
      private_dns_zone_resource_ids = var.private_endpoint.private_dns_zone_resource_ids
    }
  }

  tags             = local.tags
  enable_telemetry = var.enable_telemetry
}

# Belt-and-suspenders to the CI policy gate (report §S3): a Tier-1 cache must be
# private and have a private endpoint. Fails plan if violated.
check "tier1_must_be_private" {
  assert {
    condition     = var.criticality != "tier1" || (var.allow_public_network == false && var.private_endpoint != null)
    error_message = "Tier-1 Redis must be private (allow_public_network = false) AND have a private_endpoint."
  }
}
