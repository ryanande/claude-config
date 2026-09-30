# Pass through the AVM module's outputs. Verify exact output names against the
# pinned module version (AVM standardizes on `resource_id`, `name`, and a `resource` object).
output "resource_id" {
  description = "The Redis cache resource ID."
  value       = try(module.redis.resource_id, null)
}

output "name" {
  description = "The Redis cache name."
  value       = var.name
}

output "hostname" {
  description = "The Redis cache hostname, where exposed by the module."
  value       = try(module.redis.resource.hostname, null)
}

output "applied_profile" {
  description = "The tier-derived SKU/zone profile actually applied (for verification in plan output)."
  value       = local.sel
}
