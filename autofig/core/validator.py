"""Validate topology structure and device configurations."""


def validate_device(device):
    """Validate a single device config has required fields.
    
    Args:
        device: Dict with device config
    
    Raises:
        ValueError: If required fields missing
    
    Returns:
        True if valid
    """
    required = ["name", "type", "vendor", "hostname"]
    missing = [field for field in required if field not in device]
    
    if missing:
        raise ValueError(
            f"Device '{device.get('name', 'Unknown')}' missing: {', '.join(missing)}"
        )
    
    return True


def validate_topology(topology):
    """Validate entire topology structure.
    
    Args:
        topology: Dict with 'devices' key
    
    Raises:
        ValueError: If structure invalid
    
    Returns:
        True if valid
    """
    if not isinstance(topology, dict):
        raise ValueError("Topology must be a dict")
    
    if "devices" not in topology:
        raise ValueError("Topology must have 'devices' key")
    
    devices = topology["devices"]
    if not isinstance(devices, list):
        raise ValueError("'devices' must be a list")
    
    if not devices:
        raise ValueError("'devices' list cannot be empty")
    
    # Validate each device
    for device in devices:
        validate_device(device)
    
    return True


def validate_field(value, field_type, field_name):
    """Validate a single field type (for future expansion).
    
    Args:
        value: The value to check
        field_type: Expected type ('int', 'str', 'list', 'dict')
        field_name: Field name (for error messages)
Raises:
        ValueError: If type mismatch
    
    Returns:
        True if valid
    """
    type_map = {
        'int': int,
        'str': str,
        'list': list,
        'dict': dict,
    }
    
    if field_type not in type_map:
        raise ValueError(f"Unknown field type: {field_type}")
    
    if not isinstance(value, type_map[field_type]):
        raise ValueError(
            f"Field '{field_name}' must be {field_type}, got {type(value).__name__}"
        )
    
    return True
