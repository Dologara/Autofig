"""Legacy generator interface + CLI utilities.

This module maintains backward compatibility with the old generator.py interface
while using the new modular architecture under the hood.
"""

from pathlib import Path
from .loader import list_available_topologies
from . import generate_configs


# Package paths (for CLI use)
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
TOPOLOGY_DIR = PACKAGE_ROOT / "data" / "topologies"


def list_topology_files():
    """Return all available topology YAML files. Pure, side-effect-free.
    
    Used by CLI to show available topologies.
    """
    return list_available_topologies()


def prompt_topology_selection(topology_files):
    """Interactively ask which topology to generate. Only called from CLI.
    
    Args:
        topology_files: List of Path objects
    
    Returns:
        List of selected topology files
    """
    print("\nAvailable topologies:")
    for i, f in enumerate(topology_files, start=1):
        print(f"  {i}. {f.stem}")
    
    choice = input("\nSelect topology number to generate (or press Enter for all): ").strip()
    
    if choice:
        try:
            idx = int(choice) - 1
            return [topology_files[idx]]
        except (ValueError, IndexError):
            print("Invalid selection. Generating all instead.")
            return topology_files
    
    return topology_files


def generate_from_cli(selected_topologies, output_dir="output"):
    """CLI wrapper: generate configs for selected topologies.
Args:
        selected_topologies: List of topology file paths
        output_dir: Output directory
    
    Returns:
        List of all generated file paths
    """
    all_files = []
    
    for topology_path in selected_topologies:
        try:
            files = generate_configs(topology_path, output_dir)
            all_files.extend(files)
            print(f"✓ Generated {len(files)} configs from {topology_path.stem}")
        except Exception as e:
            print(f"✗ Error processing {topology_path.stem}: {e}")
    
    return all_files
