"""Load and parse YAML topology files and device defaults.

Enhanced with:
- Type hints (for FastAPI in Phase 2)
- Logging (for debugging)
"""

import yaml
from pathlib import Path
from typing import Dict, List
from .logging_setup import get_logger
from .config import TOPOLOGY_DIR, DEVICE_DEFAULTS_DIR
from .exceptions import DeviceLoadError

logger = get_logger(__name__)


def load_yaml(path: Path | str) -> Dict:
    """Load a YAML file and return dict.
    
    Args:
        path: Path to YAML file (Path object or string)
    
    Returns:
        Dictionary parsed from YAML
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If YAML is malformed or doesn't parse to dict
    """
    path = Path(path)
    logger.info(f"Loading YAML from {path}")
    
    if not path.exists():
        logger.error(f"YAML file not found: {path}")
        raise FileNotFoundError(f"Topology file not found: {path}")
    
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML {path}: {e}")
        raise ValueError(f"Malformed YAML in {path}: {e}")
    
    if not isinstance(data, dict):
        logger.error(f"YAML must parse to dict, got {type(data)}")
        raise ValueError(f"YAML must parse to dict, got {type(data)}")
    
    logger.debug(f"Loaded YAML with {len(data.get('devices', []))} devices")
    return data


def load_device_defaults(vendor: str, device_type: str) -> Dict:
    """Load device-specific defaults (e.g., router_cisco.yaml).
    
    Args:
        vendor: Device vendor (e.g., 'Cisco')
        device_type: Device type (e.g., 'router')
    
    Returns:
        Dict of defaults, or empty dict if not found
    
    Raises:
        DeviceLoadError: If defaults file exists but is invalid
    """
    defaults_file = DEVICE_DEFAULTS_DIR / f"{device_type.lower()}_{vendor.lower()}.yaml"
    
    logger.debug(f"Looking for device defaults: {defaults_file}")
    
    if not defaults_file.exists():
        logger.debug(f"No defaults found for {vendor}/{device_type}")
        return {}
    
    try:
        logger.info(f"Loading defaults for {vendor}/{device_type}")
        defaults = load_yaml(defaults_file)
        logger.debug(f"Loaded defaults with {len(defaults.get('defaults', {}))} config items")
        return defaults
    except Exception as e:
        logger.error(f"Failed to load defaults from {defaults_file}: {e}")
        raise DeviceLoadError(f"Failed to load device defaults for {vendor}/{device_type}: {e}")


def list_available_topologies() -> List[Path]:
    """Return list of available topology files (Path objects).
    
    Pure function, no side effects.
    
    Returns:
        Sorted list of Path objects for YAML topology files
    """
    logger.debug(f"Scanning topology directory: {TOPOLOGY_DIR}")
    topologies = sorted(TOPOLOGY_DIR.glob("*.yaml"))
    logger.info(f"Found {len(topologies)} topology files")
    return topologies
