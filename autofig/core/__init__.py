"""Autofig core package - network configuration generator."""

from .loader import load_yaml, load_device_defaults, list_available_topologies
from .validators import validate_device, validate_topology, validate_field
from .processor import merge_dicts, process_topology, build_device_defaults_map
from .renderer import render_device_config, save_config, render_topology, render_topology_with_errors
from .exceptions import (
    AutofigError,
    TopologyValidationError,
    DeviceValidationError,
    TemplateRenderError,
    DeviceLoadError,
    ConfigurationError,
)
from .vendors import (
    VENDOR_REGISTRY,
    DEVICE_TYPES,
    get_supported_vendors,
    is_vendor_supported,
    is_device_type_supported,
    get_supported_device_types,
)
from .config import (
    PACKAGE_ROOT,
    DATA_DIR,
    TEMPLATE_DIR,
    LOG_DIR,
    AUTOFIG_OUTPUT_DIR,
    AUTOFIG_LOG_LEVEL,
)
from .logging_setup import setup_logging, get_logger

__all__ = [
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
    "save_config",
    "render_topology",
    "render_topology_with_errors",
    # Exceptions
    "AutofigError",
    "TopologyValidationError",
    "DeviceValidationError",
    "TemplateRenderError",
    "DeviceLoadError",
    "ConfigurationError",
    # Vendors
    "VENDOR_REGISTRY",
    "DEVICE_TYPES",
    "get_supported_vendors",
    "is_vendor_supported",
    "is_device_type_supported",
    "get_supported_device_types",
    # Config
    "PACKAGE_ROOT",
    "DATA_DIR",
    "TEMPLATE_DIR",
    "LOG_DIR",
    "AUTOFIG_OUTPUT_DIR",
    "AUTOFIG_LOG_LEVEL",
    # Logging
    "setup_logging",
    "get_logger",
]
