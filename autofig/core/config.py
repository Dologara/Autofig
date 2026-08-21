"""Configuration and constants for Autofig.

Environment-based configuration for flexibility (especially for deployment).
"""

import os
from pathlib import Path

# Package root directory
PACKAGE_ROOT = Path(__file__).resolve().parent.parent

# Directories
DATA_DIR = PACKAGE_ROOT / "data"
TOPOLOGY_DIR = DATA_DIR / "topologies"
DEVICE_DEFAULTS_DIR = DATA_DIR / "devices"
TEMPLATE_DIR = PACKAGE_ROOT / "templates"

# Output configuration (can be overridden via environment variables)
OUTPUT_DIR = os.getenv("AUTOFIG_OUTPUT_DIR", "output")
LOGS_DIR = os.getenv("AUTOFIG_LOGS_DIR", "logs")

# Logging configuration
LOG_LEVEL = os.getenv("AUTOFIG_LOG_LEVEL", "INFO")
LOG_FILE = os.path.join(LOGS_DIR, "autofig.log")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Template configuration
DEFAULT_TEMPLATE_EXTENSION = ".j2"
FALLBACK_TEMPLATE = "base_template.j2"

# Validation configuration
HOSTNAME_MAX_LENGTH = 15
DEVICE_NAME_MAX_LENGTH = 255

# API configuration (for Phase 2)
API_VERSION = "1.0"
API_TIMEOUT = 30  # seconds

# Vendor configuration
DEFAULT_VENDOR = "Cisco"
DEFAULT_OS = "ios"

# Feature flags (for future use)
ENABLE_NETBOX_INTEGRATION = os.getenv("AUTOFIG_NETBOX_ENABLED", "false").lower() == "true"
ENABLE_ANSIBLE_EXPORT = os.getenv("AUTOFIG_ANSIBLE_ENABLED", "false").lower() == "true"

# Validate critical directories exist
if not TEMPLATE_DIR.exists():
    raise FileNotFoundError(f"Template directory not found: {TEMPLATE_DIR}")

if not DEVICE_DEFAULTS_DIR.exists():
    raise FileNotFoundError(f"Device defaults directory not found: {DEVICE_DEFAULTS_DIR}")
