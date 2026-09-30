# Models the version-pinning hygiene the estate is missing today
# (report: Operations — "no required_version anywhere").
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      # AVM current generation targets azurerm 4.x. The estate is on ~> 3.0 today;
      # the provider uplift is part of the module-adoption migration (report §S2).
      version = "~> 4.0"
    }
  }
}
