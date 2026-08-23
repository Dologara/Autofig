"""Configuration and constants for Autofig."""

import os
from pathlib import Path

# Package root: autofig/core/config.py → parent.parent is autofig/
PACKAGE_ROOT = Path(__file__).resolve().parent.parent

# Data + templates ship inside the package, so they resolve correctly no
# matter what directory Autofig is run from (or where it's pip-installed to).
DATA_DIR = PACKAGE_ROOT / "data"
TEMPLATE_DIR = PACKAGE_ROOT / "templates"

# Subdirectories within DATA_DIR
TOPOLOGY_DIR = DATA_DIR / "topologies"
DEVICE_DEFAULTS_DIR = DATA_DIR / "devices"

# Output and logs are run artifacts, not shipped package data - they default
# to the caller's current working directory (overridable via env var), never
# to PACKAGE_ROOT. Writing here matters especially for real (non-editable)
# installs, where PACKAGE_ROOT lives under site-packages and is often not
# writable by the user running the CLI.
AUTOFIG_OUTPUT_DIR = Path(os.getenv("AUTOFIG_OUTPUT_DIR", "output"))
LOG_DIR = Path(os.getenv("AUTOFIG_LOG_DIR", "logs"))

# Logging configuration
AUTOFIG_LOG_LEVEL = os.getenv("AUTOFIG_LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Template configuration
FALLBACK_TEMPLATE = "base_template.j2"

# Feature flags (for future phases)
ENABLE_NETBOX_INTEGRATION = os.getenv("ENABLE_NETBOX_INTEGRATION", "false").lower() == "true"
ENABLE_ANSIBLE_EXPORT = os.getenv("ENABLE_ANSIBLE_EXPORT", "false").lower() == "true"

# Note: directories are intentionally NOT created here at import time.
# Creating output/log directories as a side effect of `import autofig...`
# means every import - including from a test collector or a read-only
# install - touches the filesystem. DATA_DIR/TEMPLATE_DIR ship with the
# package so they always exist already; AUTOFIG_OUTPUT_DIR/LOG_DIR are
# created lazily by whichever function actually writes to them
# (see renderer.py's render_topology / render_topology_with_errors).
