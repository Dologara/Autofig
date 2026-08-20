"""Autofig core modules - main entry point for the library."""

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
        ValueError: If topology structure invalid
    """
    # Load
    topology = load_yaml(topology_path)
    
    # Validate
    validate_topology(topology)
    
    # Process (merge defaults)
    defaults_map = build_device_defaults_map(load_device_defaults)
    processed = process_topology(topology, defaults_map)
    
    # Render & save
    saved_files = render_topology(processed, output_dir)
    
    return saved_files
def generate_configs_with_errors(topology_path, output_dir="output"):
    """Generate configs and return detailed error info (for API use).
    
    Args:
        topology_path: Path to YAML topology file
        output_dir: Directory to save configs
    
    Returns:
        Dict with keys:
            - saved: list of file paths
            - errors: list of error dicts
            - total_devices: count
            - successful: count
    """
    # Load
    topology = load_yaml(topology_path)
    
    # Validate (but don't fail on device-level issues)
    try:
        validate_topology(topology)
    except ValueError as e:
        return {
            "saved": [],
            "errors": [{"topology": str(e)}],
            "total_devices": 0,
            "successful": 0,
        }
    
    # Process
    defaults_map = build_device_defaults_map(load_device_defaults)
    processed = process_topology(topology, defaults_map)
    
    # Render with error handling
    return render_topology_with_errors(processed, output_dir)


__all__ = [
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
