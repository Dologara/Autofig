"""Autofig core modules - main entry point for the library."""

# Infrastructure
from .exceptions import (
    AutofigError,
    TopologyValidationError,
    DeviceValidationError,
    TemplateRenderError,
    DeviceLoadError,
    ConfigurationError,
)
from .config import *
from .vendors import (
    VENDOR_REGISTRY,
    DEVICE_TYPES,
    get_supported_vendors,
    get_supported_device_types,
    is_vendor_supported,
    is_device_type_supported,
)
from .logging_setup import setup_logging, get_logger

# Core functions
from .loader import load_yaml, load_device_defaults, list_available_topologies
from .validator import validate_device, validate_topology, validate_field
from .processor import merge_dicts, process_topology, build_device_defaults_map
from .renderer import (
    render_device_config,
    render_topology,
    render_topology_with_errors,
    save_config,
)


def generate_configs(topology_path, output_dir="output"):
    """Main entry point: load → validate → process → render.
    
    This is the orchestrator function that ties all modules together.
    
    Args:
        topology_path: Path to YAML topology file (str or Path)
        output_dir: Directory to save configs (default: "output")
    
    Returns:
        List of generated file paths
    
    Raises:
        FileNotFoundError: If topology file not found
        TopologyValidationError: If topology structure invalid
        TemplateRenderError: If rendering fails
    """
    logger = get_logger(__name__)
    logger.info(f"Starting config generation from {topology_path}")
    
    # Load
    topology = load_yaml(topology_path)
    
    # Validate
    validate_topology(topology)
    
    # Process (merge defaults)
    defaults_map = build_device_defaults_map(load_device_defaults)
    processed = process_topology(topology, defaults_map)
    
    # Render & save
    saved_files = render_topology(processed, output_dir)
    
    logger.info(f"Config generation complete: {len(saved_files)} files")
    return saved_files


def generate_configs_with_errors(topology_path, output_dir="output"):
    """Generate configs and return detailed error info (for API use).
    
    Standardized response format for Phase 2 FastAPI.
    
    Args:
        topology_path: Path to YAML topology file
        output_dir: Directory to save configs
    
    Returns:
        Dict with keys:
            - status: 'success', 'partial_success', or 'failure'
            - data: {'saved': [...], 'generated': count}
            - errors: list of error dicts
            - metadata: {'timestamp': ..., 'total_devices': ...}
    """
    logger = get_logger(__name__)
    logger.info(f"Starting config generation (with error handling) from {topology_path}")
    
    # Load
    topology = load_yaml(topology_path)
    
    # Validate (but don't fail on device-level issues)
    try:
        validate_topology(topology)
    except Exception as e:
        logger.error(f"Topology validation failed: {e}")
        return {
            "status": "failure",
            "data": {"saved": [], "generated": 0},
            "errors": [{"device": "topology", "error": str(e), "severity": "critical"}],
            "metadata": {
                "timestamp": None,
                "total_devices": 0,
                "successful": 0,
                "failed": 1
            }
        }
    
    # Process
    defaults_map = build_device_defaults_map(load_device_defaults)
    processed = process_topology(topology, defaults_map)
    
    # Render with error handling
    result = render_topology_with_errors(processed, output_dir)
    logger.info(f"Config generation complete: {result['metadata']['successful']}/{result['metadata']['total_devices']} succeeded")
    return result


__all__ = [
    # Exceptions
    "AutofigError",
    "TopologyValidationError",
    "DeviceValidationError",
    "TemplateRenderError",
    "DeviceLoadError",
    "ConfigurationError",
    
    # Config & Vendors
    "VENDOR_REGISTRY",
    "DEVICE_TYPES",
    "get_supported_vendors",
    "get_supported_device_types",
    "is_vendor_supported",
    "is_device_type_supported",
    
    # Logging
    "setup_logging",
    "get_logger",
    
    # Main functions
    "generate_configs",
    "generate_configs_with_errors",
    
    # Loader
    "load_yaml",
    "load_device_defaults",
    "list_available_topologies",
    
    # Validator
    "validate_device",
    "validate_topology",
    "validate_field",
    
    # Processor
    "merge_dicts",
    "process_topology",
    "build_device_defaults_map",
    
    # Renderer
    "render_device_config",
    "render_topology",
    "render_topology_with_errors",
    "save_config",
]
