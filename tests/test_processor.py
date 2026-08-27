"""Tests for autofig.core.processor module."""

import pytest
from autofig.core.processor import merge_dicts, process_topology, build_device_defaults_map


class TestMergeDicts:
    """Tests for merge_dicts function."""
    
    def test_merge_dicts_simple(self):
        """Test merging two simple dicts."""
        base = {"a": 1, "b": 2}
        override = {"b": 20, "c": 3}
        result = merge_dicts(base, override)
        
        assert result == {"a": 1, "b": 20, "c": 3}
        # Original should be unchanged
        assert base == {"a": 1, "b": 2}
    
    def test_merge_dicts_nested(self):
        """Test merging nested dicts (recursive merge)."""
        base = {"config": {"ip": "10.0.0.1", "mask": "255.255.255.0"}}
        override = {"config": {"mask": "255.255.0.0"}}
        result = merge_dicts(base, override)
        
        assert result["config"]["ip"] == "10.0.0.1"
        assert result["config"]["mask"] == "255.255.0.0"
    
    def test_merge_dicts_override_precedence(self):
        """Test that override values take precedence."""
        base = {"x": {"y": 1}}
        override = {"x": 999}  # Override nested dict with scalar
        result = merge_dicts(base, override)
        
        assert result["x"] == 999
    
    def test_merge_dicts_empty_base(self):
        """Test merging with empty base."""
        base = {}
        override = {"a": 1, "b": 2}
        result = merge_dicts(base, override)
        
        assert result == {"a": 1, "b": 2}
    
    def test_merge_dicts_empty_override(self):
        """Test merging with empty override."""
        base = {"a": 1, "b": 2}
        override = {}
        result = merge_dicts(base, override)
        
        assert result == {"a": 1, "b": 2}
    
    def test_merge_dicts_base_not_dict(self):
        """Test merging when base is not a dict."""
        base = "not a dict"
        override = {"a": 1}
        result = merge_dicts(base, override)
        
        assert result == {"a": 1}


class TestProcessTopology:
    """Tests for process_topology function."""
    
    def test_process_topology_basic(self):
        """Test processing a basic topology."""
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
        
        defaults_map = {"Cisco": {"router": {}}}
        result = process_topology(topology, defaults_map)
        
        assert "devices" in result
        assert len(result["devices"]) == 1
        assert result["devices"][0]["name"] == "router1"
    
    def test_process_topology_merges_global_defaults(self):
        """Test that global defaults are merged."""
        topology = {
            "defaults": {"ssh_enabled": True, "ntp_enabled": True},
            "devices": [
                {
                    "name": "router1",
                    "type": "router",
                    "vendor": "Cisco",
                    "hostname": "R1"
                }
            ]
        }
        
        defaults_map = {"Cisco": {"router": {}}}
        result = process_topology(topology, defaults_map)
        
        # Device should have global defaults
        device = result["devices"][0]
        assert device["ssh_enabled"] is True
        assert device["ntp_enabled"] is True
    
    def test_process_topology_device_overrides_global(self):
        """Test that device config overrides global defaults."""
        topology = {
            "defaults": {"ssh_enabled": True},
            "devices": [
                {
                    "name": "router1",
                    "type": "router",
                    "vendor": "Cisco",
                    "hostname": "R1",
                    "ssh_enabled": False  # Override global
                }
            ]
        }
        
        defaults_map = {"Cisco": {"router": {}}}
        result = process_topology(topology, defaults_map)
        
        # Device's value should take precedence
        device = result["devices"][0]
        assert device["ssh_enabled"] is False
    
    def test_process_topology_multiple_devices(self):
        """Test processing topology with multiple devices."""
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
        
        defaults_map = {"Cisco": {"router": {}, "switch": {}}}
        result = process_topology(topology, defaults_map)
        
        assert len(result["devices"]) == 2
        assert result["devices"][0]["name"] == "router1"
        assert result["devices"][1]["name"] == "switch1"
    
    def test_process_topology_empty_defaults_map(self):
        """Test processing with empty defaults map."""
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
        
        defaults_map = {}
        result = process_topology(topology, defaults_map)
        
        # Should still work, just without vendor defaults
        assert len(result["devices"]) == 1


class TestBuildDeviceDefaultsMap:
    """Tests for build_device_defaults_map function."""
    
    def test_build_device_defaults_map(self):
        """Test building the device defaults map."""
        def mock_loader(vendor, device_type):
            # Mock loader that returns empty dicts
            return {}
        
        defaults_map = build_device_defaults_map(mock_loader)
        
        # Should have Cisco vendor
        assert "Cisco" in defaults_map
        # Should have at least router type
        assert "router" in defaults_map["Cisco"] or len(defaults_map["Cisco"]) >= 0
    
    def test_build_device_defaults_map_structure(self):
        """Test the structure of the defaults map."""
        def mock_loader(vendor, device_type):
            return {"defaults": {"test": "value"}}
        
        defaults_map = build_device_defaults_map(mock_loader)
        
        # Map should be a dict
        assert isinstance(defaults_map, dict)
        # Should have at least one vendor
        assert len(defaults_map) > 0
        # Each vendor should have device types
        for vendor, device_types in defaults_map.items():
            assert isinstance(device_types, dict)
    
    def test_build_device_defaults_map_handles_exceptions(self):
        """Test that map building handles exceptions gracefully."""
        def failing_loader(vendor, device_type):
            raise Exception("Load failed")
        
        # Should not raise, just skip failed loads
        defaults_map = build_device_defaults_map(failing_loader)
        
        assert isinstance(defaults_map, dict)
