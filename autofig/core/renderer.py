"""Render Jinja2 templates and save configuration files.

Enhanced with:
- Type hints
- Logging
- Standardized error response format
- Bug fixes (proper indentation)
"""

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from .logging_setup import get_logger
from .config import TEMPLATE_DIR, FALLBACK_TEMPLATE
from .exceptions import TemplateRenderError

logger = get_logger(__name__)

# Jinja2 setup
jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def get_template(template_name: str):
    """Get a Jinja2 template by name.
    
    Args:
        template_name: Name like 'router.j2'
    
    Returns:
        Jinja2 Template object
    
    Raises:
        TemplateNotFound: If template doesn't exist
    """
    logger.debug(f"Loading template: {template_name}")
    try:
        return jinja_env.get_template(template_name)
    except TemplateNotFound:
        logger.error(f"Template not found: {template_name}")
        raise TemplateNotFound(
            f"Template '{template_name}' not found in {TEMPLATE_DIR}"
        )


def render_device_config(device: Dict, template_name: Optional[str] = None) -> str:
    """Render a single device's configuration.
    
    Args:
        device: Device dict with all config
        template_name: Template filename. If None, infer from device type.
    
    Returns:
        Rendered config as string
    
    Raises:
        TemplateRenderError: If rendering fails
    """
    device_name = device.get("name", "Unknown")
    logger.info(f"Rendering config for device: {device_name}")
    
    # Infer template if not provided
    if not template_name:
        device_type = device.get("type", "").lower()
        template_name = f"{device_type}.j2"
        logger.debug(f"Inferred template: {template_name}")
    
    try:
        template = get_template(template_name)
    except TemplateNotFound:
        # Fallback to base template
        logger.warning(f"Template {template_name} not found, using fallback")
        template = get_template(FALLBACK_TEMPLATE)
    
    try:
        # Render with device data
        rendered = template.render(
            device=device,
            defaults=device,
            now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        logger.debug(f"Rendered {len(rendered)} bytes for {device_name}")
        return rendered
    except Exception as e:
        logger.error(f"Failed to render template for {device_name}: {e}")
        raise TemplateRenderError(f"Failed to render config for {device_name}: {e}")


def save_config(config_text: str, output_path: Path | str) -> Path:
    """Save rendered config to file.
    
    Args:
        config_text: Rendered configuration string
        output_path: Path to save (str or Path)
    
    Returns:
        Path object of saved file
    """
    output_path = Path(output_path)
    logger.debug(f"Saving config to: {output_path}")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(config_text)
    
    logger.info(f"Saved config file: {output_path}")
    return output_path


def render_topology(topology: Dict, output_dir: Path | str = "output") -> List[Path]:
    """Render all devices in a topology to files.
    
    Args:
        topology: Processed topology dict
        output_dir: Directory to save configs (str or Path)
    
    Returns:
        List of saved file paths
    """
    output_dir = Path(output_dir)
    logger.info(f"Rendering topology with {len(topology.get('devices', []))} devices")
    logger.info(f"Output directory: {output_dir}")
    
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
            logger.error(f"Error rendering {device.get('name', 'Unknown')}: {e}")
    
    logger.info(f"Topology rendering complete: {len(saved_files)} files saved")
    return saved_files


def render_topology_with_errors(topology: Dict, output_dir: Path | str = "output") -> Dict:
    """Render topology and return both successes and errors (for API use).
    
    Standardized error response format for Phase 2 FastAPI.
    
    Args:
        topology: Processed topology dict
        output_dir: Directory to save configs
    
    Returns:
        Dict with keys:
            - status: 'success', 'partial_success', or 'failure'
            - data: {'saved': [...], 'generated': count}
            - errors: list of error dicts with 'device', 'error', 'severity'
            - metadata: {'timestamp': ..., 'total_devices': ...}
    """
    output_dir = Path(output_dir)
    logger.info(f"Rendering topology with error handling: {len(topology.get('devices', []))} devices")
    
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
            logger.error(f"Error rendering {device.get('name', 'Unknown')}: {e}")
            errors.append({
                "device": device.get('name', 'Unknown'),
                "error": str(e),
                "severity": "error"
            })
    
    total_devices = len(topology.get("devices", []))
    successful = len(saved_files)
    
    # Determine overall status
    if len(errors) == 0:
        status = "success"
    elif successful > 0:
        status = "partial_success"
    else:
        status = "failure"
    
    logger.info(f"Rendering complete - Status: {status}, Success: {successful}/{total_devices}")
    
    return {
        "status": status,
        "data": {
            "saved": saved_files,
            "generated": successful
        },
        "errors": errors,
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_devices": total_devices,
            "successful": successful,
            "failed": len(errors)
        }
    }
