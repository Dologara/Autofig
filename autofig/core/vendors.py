"""Vendor registry and device type definitions.

Single source of truth for supported vendors and their device types.
Easy to extend for Phase 4 (multi-vendor support).
"""

from typing import Dict, List

# Vendor registry: maps vendor name to metadata and supported device types
VENDOR_REGISTRY: Dict[str, Dict] = {
    "Cisco": {
        "name": "Cisco Systems",
        "display_name": "Cisco IOS",
        "os_type": "ios",
        "device_types": ["router", "switch", "multilayer_switch"],
        "template_format": "ios_cli",
        "description": "Cisco IOS command-line interface",
    },
    # Easy to add later (Phase 4):
    # "Juniper": {
    #     "name": "Juniper Networks",
    #     "display_name": "Junos",
    #     "os_type": "junos",
    #     "device_types": ["router", "switch", "firewall"],
    #     "template_format": "junos_cli",
    #     "description": "Juniper Junos CLI",
    # },
    # "Arista": {
    #     "name": "Arista Networks",
    #     "display_name": "EOS",
    #     "os_type": "eos",
    #     "device_types": ["switch", "router"],
    #     "template_format": "eos_cli",
    #     "description": "Arista EOS CLI",
    # },
}

# Device type metadata
DEVICE_TYPES: Dict[str, Dict] = {
    "router": {
        "name": "Router",
        "description": "Layer 3 routing device",
        "default_protocols": ["static", "ospf"],
    },
    "switch": {
        "name": "Layer 2 Switch",
        "description": "Layer 2 switching device (VLANs, STP)",
        "default_protocols": ["stp"],
    },
    "multilayer_switch": {
        "name": "Multilayer Switch",
        "description": "Layer 2/3 switching device (routing + VLANs)",
        "default_protocols": ["stp", "static", "ospf"],
    },
    # Future device types:
    # "firewall": {
    #     "name": "Firewall",
    #     "description": "Security appliance",
    #     "default_protocols": ["static"],
    # },
    # "load_balancer": {
    #     "name": "Load Balancer",
    #     "description": "Traffic distribution appliance",
    #     "default_protocols": ["static"],
    # },
}


def get_supported_vendors() -> List[str]:
    """Get list of supported vendor names.
    
    Returns:
        List of vendor names (e.g., ['Cisco', 'Juniper'])
    """
    return list(VENDOR_REGISTRY.keys())


def get_supported_device_types(vendor: str) -> List[str]:
    """Get device types supported by a vendor.
    
    Args:
        vendor: Vendor name (e.g., 'Cisco')
    
    Returns:
        List of device types, or empty list if vendor not found
    """
    if vendor in VENDOR_REGISTRY:
        return VENDOR_REGISTRY[vendor]["device_types"]
    return []


def is_vendor_supported(vendor: str) -> bool:
    """Check if a vendor is supported.
    
    Args:
        vendor: Vendor name
    
    Returns:
        True if supported, False otherwise
    """
    return vendor in VENDOR_REGISTRY


def is_device_type_supported(vendor: str, device_type: str) -> bool:
    """Check if a device type is supported for a vendor.
    
    Args:
        vendor: Vendor name
        device_type: Device type (e.g., 'router')
    
    Returns:
        True if supported, False otherwise
    """
    if vendor not in VENDOR_REGISTRY:
        return False
    return device_type in VENDOR_REGISTRY[vendor]["device_types"]
