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
        "description": "Layer 3-capable switch (routing + VLANs)",
        "default_protocols": ["stp", "ospf"],
    },
}


def _find_registry_key(vendor: str) -> str:
    """Find vendor key in registry (case-insensitive).
    
    Args:
        vendor: Vendor name (any case)
    
    Returns:
        Actual key from VENDOR_REGISTRY, or None if not found
    """
    if not vendor:
        return None
    
    vendor_lower = vendor.lower()
    for key in VENDOR_REGISTRY:
        if key.lower() == vendor_lower:
            return key
    
    return None


def get_supported_vendors() -> List[str]:
    """Get list of supported vendors.
    
    Returns:
        List of vendor names as they appear in registry
    """
    return list(VENDOR_REGISTRY.keys())


def is_vendor_supported(vendor: str) -> bool:
    """Check if a vendor is supported.
    
    Args:
        vendor: Vendor name (case-insensitive)
    
    Returns:
        True if supported, False otherwise
    """
    return _find_registry_key(vendor) is not None


def is_device_type_supported(vendor: str, device_type: str) -> bool:
    """Check if a device type is supported for a vendor.
    
    Args:
        vendor: Vendor name (case-insensitive)
        device_type: Device type name
    
    Returns:
        True if supported, False otherwise
    """
    registry_vendor = _find_registry_key(vendor)
    if not registry_vendor:
        return False
    
    supported_types = VENDOR_REGISTRY[registry_vendor].get("device_types", [])
    return device_type in supported_types


def get_supported_device_types(vendor: str) -> List[str]:
    """Get supported device types for a vendor.
    
    Args:
        vendor: Vendor name (case-insensitive)
    
    Returns:
        List of device types, or empty list if vendor not found
    """
    registry_vendor = _find_registry_key(vendor)
    if not registry_vendor:
        return []
    
    return VENDOR_REGISTRY[registry_vendor].get("device_types", [])
