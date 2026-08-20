"""Load and parse YAML topology files and device defaults."""

import yaml
from pathlib import Path

# Paths are relative to this package
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PACKAGE_ROOT / "data"
TOPOLOGY_DIR = DATA_DIR / "topologies"
DEVICE_DIR = DATA_DIR / "devices"


def load_yaml(path):
    """Load a YAML file and return dict. Can accept Path or str.
    
    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML is malformed
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Topology file not found: {path}")
    
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    
    if not isinstance(data, dict):
        raise ValueError(f"YAML must parse to dict, got {type(data)}")
    
    return data


def load_device_defaults(vendor, device_type):
    """Load device-specific defaults (e.g., router_cisco.yaml).
    
    Args:
        vendor: Device vendor (e.g., 'Cisco')
        device_type: Device type (e.g., 'router')
    
    Returns:
        Dict of defaults, or empty dict if not found
    """
    defaults_file = DEVICE_DIR / f"{device_type.lower()}_{vendor.lower()}.yaml"
    if defaults_file.exists():
        return load_yaml(defaults_file)
    return {}


def list_available_topologies():
    """Return list of available topology files (Path objects).
    
    Pure function, no side effects.
    """
    return sorted(TOPOLOGY_DIR.glob("*.yaml"))
