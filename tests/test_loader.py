"""Tests for autofig.core.loader module."""

import pytest
from pathlib import Path
import tempfile
import yaml
from autofig.core.loader import load_yaml, load_device_defaults, list_available_topologies
from autofig.core.exceptions import DeviceLoadError


class TestLoadYaml:
    """Tests for load_yaml function."""
    
    def test_load_yaml_valid(self):
        """Test loading a valid YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({"devices": [{"name": "router1"}]}, f)
            temp_path = f.name
        
        try:
            data = load_yaml(temp_path)
            assert isinstance(data, dict)
            assert "devices" in data
        finally:
            Path(temp_path).unlink()
    
    def test_load_yaml_not_found(self):
        """Test loading non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_yaml("/fake/path/nonexistent.yaml")
    
    def test_load_yaml_malformed(self):
        """Test loading malformed YAML raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: [yaml: content:")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                load_yaml(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_load_yaml_not_dict(self):
        """Test loading YAML that doesn't parse to dict."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(["list", "instead", "of", "dict"], f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                load_yaml(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_load_yaml_with_path_object(self):
        """Test loading YAML with Path object."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({"devices": []}, f)
            temp_path = Path(f.name)
        
        try:
            data = load_yaml(temp_path)
            assert isinstance(data, dict)
        finally:
            temp_path.unlink()


class TestLoadDeviceDefaults:
    """Tests for load_device_defaults function."""
    
    def test_load_device_defaults_cisco_router(self):
        """Test loading Cisco router defaults."""
        defaults = load_device_defaults("Cisco", "router")
        # Should return dict (empty or with content)
        assert isinstance(defaults, dict)
    
    def test_load_device_defaults_cisco_switch(self):
        """Test loading Cisco switch defaults."""
        defaults = load_device_defaults("Cisco", "switch")
        assert isinstance(defaults, dict)
    
    def test_load_device_defaults_cisco_multilayer_switch(self):
        """Test loading Cisco multilayer switch defaults."""
        defaults = load_device_defaults("Cisco", "multilayer_switch")
        assert isinstance(defaults, dict)
    
    def test_load_device_defaults_not_found(self):
        """Test loading non-existent device type returns empty dict."""
        defaults = load_device_defaults("Cisco", "nonexistent_device")
        assert defaults == {}
    
    def test_load_device_defaults_unsupported_vendor(self):
        """Test loading unsupported vendor returns empty dict."""
        defaults = load_device_defaults("Juniper", "router")
        assert defaults == {}


class TestListAvailableTopologies:
    """Tests for list_available_topologies function."""
    
    def test_list_available_topologies(self):
        """Test listing topology files."""
        topologies = list_available_topologies()
        assert isinstance(topologies, list)
        assert len(topologies) > 0
        # All should be Path objects
        assert all(isinstance(t, Path) for t in topologies)
        # All should end in .yaml
        assert all(t.suffix == ".yaml" for t in topologies)
    
    def test_topologies_are_sorted(self):
        """Test that topologies are sorted."""
        topologies = list_available_topologies()
        sorted_topologies = sorted(topologies)
        assert topologies == sorted_topologies
    
    def test_topologies_exist(self):
        """Test that all returned topologies exist."""
        topologies = list_available_topologies()
        for topo in topologies:
            assert topo.exists(), f"Topology file does not exist: {topo}"
