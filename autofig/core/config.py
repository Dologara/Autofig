"""Configuration and constants for Autofig."""

import os
from pathlib import Path

# Package root: autofig/core/config.py → parent.parent is autofig/
PACKAGE_ROOT = Path(__file__).resolve().parent.parent

# Main directories
DATA_DIR = PACKAGE_ROOT / "data"
TEMPLATE_DIR = PACKAGE_ROOT / "templates"
LOG_DIR = PACKAGE_ROOT / "logs"

# Subdirectories within DATA_DIR
TOPOLOGY_DIR = DATA_DIR / "topologies"
DEVICE_DEFAULTS_DIR = DATA_DIR / "devices"

# Output directory (can be overridden via env var)
AUTOFIG_OUTPUT_DIR = Path(os.getenv("AUTOFIG_OUTPUT_DIR", Path.home() / "autofig_output"))

# Logging configuration
AUTOFIG_LOG_LEVEL = os.getenv("AUTOFIG_LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Template configuration
FALLBACK_TEMPLATE = "base_template.j2"

# Feature flags (for future phases)
ENABLE_NETBOX_INTEGRATION = os.getenv("ENABLE_NETBOX_INTEGRATION", "false").lower() == "true"
ENABLE_ANSIBLE_EXPORT = os.getenv("ENABLE_ANSIBLE_EXPORT", "false").lower() == "true"

# Create directories if they don't exist
for directory in [DATA_DIR, TEMPLATE_DIR, LOG_DIR, TOPOLOGY_DIR, DEVICE_DEFAULTS_DIR, AUTOFIG_OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
