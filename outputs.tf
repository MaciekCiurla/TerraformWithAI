# Outputs for the Multiple Linux VMs deployment

output "resource_group_name" {
  description = "Name of the created resource group"
  value       = azurerm_resource_group.rg.name
}

output "resource_group_location" {
  description = "Location of the created resource group"
  value       = azurerm_resource_group.rg.location
}

output "virtual_network_name" {
  description = "Name of the created virtual network"
  value       = azurerm_virtual_network.vnet.name
}

output "virtual_network_id" {
  description = "ID of the created virtual network"
  value       = azurerm_virtual_network.vnet.id
}

output "subnet_id" {
  description = "ID of the created subnet"
  value       = azurerm_subnet.subnet.id
}

output "vm_names" {
  description = "Names of the created virtual machines"
  value       = var.deploy_vms ? azurerm_linux_virtual_machine.vm[*].name : []
}

output "vm_private_ips" {
  description = "Private IP addresses of the created virtual machines"
  value       = var.deploy_vms ? azurerm_network_interface.nic[*].ip_configuration[0].private_ip_address : []
}

output "vm_ids" {
  description = "IDs of the created virtual machines"
  value       = var.deploy_vms ? azurerm_linux_virtual_machine.vm[*].id : []
  sensitive   = true
}

output "network_security_group_name" {
  description = "Name of the network security group"
  value       = azurerm_network_security_group.nsg.name
}

output "ssh_connection_commands" {
  description = "SSH commands to connect to the VMs (if using SSH keys)"
  value = var.deploy_vms && var.ssh_public_key != null ? [
    for i, vm in azurerm_linux_virtual_machine.vm : 
    "ssh ${var.admin_username}@${azurerm_network_interface.nic[i].ip_configuration[0].private_ip_address}"
  ] : []
}

output "deployment_summary" {
  description = "Summary of the deployment"
  value = {
    resource_group = azurerm_resource_group.rg.name
    location       = azurerm_resource_group.rg.location
    vm_count       = var.deploy_vms ? var.vm_count : 0
    vm_size        = var.vm_size
    authentication = var.ssh_public_key != null ? "SSH Key" : "Password"
    tags           = var.tags
  }
}
