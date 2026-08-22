"""Input validation helpers for interactive CLI forms.

Each function validates one kind of user input (IP address, hostname,
VLAN ID, subnet mask, interface name) and raises ValidationError with
a specific, actionable message on failure. Used by cli_builder_enhanced.py
to give the user immediate, helpful feedback instead of letting bad data
flow silently into the generated YAML.
"""

import ipaddress
import re


class ValidationError(Exception):
    """Raised when user input fails validation. Message is meant to be
    shown directly to the user."""
    pass


def validate_ip(value: str) -> str:
    """Validate an IPv4 address string (e.g., '10.0.1.1').

    Returns the value unchanged if valid.
    """
    value = value.strip()
    try:
        ipaddress.IPv4Address(value)
        return value
    except ValueError:
        raise ValidationError(
            f"'{value}' is not a valid IPv4 address. "
            f"Expected format: X.X.X.X, e.g. 192.168.1.1"
        )


def validate_subnet_mask(value: str) -> str:
    """Validate a dotted-decimal subnet mask (e.g., '255.255.255.0').

    Checks both that it's a valid IPv4-shaped value AND that its bits
    form a contiguous mask (1s followed by 0s) - '255.0.255.0' is
    IP-shaped but not a real mask.
    """
    value = value.strip()
    try:
        addr = ipaddress.IPv4Address(value)
    except ValueError:
        raise ValidationError(
            f"'{value}' is not a valid subnet mask. "
            f"Expected dotted-decimal format, e.g. 255.255.255.0"
        )

    bits = "".join(f"{octet:08b}" for octet in addr.packed)
    if "01" in bits:
        raise ValidationError(
            f"'{value}' is not a valid subnet mask - the bits must be a "
            f"contiguous run of 1s followed by 0s (e.g. 255.255.255.0, "
            f"255.255.254.0). '{value}' has a gap in it."
        )
    return value


def validate_hostname(value: str, max_length: int = 15) -> str:
    """Validate a Cisco-style device hostname.

    Rules: starts with a letter, contains only letters/digits/hyphens,
    doesn't end with a hyphen, and fits Cisco IOS's default hostname
    length limit (15 chars).
    """
    value = value.strip()
    if not value:
        raise ValidationError("Hostname can't be empty.")

    if len(value) > max_length:
        raise ValidationError(
            f"'{value}' is {len(value)} characters - Cisco IOS hostnames "
            f"must be {max_length} characters or fewer. Try something "
            f"shorter, e.g. '{value[:max_length]}'"
        )

    if not re.match(r"^[A-Za-z][A-Za-z0-9-]*$", value):
        raise ValidationError(
            f"'{value}' isn't a valid hostname. It must start with a "
            f"letter and contain only letters, digits, and hyphens "
            f"(e.g. 'Router-1', 'HQ-SW01')."
        )

    if value.endswith("-"):
        raise ValidationError(
            f"'{value}' can't end with a hyphen. Try '{value.rstrip('-')}'"
        )

    return value


def validate_vlan_id(value) -> int:
    """Validate a VLAN ID is a real, usable Cisco VLAN number."""
    try:
        vlan_id = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValidationError(
            f"'{value}' isn't a valid VLAN ID. It must be a whole number."
        )

    if not (1 <= vlan_id <= 4094):
        raise ValidationError(
            f"VLAN ID {vlan_id} is out of range. Valid VLAN IDs are 1-4094."
        )

    if 1002 <= vlan_id <= 1005:
        raise ValidationError(
            f"VLAN ID {vlan_id} is reserved by Cisco for legacy FDDI/Token "
            f"Ring support and can't be used. Pick a different ID (e.g. 10, 20, 30)."
        )

    return vlan_id


def validate_interface_name(value: str) -> str:
    """Loosely validate an interface name looks like a real Cisco interface."""
    value = value.strip()
    if not value:
        raise ValidationError("Interface name can't be empty.")
    if not re.match(r"^[A-Za-z]+[A-Za-z0-9/.]*$", value):
        raise ValidationError(
            f"'{value}' doesn't look like a valid interface name. "
            f"Expected something like 'GigabitEthernet0/1' or 'FastEthernet0/1'."
        )
    return value


def validate_vlan_list(value: str) -> list:
    """Validate a comma-separated list of VLAN IDs, returning ints."""
    ids = [v.strip() for v in value.split(",") if v.strip()]
    if not ids:
        raise ValidationError("Enter at least one VLAN ID.")
    return [validate_vlan_id(v) for v in ids]
