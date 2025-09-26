terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.1"
    }
  }
  backend "azurerm" {
  resource_group_name   = "MC"
  storage_account_name  = "mctf"
  container_name        = "tfstate"
  key                   = "terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}
