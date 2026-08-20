

"""Process and merge topology configurations."""


def merge_dicts(base, override):
    """Recursively merge override dict into base dict.
    
    Args:
        base: Base dict (won't be modified)
        override: Dict to merge in (takes precedence)
    
    Returns:
        Merged dict
    """
    if not isinstance(base, dict):
        return override
    
    result = base.copy()
    for key, value in override.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            # Recursive merge for nested dicts
            result[key] = merge_dicts(result[key], value)
        else:
            # Override takes precedence
            result[key] = value
    
    return result


def process_topology(topology, device_defaults_map):
    """Prepare topology for rendering: merge defaults, validate structure.
    
    Args:
        topology: Topology dict from YAML
        device_defaults_map: Dict of {vendor: {device_type: defaults_dict}}
                            Example: {'Cisco': {'router': {...}}}
    
    Returns:
        Processed topology with merged configs
    """
    processed = topology.copy()
    processed_devices = []
    
    for device in topology.get("devices", []):
        # Start with global defaults
        merged = topology.get("defaults", {}).copy()
# Merge vendor + device type defaults
        vendor = device.get("vendor", "")
        device_type = device.get("type", "")
        if vendor in device_defaults_map:
            if device_type in device_defaults_map[vendor]:
                merged = merge_dicts(
                    merged,
                    device_defaults_map[vendor][device_type].get("defaults", {})
                )
        
        # Merge device-specific config (overrides everything)
        merged = merge_dicts(merged, device)
        
        processed_devices.append(merged)
    
    processed["devices"] = processed_devices
    return processed


def build_device_defaults_map(loader_func):
    """Build a map of vendor→type→defaults for efficient lookups.
    
    Args:
        loader_func: Function to load device defaults (e.g., load_device_defaults)
    

    Returns:
        Dict structure: {vendor: {device_type: defaults_dict}}
    
    Example:
        {'Cisco': {'router': {...}, 'switch': {...}}}
    """
    # For now, only Cisco. Expand later with more vendors/types.
    vendors = ["Cisco"]
    device_types = ["router", "switch", "multilayer_switch"]
    
    defaults_map = {}
    
    for vendor in vendors:
        defaults_map[vendor] = {}
        for dev_type in device_types:
            try:
                defaults = loader_func(vendor, dev_type)
                if defaults:
                    defaults_map[vendor][dev_type] = defaults
            except Exception:
                # Skip if device type doesn't exist for this vendor
                pass
    
    return defaults_map
