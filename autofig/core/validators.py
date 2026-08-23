"""Validation module for device configs, topologies, and user input fields."""

import ipaddress
import re
from typing import Dict, Any

from .vendors import is_vendor_supported, is_device_type_supported
from .exceptions import DeviceValidationError, TopologyValidationError


class ValidationError(ValueError):
    """Raised when a single form field fails validation (IP, hostname, etc).

    Subclasses ValueError so callers that only care "was this bad input"
    (e.g. validate_field's generic type checks) can catch either this or
    a plain ValueError. Structure-level validation (validate_device,
    validate_topology) raises the more specific DeviceValidationError /
    TopologyValidationError from exceptions.py instead, so callers can
    distinguish "the YAML is malformed" from "the user typed a bad IP".
    """
    pass


# ============================================================================
# STRUCTURE VALIDATORS (for YAML validation)
# ============================================================================

def validate_device(device: Dict[str, Any]) -> bool:
    """Validate a device dict has required fields and correct vendor/type.
    
    Args:
        device: Device dict to validate
    
    Returns:
        True if valid
    
    Raises:
        DeviceValidationError: If validation fails
    """
    required_fields = ["name", "type", "vendor", "hostname"]
    
    for field in required_fields:
        if field not in device:
            raise DeviceValidationError(f"Device missing required field: {field}")
    
    vendor = device.get("vendor", "")
    device_type = device.get("type", "")
    
    if not is_vendor_supported(vendor):
        raise DeviceValidationError(f"Unsupported vendor: {vendor}")
    
    if not is_device_type_supported(vendor, device_type):
        raise DeviceValidationError(f"Device type '{device_type}' not supported for vendor '{vendor}'")
    
    return True


def validate_topology(topology: Dict[str, Any]) -> bool:
    """Validate a topology has devices and each device is valid.
    
    Args:
        topology: Topology dict to validate
    
    Returns:
        True if valid
    
    Raises:
        TopologyValidationError: If the topology's own structure is invalid
        DeviceValidationError: If a device within it is invalid
    """
    if not isinstance(topology, dict):
        raise TopologyValidationError("Topology must be a dict")
    
    if "devices" not in topology:
        raise TopologyValidationError("Topology missing 'devices' key")
    
    devices = topology.get("devices", [])
    
    if not isinstance(devices, list):
        raise TopologyValidationError("'devices' must be a list")
    
    if len(devices) == 0:
        raise TopologyValidationError("Topology must have at least one device")
    
    # Validate each device (raises DeviceValidationError on failure)
    for device in devices:
        validate_device(device)
    
    return True


def validate_field(value: Any, field_type: str, field_name: str = None) -> bool:
    """Validate a single field value type.
    
    Args:
        value: Value to validate
        field_type: Expected type ('int', 'str', 'list', 'dict')
        field_name: Name of field (for error messages)
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If validation fails
    """
    type_map = {
        "int": int,
        "str": str,
        "list": list,
        "dict": dict,
    }
    
    if field_type not in type_map:
        raise ValidationError(f"Unknown field type: {field_type}")
    
    expected_type = type_map[field_type]
    
    if not isinstance(value, expected_type):
        field_info = f" ({field_name})" if field_name else ""
        raise ValidationError(
            f"Field{field_info} must be {field_type}, got {type(value).__name__}"
        )
    
    return True


# ============================================================================
# FIELD VALIDATORS (for user input validation in forms)
# ============================================================================

def validate_ip(value: str) -> str:
    """Validate an IPv4 address string (e.g., '10.0.1.1').
    
    Args:
        value: IP address string to validate
    
    Returns:
        The value unchanged if valid
    
    Raises:
        ValidationError: If not a valid IPv4 address
    """
    value = value.strip()
    try:
        ipaddress.IPv4Address(value)
        return value
    except ValueError:
        raise ValidationError(
            f"Invalid IPv4 address: {value} (expected format: 192.168.1.1)"
        )


def validate_subnet_mask(value: str) -> str:
    """Validate a dotted-decimal subnet mask (e.g., '255.255.255.0').
    
    Checks the value is a valid IPv4-shaped address AND that its bits form
    a contiguous mask (a run of 1s followed by 0s) - this covers every
    real subnet mask, not just a fixed shortlist of common /8-/32 values.
    
    Args:
        value: Subnet mask to validate
    
    Returns:
        The value unchanged if valid
    
    Raises:
        ValidationError: If not a valid subnet mask
    """
    value = value.strip()
    try:
        addr = ipaddress.IPv4Address(value)
    except ValueError:
        raise ValidationError(
            f"Invalid subnet mask: {value} (expected dotted-decimal, e.g. 255.255.255.0)"
        )

    bits = "".join(f"{octet:08b}" for octet in addr.packed)
    if "01" in bits:
        raise ValidationError(
            f"Invalid subnet mask: {value} (bits must be a contiguous run of "
            f"1s followed by 0s, e.g. 255.255.255.0, 255.255.254.0)"
        )
    return value


def validate_hostname(value: str, max_length: int = 15) -> str:
    """Validate a hostname (max 15 chars, alphanumeric + hyphens).
    
    Args:
        value: Hostname to validate
        max_length: Maximum length (Cisco limit is 15)
    
    Returns:
        The value unchanged if valid
    
    Raises:
        ValidationError: If not a valid hostname
    """
    value = value.strip()
    
    if len(value) > max_length:
        raise ValidationError(
            f"Hostname too long: {len(value)} chars (max {max_length})"
        )
    
    if not re.match(r"^[a-zA-Z0-9-]+$", value):
        raise ValidationError(
            f"Hostname '{value}' invalid (alphanumeric and hyphens only, no spaces)"
        )
    
    if value.startswith("-") or value.endswith("-"):
        raise ValidationError("Hostname cannot start or end with hyphen")
    
    return value


def validate_vlan_id(value) -> int:
    """Validate a VLAN ID (1-4094).
    
    Args:
        value: VLAN ID to validate (int or string)
    
    Returns:
        VLAN ID as int if valid
    
    Raises:
        ValidationError: If not a valid VLAN ID
    """
    try:
        vlan_id = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"VLAN must be a number, got {value}")
    
    if vlan_id < 1 or vlan_id > 4094:
        raise ValidationError(f"VLAN must be 1-4094, got {vlan_id}")
    
    return vlan_id


def validate_vlan_list(value: str) -> list:
    """Validate comma-separated VLAN IDs.
    
    Args:
        value: Comma-separated VLAN IDs (e.g., '1,10,20,30')
    
    Returns:
        List of validated VLAN IDs as integers
    
    Raises:
        ValidationError: If any VLAN ID is invalid
    """
    if isinstance(value, list):
        return value
    
    value = value.strip()
    if not value:
        raise ValidationError("VLAN list cannot be empty")
    
    try:
        vlan_ids = [int(v.strip()) for v in value.split(",")]
    except ValueError as e:
        raise ValidationError(f"Invalid VLAN ID: {e}")
    
    # Validate each VLAN
    for vlan_id in vlan_ids:
        if vlan_id < 1 or vlan_id > 4094:
            raise ValidationError(f"VLAN {vlan_id} out of range (1-4094)")
    
    return vlan_ids


def validate_interface_name(value: str) -> str:
    """Validate a Cisco interface name.
    
    Args:
        value: Interface name (e.g., 'GigabitEthernet0/0')
    
    Returns:
        The value unchanged if valid
    
    Raises:
        ValidationError: If not a valid interface name
    """
    value = value.strip()

    # Split into a letter/hyphen prefix and a numeric suffix (slot/port
    # notation), e.g. "TenGigabitEthernet1/0/1" -> ("TenGigabitEthernet", "1/0/1")
    match = re.match(r"^([A-Za-z][A-Za-z-]*)(\d[\d/.:]*)$", value)
    if not match:
        raise ValidationError(
            f"Invalid interface name: {value} "
            f"(expected e.g., GigabitEthernet0/0, TenGigabitEthernet1/0/1, FastEthernet0/1)"
        )

    prefix = match.group(1)
    # Accept any *Ethernet family (Gigabit/TenGigabit/FastEthernet/AppGigabit/...),
    # the common short forms, and the other standard interface types.
    known_families = {
        "Port-channel", "Loopback", "Vlan", "Tunnel", "Serial",
        "E", "G", "F", "Te", "Fo",
    }
    if not (prefix.endswith("Ethernet") or prefix in known_families):
        raise ValidationError(
            f"Invalid interface name: {value} "
            f"(expected e.g., GigabitEthernet0/0, TenGigabitEthernet1/0/1, FastEthernet0/1)"
        )

    return value
