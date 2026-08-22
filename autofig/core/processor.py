"""Process and merge topology configuration hierarchies.

Handles the merge order for defaults:
1. Device-type defaults (base layer)
2. Topology-level defaults (override device-type)
3. Device-specific config (highest precedence)
"""

from typing import Dict, Callable
import logging

from .vendors import _find_registry_key

logger = logging.getLogger(__name__)


def merge_dicts(base: Dict, override: Dict) -> Dict:
    """Recursively merge two dicts; override takes precedence.
    
    Args:
        base: Base configuration dict
        override: Dict with overrides (takes precedence)
    
    Returns:
        Merged dict with override values taking precedence
    """
    if not isinstance(base, dict):
        logger.debug(f"Base is not dict ({type(base)}), returning override")
        return override
    
    result = base.copy()
    for key, value in override.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            # Recursive merge for nested dicts
            logger.debug(f"Recursively merging nested dict for key '{key}'")
            result[key] = merge_dicts(result[key], value)
        else:
            # Override takes precedence
            logger.debug(f"Overriding key '{key}'")
            result[key] = value
    
    return result


def process_topology(topology: Dict, device_defaults_map: Dict) -> Dict:
    """Prepare topology for rendering: merge defaults, validate structure.
    
    Merge order (lowest to highest precedence):
    1. Device-type defaults (base layer - from device_defaults_map)
    2. Topology-level defaults (from topology['defaults'])
    3. Device-specific config (highest precedence)
    
    Args:
        topology: Topology dict from YAML
        device_defaults_map: Dict of {vendor: {device_type: defaults_dict}}
                            Example: {'Cisco': {'router': {...}}}
    
    Returns:
        Processed topology with merged configs
    """
    logger.info(f"Processing topology with {len(topology.get('devices', []))} devices")
    
    processed = topology.copy()
    processed_devices = []
    
    for device in topology.get("devices", []):
        device_name = device.get("name", "Unknown")
        logger.debug(f"Processing device: {device_name}")
        
        # Start with device-type defaults (base layer)
        merged = {}
        vendor = device.get("vendor", "")
        device_type = device.get("type", "")
        
        # Find the correct vendor key (case-insensitive)
        if vendor:
            registry_vendor = _find_registry_key(vendor)
            if registry_vendor and registry_vendor in device_defaults_map:
                if device_type in device_defaults_map[registry_vendor]:
                    defaults = device_defaults_map[registry_vendor][device_type].get("defaults", {})
                    logger.debug(f"Starting with device-type defaults for {registry_vendor}/{device_type}")
                    merged = defaults.copy()
        
        # Merge topology-level defaults (override device-type defaults)
        topology_defaults = topology.get("defaults", {})
        if topology_defaults:
            logger.debug(f"Merging topology-level defaults")
            merged = merge_dicts(merged, topology_defaults)
        
        # Merge device-specific config (overrides everything)
        logger.debug(f"Merging device-specific config for {device_name}")
        merged = merge_dicts(merged, device)
        
        processed_devices.append(merged)
    
    processed["devices"] = processed_devices
    return processed


def build_device_defaults_map(loader_func: Callable) -> Dict:
    """Build a map of device-type defaults for all vendors.
    
    Calls loader_func(vendor, device_type) for each vendor/type combo.
    
    Args:
        loader_func: Function that loads defaults: load_device_defaults(vendor, device_type)
    
    Returns:
        Dict: {vendor: {device_type: {defaults_dict}}}
    """
    from .vendors import get_supported_vendors, get_supported_device_types
    
    defaults_map = {}
    
    for vendor in get_supported_vendors():
        defaults_map[vendor] = {}
        for device_type in get_supported_device_types(vendor):
            try:
                defaults = loader_func(vendor, device_type)
                defaults_map[vendor][device_type] = {"defaults": defaults}
                logger.debug(f"Loaded defaults for {vendor}/{device_type}")
            except Exception as e:
                logger.warning(f"Failed to load defaults for {vendor}/{device_type}: {e}")
                defaults_map[vendor][device_type] = {"defaults": {}}
    
    return defaults_map
