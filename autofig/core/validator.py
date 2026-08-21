"""Validate topology structure and device configurations.

Enhanced with:
- Type hints
- Logging
- Custom exceptions
"""

from typing import Dict, List
from .logging_setup import get_logger
from .exceptions import TopologyValidationError, DeviceValidationError
from .vendors import is_vendor_supported, is_device_type_supported

logger = get_logger(__name__)


def validate_device(device: Dict) -> bool:
    """Validate a single device config has required fields.
    
    Args:
        device: Dict with device config
    
    Returns:
        True if valid
    
    Raises:
        DeviceValidationError: If required fields missing
    """
    required = ["name", "type", "vendor", "hostname"]
    missing = [field for field in required if field not in device]
    
    device_name = device.get("name", "Unknown")
    
    if missing:
        logger.error(f"Device '{device_name}' missing required fields: {missing}")
        raise DeviceValidationError(
            f"Device '{device_name}' missing: {', '.join(missing)}"
        )
    
    # Validate vendor is supported
    vendor = device.get("vendor", "")
    if not is_vendor_supported(vendor):
        logger.error(f"Device '{device_name}' has unsupported vendor: {vendor}")
        raise DeviceValidationError(f"Unsupported vendor: {vendor}")
    
    # Validate device type is supported for vendor
    device_type = device.get("type", "")
    if not is_device_type_supported(vendor, device_type):
        logger.error(f"Device '{device_name}' has unsupported type '{device_type}' for vendor '{vendor}'")
        raise DeviceValidationError(f"Unsupported device type '{device_type}' for vendor '{vendor}'")
    
    logger.debug(f"Device '{device_name}' validation passed")
    return True


def validate_topology(topology: Dict) -> bool:
    """Validate entire topology structure.
    
    Args:
        topology: Dict with 'devices' key
    
    Returns:
        True if valid
    
    Raises:
        TopologyValidationError: If structure invalid
    """
    logger.info("Validating topology structure")
    
    if not isinstance(topology, dict):
        logger.error(f"Topology must be a dict, got {type(topology)}")
        raise TopologyValidationError("Topology must be a dict")
    
    if "devices" not in topology:
        logger.error("Topology missing 'devices' key")
        raise TopologyValidationError("Topology must have 'devices' key")
    
    devices = topology["devices"]
    if not isinstance(devices, list):
        logger.error(f"'devices' must be a list, got {type(devices)}")
        raise TopologyValidationError("'devices' must be a list")
    
    if not devices:
        logger.error("'devices' list is empty")
        raise TopologyValidationError("'devices' list cannot be empty")
    
    logger.info(f"Validating {len(devices)} devices")
    
    # Validate each device
    for i, device in enumerate(devices):
        try:
            validate_device(device)
        except DeviceValidationError as e:
            logger.error(f"Device {i} validation failed: {e}")
            raise
    
    logger.info("Topology validation passed")
    return True


def validate_field(value, field_type: str, field_name: str) -> bool:
    """Validate a single field type.
    
    Args:
        value: The value to check
        field_type: Expected type ('int', 'str', 'list', 'dict')
        field_name: Field name (for error messages)
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If type mismatch
    """
    type_map = {
        'int': int,
        'str': str,
        'list': list,
        'dict': dict,
    }
    
    if field_type not in type_map:
        logger.error(f"Unknown field type: {field_type}")
        raise ValueError(f"Unknown field type: {field_type}")
    
    if not isinstance(value, type_map[field_type]):
        logger.error(f"Field '{field_name}' must be {field_type}, got {type(value).__name__}")
        raise ValueError(
            f"Field '{field_name}' must be {field_type}, got {type(value).__name__}"
        )
    
    logger.debug(f"Field '{field_name}' validation passed ({field_type})")
    return True
