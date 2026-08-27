"""Custom exception classes for Autofig.

All exceptions inherit from AutofigError for easy catching.
"""


class AutofigError(Exception):
    """Base exception for all Autofig errors."""
    pass


class TopologyValidationError(AutofigError):
    """Raised when topology structure is invalid.
    
    Examples:
        - Missing 'devices' key
        - Devices list is empty
        - Device missing required fields
    """
    pass


class DeviceValidationError(AutofigError):
    """Raised when a device config is invalid.
    
    Examples:
        - Missing name, type, vendor, or hostname
        - Invalid device type
    """
    pass


class TemplateRenderError(AutofigError):
    """Raised when template rendering fails.
    
    Examples:
        - Template file not found
        - Jinja2 syntax error in template
        - Missing required fields in device config
    """
    pass


class DeviceLoadError(AutofigError):
    """Raised when loading device defaults fails.
    
    Examples:
        - Device defaults file not found
        - Invalid YAML in defaults file
    """
    pass


class ConfigurationError(AutofigError):
    """Raised when configuration is invalid.
    
    Examples:
        - Invalid output directory
        - Invalid template directory
    """
    pass
