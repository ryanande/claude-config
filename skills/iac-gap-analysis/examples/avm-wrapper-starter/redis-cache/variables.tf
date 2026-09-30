variable "name" {
  description = "Redis cache name (e.g. PrePassIdentity-Redis-Cache-prd). One value per environment — parameterize from the caller, never copy-paste a block."
  type        = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "criticality" {
  description = "Drives the secure-by-default SKU + resilience profile. tier1=prod Tier-1 (Premium, zone-redundant, private); tier2=standard prod; tier3=non-prod only."
  type        = string
  validation {
    condition     = contains(["tier1", "tier2", "tier3"], var.criticality)
    error_message = "criticality must be one of: tier1, tier2, tier3."
  }
}

variable "environment" {
  description = "int | tst | npr | prd — used for tagging, not for resource sizing (sizing comes from criticality)."
  type        = string
}

variable "capacity" {
  description = "Optional cache size override (Basic/Standard: 0-6 'C' sizes; Premium: 1-5 'P' sizes). Null = the tier default."
  type        = number
  default     = null
}

variable "allow_public_network" {
  description = "Org default is PRIVATE. Only set true with a documented exception; Tier-1 may never be public (enforced below)."
  type        = bool
  default     = false
}

variable "private_endpoint" {
  description = "Private endpoint wiring. Required for tier1 (enforced). Null = no PE (acceptable for tier3 / behind-firewall tier2)."
  type = object({
    subnet_resource_id            = string
    private_dns_zone_resource_ids = optional(set(string), [])
  })
  default = null
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace resource ID for diagnostic settings. Null = no diagnostics wired (flagged: violates 'Observable by Design')."
  type        = string
  default     = null
}

variable "owner" {
  type    = string
  default = "platform-team"
}

variable "cost_center" {
  type = string
}

variable "data_classification" {
  description = "public | internal | confidential | restricted (e.g. identity/payment = restricted)."
  type        = string
  default     = "internal"
}

variable "extra_tags" {
  type    = map(string)
  default = {}
}

variable "enable_telemetry" {
  description = "AVM module telemetry (anonymous module-usage signal to Microsoft). Set false to disable."
  type        = bool
  default     = true
}
