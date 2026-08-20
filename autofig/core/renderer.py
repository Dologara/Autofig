"""Render Jinja2 templates and save configuration files."""

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from pathlib import Path
from datetime import datetime


# Paths
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PACKAGE_ROOT / "templates"

# Jinja2 setup
jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def get_template(template_name):
    """Get a Jinja2 template by name.
    
    Args:
        template_name: Name like 'router.j2'
    
    Returns:
        Jinja2 Template object
    
    Raises:
        TemplateNotFound: If template doesn't exist
    """
    try:
        return jinja_env.get_template(template_name)
    except TemplateNotFound:
        raise TemplateNotFound(
            f"Template '{template_name}' not found in {TEMPLATE_DIR}"
        )


def render_device_config(device, template_name=None):
    """Render a single device's configuration.
    
    Args:
        device: Device dict with all config
        template_name: Template filename. If None, infer from device type.
    
    Returns:
        Rendered config as string
    
    Raises:
        TemplateNotFound: If template doesn't exist
    """
    # Infer template if not provided
    if not template_name:
        device_type = device.get("type", "").lower()
        template_name = f"{device_type}.j2"
try:
        template = get_template(template_name)
    except TemplateNotFound:
        # Fallback to base template
        template = get_template("base_template.j2")
    
    # Render with device data
    rendered = template.render(
        device=device,
        defaults=device,
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    return rendered


def save_config(config_text, output_path):
    """Save rendered config to file.
    
    Args:
        config_text: Rendered configuration string
        output_path: Path to save (str or Path)
    
    Returns:
        Path object of saved file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_path.write_text(config_text)
    
    return output_path


def render_topology(topology, output_dir="output"):
    """Render all devices in a topology to files.
    
    Args:
        topology: Processed topology dict
        output_dir: Directory to save configs (str or Path)
    
    Returns:
        List of saved file paths
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    saved_files = []
    
    for device in topology.get("devices", []):
        try:
            # Render config
            config = render_device_config(device)
            
            # Save to file
            filename = f"{device['name']}_config.txt"
            filepath = output_dir / filename
            saved_path = save_config(config, filepath)
saved_files.append(saved_path)
        
        except Exception as e:
            print(f"Error rendering {device.get('name', 'Unknown')}: {e}")
    
    return saved_files


def render_topology_with_errors(topology, output_dir="output"):
    """Render topology and return both successes and errors (for API use).
    
    Args:
        topology: Processed topology dict
        output_dir: Directory to save configs
    
    Returns:
        Dict with keys:
            - saved: list of file paths (as strings)
            - errors: list of error dicts with 'device' and 'error' keys
            - total_devices: total device count
            - successful: successful render count
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    saved_files = []
    errors = []
    
    for device in topology.get("devices", []):
        try:
            config = render_device_config(device)
            filename = f"{device['name']}_config.txt"
            filepath = output_dir / filename
            saved_path = save_config(config, filepath)
            saved_files.append(str(saved_path))
        
        except Exception as e:
            errors.append({
                "device": device.get('name', 'Unknown'),
                "error": str(e)
            })
    
    return {
        "saved": saved_files,
        "errors": errors,
        "total_devices": len(topology.get("devices", [])),
        "successful": len(saved_files)
    }
