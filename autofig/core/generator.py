import yaml
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import datetime

# PACKAGE_ROOT = the autofig/ package folder (this file lives at autofig/core/generator.py)
PACKAGE_ROOT = Path(__file__).resolve().parent.parent

# Data + templates ship inside the package, so they resolve correctly
# no matter what directory Autofig is run from.
DATA_DIR = PACKAGE_ROOT / "data"
TOPOLOGY_DIR = DATA_DIR / "topologies"
DEVICE_DIR = DATA_DIR / "devices"
TEMPLATE_DIR = PACKAGE_ROOT / "templates"

# Output + logs are run artifacts, so they belong in the caller's
# current working directory, not inside the installed package.
OUTPUT_DIR = Path("output")
LOG_DIR = Path("logs")

# Jinja setup
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def load_yaml(path):
    """Load a YAML file safely."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def load_device_defaults(vendor, dev_type):
    """Load device defaults if available (like router_cisco.yaml)."""
    dev_file = DEVICE_DIR / f"{dev_type.lower()}_{vendor.lower()}.yaml"
    if dev_file.exists():
        return load_yaml(dev_file)
    return {}


def validate_device(device):
    """Ensure required fields exist."""
    required = ["name", "type", "vendor", "hostname"]
    missing = [r for r in required if r not in device]
    if missing:
        raise ValueError(f"Missing required fields for {device.get('name', 'Unknown')}: {missing}")


def merge_dicts(base, override):
    """Recursive dictionary merge."""
    if not isinstance(base, dict):
        return override
    result = base.copy()
    for key, value in override.items():
        if isinstance(value, dict) and key in result:
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def list_topology_files():
    """Return all available topology YAML files. Pure, side-effect-free."""
    return list(TOPOLOGY_DIR.glob("*.yaml"))


def prompt_topology_selection(topology_files):
    """Interactively ask which topology to generate. Only called from the CLI entrypoint."""
    print("\nAvailable topologies:")
    for i, f in enumerate(topology_files, start=1):
        print(f" {i}. {f.stem}")

    choice = input("\nSelect topology number to generate (or press Enter for all): ").strip()

    if choice:
        try:
            idx = int(choice) - 1
            return [topology_files[idx]]
        except (ValueError, IndexError):
            print("Invalid selection. Generating all instead.")
            return topology_files
    return topology_files


def generate_configs(selected_files=None):
    """Main generation logic. If selected_files is None, generates all topologies
    (no prompting) — this makes the function safe to import and call from tests,
    the CLI, or (later) the API/web UI without ever touching stdin."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    if selected_files is None:
        selected_files = list_topology_files()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    run_log = LOG_DIR / f"run_{timestamp}.log"

    with run_log.open("w") as log:
        log.write(f"[INFO] Autofig run started at {timestamp}\n")

        for topo_file in selected_files:
            topo_data = load_yaml(topo_file)
            topo_name = topo_data.get("topology_name", topo_file.stem)

            log.write(f"[INFO] Processing topology: {topo_name}\n")

            # Create subfolder for this topology
            topo_output = OUTPUT_DIR / f"{timestamp}_{topo_name.replace(' ', '_')}"
            topo_output.mkdir(exist_ok=True)

            for device in topo_data.get("devices", []):
                try:
                    validate_device(device)
                    vendor = device["vendor"]
                    dev_type = device["type"]

                    # Merge defaults from device YAMLs if found
                    dev_defaults = load_device_defaults(vendor, dev_type)
                    merged = merge_dicts(dev_defaults.get("defaults", {}), topo_data.get("defaults", {}))
                    device_full = merge_dicts(merged, device)

                    # Select template
                    template_name = f"{dev_type.lower()}.j2"
                    try:
                        template = env.get_template(template_name)
                    except Exception:
                        template = env.get_template("base_template.j2")
                        log.write(f"[WARN] Template not found for {dev_type}, using base.\n")

                    # Render config
                    config_text = template.render(
                        device=device_full,
                        defaults=device_full,
                        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )

                    # Save output
                    out_path = topo_output / f"{device['name']}_config.txt"
                    out_path.write_text(config_text)
                    log.write(f"[OK] {device['name']} ({dev_type}) -> {out_path.name}\n")

                except Exception as e:
                    log.write(f"[ERROR] Failed to process {device.get('name', 'Unknown')}: {e}\n")

        log.write(f"[INFO] Run completed at {datetime.now()}\n")

    print(f"\n Generation complete! See logs/{run_log.name} for details.\n")
    return run_log


def main():
    """Interactive entrypoint — the only place that touches stdin."""
    topology_files = list_topology_files()
    selected_files = prompt_topology_selection(topology_files)
    generate_configs(selected_files)


if __name__ == "__main__":
    main()
