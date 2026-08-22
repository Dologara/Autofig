"""Tests for autofig.core.validator module."""

import pytest
from autofig.core.validators import validate_device, validate_topology, validate_field
from autofig.core.exceptions import TopologyValidationError, DeviceValidationError


class TestValidateDevice:
    """Tests for validate_device function."""
    
    def test_validate_device_valid(self):
        """Test validating a correct device."""
        device = {
            "name": "router1",
            "type": "router",
            "vendor": "Cisco",
            "hostname": "R1"
        }
        assert validate_device(device) is True
    
    def test_validate_device_missing_name(self):
        """Test device missing 'name' field."""
        device = {
            "type": "router",
            "vendor": "Cisco",
            "hostname": "R1"
        }
        with pytest.raises(DeviceValidationError):
            validate_device(device)
    
    def test_validate_device_missing_type(self):
        """Test device missing 'type' field."""
        device = {
            "name": "router1",
            "vendor": "Cisco",
            "hostname": "R1"
        }
        with pytest.raises(DeviceValidationError):
            validate_device(device)
    
    def test_validate_device_missing_vendor(self):
        """Test device missing 'vendor' field."""
        device = {
            "name": "router1",
            "type": "router",
            "hostname": "R1"
        }
        with pytest.raises(DeviceValidationError):
            validate_device(device)
    
    def test_validate_device_missing_hostname(self):
        """Test device missing 'hostname' field."""
        device = {
            "name": "router1",
            "type": "router",
            "vendor": "Cisco"
        }
        with pytest.raises(DeviceValidationError):
            validate_device(device)
    
    def test_validate_device_unsupported_vendor(self):
        """Test device with unsupported vendor."""
        device = {
            "name": "router1",
            "type": "router",
            "vendor": "UnsupportedVendor",
            "hostname": "R1"
        }
        with pytest.raises(DeviceValidationError):
            validate_device(device)
    
    def test_validate_device_unsupported_type_for_vendor(self):
        """Test device with unsupported type for vendor."""
        device = {
            "name": "device1",
            "type": "unsupported_type",
            "vendor": "Cisco",
            "hostname": "D1"
        }
        with pytest.raises(DeviceValidationError):
            validate_device(device)
    
    def test_validate_device_with_extra_fields(self):
        """Test device with extra custom fields (should be allowed)."""
        device = {
            "name": "router1",
            "type": "router",
            "vendor": "Cisco",
            "hostname": "R1",
            "custom_field": "value",
            "bgp_asn": 65001
        }
        assert validate_device(device) is True


class TestValidateTopology:
    """Tests for validate_topology function."""
    
    def test_validate_topology_valid(self):
        """Test validating a correct topology."""
        topology = {
            "devices": [
                {
                    "name": "router1",
                    "type": "router",
                    "vendor": "Cisco",
                    "hostname": "R1"
                }
            ]
        }
        assert validate_topology(topology) is True
    
    def test_validate_topology_not_dict(self):
        """Test topology that is not a dict."""
        with pytest.raises(TopologyValidationError):
            validate_topology("not a dict")
    
    def test_validate_topology_missing_devices(self):
        """Test topology missing 'devices' key."""
        topology = {"name": "my_topology"}
        with pytest.raises(TopologyValidationError):
            validate_topology(topology)
    
    def test_validate_topology_devices_not_list(self):
        """Test topology with non-list devices."""
        topology = {"devices": "not a list"}
        with pytest.raises(TopologyValidationError):
            validate_topology(topology)
    
    def test_validate_topology_empty_devices(self):
        """Test topology with empty devices list."""
        topology = {"devices": []}
        with pytest.raises(TopologyValidationError):
            validate_topology(topology)
    
    def test_validate_topology_multiple_devices(self):
        """Test topology with multiple devices."""
        topology = {
            "devices": [
                {
                    "name": "router1",
                    "type": "router",
                    "vendor": "Cisco",
                    "hostname": "R1"
                },
                {
                    "name": "switch1",
                    "type": "switch",
                    "vendor": "Cisco",
                    "hostname": "S1"
                }
            ]
        }
        assert validate_topology(topology) is True
    
    def test_validate_topology_invalid_device_in_list(self):
        """Test topology with invalid device in list."""
        topology = {
            "devices": [
                {
                    "name": "router1",
                    "type": "router",
                    "vendor": "Cisco",
                    "hostname": "R1"
                },
                {
                    "name": "switch1",
                    # Missing type, vendor, hostname
                }
            ]
        }
        with pytest.raises(DeviceValidationError):
            validate_topology(topology)


class TestValidateField:
    """Tests for validate_field function."""
    
    def test_validate_field_int_valid(self):
        """Test validating an integer field."""
        assert validate_field(42, "int", "port") is True
    
    def test_validate_field_int_invalid(self):
        """Test validating wrong type for int field."""
        with pytest.raises(ValueError):
            validate_field("not_an_int", "int", "port")
    
    def test_validate_field_str_valid(self):
        """Test validating a string field."""
        assert validate_field("hello", "str", "hostname") is True
    
    def test_validate_field_str_invalid(self):
        """Test validating wrong type for str field."""
        with pytest.raises(ValueError):
            validate_field(123, "str", "hostname")
    
    def test_validate_field_list_valid(self):
        """Test validating a list field."""
        assert validate_field([1, 2, 3], "list", "ports") is True
    
    def test_validate_field_list_invalid(self):
        """Test validating wrong type for list field."""
        with pytest.raises(ValueError):
            validate_field("not_a_list", "list", "ports")
    
    def test_validate_field_dict_valid(self):
        """Test validating a dict field."""
        assert validate_field({"key": "value"}, "dict", "config") is True
    
    def test_validate_field_dict_invalid(self):
        """Test validating wrong type for dict field."""
        with pytest.raises(ValueError):
            validate_field([1, 2, 3], "dict", "config")
    
    def test_validate_field_unknown_type(self):
        """Test validating unknown field type."""
        with pytest.raises(ValueError):
            validate_field("value", "unknown_type", "field")
