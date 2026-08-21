"""Process and merge topology configurations.

Enhanced with:
- Type hints
- Logging
"""

from typing import Dict, Callable
from .logging_setup import get_logger

logger = get_logger(__name__)


def merge_dicts(base: Dict, override: Dict) -> Dict:
    """Recursively merge override dict into base dict.
    
    Args:
        base: Base dict (won't be modified)
        override: Dict to merge in (takes precedence)
    
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
    1. Global defaults (from topology['defaults'])
    2. Vendor+device type defaults (from device_defaults_map)
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
        
        # Start with global defaults
        merged = topology.get("defaults", {}).copy()
        logger.debug(f"Started with global defaults")
        
        # Merge vendor + device type defaults
        vendor = device.get("vendor", "")
        device_type = device.get("type", "")
        
        if vendor in device_defaults_map:
            if device_type in device_defaults_map[vendor]:
                defaults = device_defaults_map[vendor][device_type].get("defaults", {})
                logger.debug(f"Merging defaults for {vendor}/{device_type}")
                merged = merge_dicts(merged, defaults)
        
        # Merge device-specific config (overrides everything)
        logger.debug(f"Merging device-specific config for {device_name}")
        merged = merge_dicts(merged, device)
        
        processed_devices.append(merged)
        logger.debug(f"Device {device_name} processing complete")
    
    processed["devices"] = processed_devices
    logger.info(f"Topology processing complete: {len(processed_devices)} devices")
    return processed


def build_device_defaults_map(loader_func: Callable) -> Dict:
    """Build a map of vendor→type→defaults for efficient lookups.
    
    Args:
        loader_func: Function to load device defaults (e.g., load_device_defaults)
    
    Returns:
        Dict structure: {vendor: {device_type: defaults_dict}}
    
    Example:
        {'Cisco': {'router': {...}, 'switch': {...}}}
    """
    logger.info("Building device defaults map")
    
    # For now, only Cisco. Expand later with more vendors/types.
    vendors = ["Cisco"]
    device_types = ["router", "switch", "multilayer_switch"]
    
    defaults_map = {}
    
    for vendor in vendors:
        logger.debug(f"Loading defaults for vendor: {vendor}")
        defaults_map[vendor] = {}
        
        for dev_type in device_types:
            try:
                defaults = loader_func(vendor, dev_type)
                if defaults:
                    defaults_map[vendor][dev_type] = defaults
                    logger.debug(f"Loaded defaults for {vendor}/{dev_type}")
            except Exception as e:
                # Skip if device type doesn't exist for this vendor
                logger.warning(f"Could not load defaults for {vendor}/{dev_type}: {e}")
                pass
    
    logger.info(f"Device defaults map built with {len(defaults_map)} vendors")
    return defaults_map
