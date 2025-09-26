variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
  default     = "15525204-448b-4828-998e-370e02b3d64f"
}

variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  default     = "example-resources"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US"
}

variable "deploy_vms" {
  description = "Whether to deploy VMs"
  type        = bool
  default     = true
}

variable "vm_count" {
  description = "Number of VMs to deploy"
  type        = number
  default     = 2
  
  validation {
    condition     = var.vm_count >= 1 && var.vm_count <= 10
    error_message = "VM count must be between 1 and 10."
  }
}

variable "vm_size" {
  description = "Size of the virtual machines"
  type        = string
  default     = "Standard_B1s"
}

variable "admin_username" {
  description = "Admin username for VMs"
  type        = string
  default     = "azureuser"
}

variable "admin_password" {
  description = "Admin password for VMs (use ssh_public_key instead for better security)"
  type        = string
  default     = "Tymczasowe01"
  sensitive   = true
}

variable "ssh_public_key" {
  description = "SSH public key for VM access (recommended over password)"
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Environment = "Development"
    Project     = "MultipleLinuxVMs"
    ManagedBy   = "Terraform"
  }
}
