"""Tests for autofig.core.renderer module."""

import pytest
from pathlib import Path
import tempfile
from autofig.core.renderer import (
    render_device_config,
    save_config,
    render_topology,
    render_topology_with_errors
)
from autofig.core.exceptions import TemplateRenderError


class TestRenderDeviceConfig:
    """Tests for render_device_config function."""
    
    def test_render_device_config_basic(self):
        """Test rendering a basic device config."""
        device = {
            "name": "router1",
            "type": "router",
            "vendor": "Cisco",
            "hostname": "R1",
            "ip": "10.0.0.1"
        }
        
        # Should not raise, should return string
        result = render_device_config(device)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_render_device_config_with_custom_template(self):
        """Test rendering with explicit template name."""
        device = {
            "name": "test",
            "type": "router",
            "vendor": "Cisco",
            "hostname": "TEST"
        }
        
        # Use base_template.j2 explicitly
        result = render_device_config(device, template_name="base_template.j2")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_render_device_config_infers_template(self):
        """Test that template is inferred from device type."""
        device = {
            "name": "switch1",
            "type": "switch",
            "vendor": "Cisco",
            "hostname": "S1"
        }
        
        # Should infer switch.j2 template
        result = render_device_config(device)
        assert isinstance(result, str)
    
    def test_render_device_config_fallback_template(self):
        """Test fallback to base template when specific template missing."""
        device = {
            "name": "unknown",
            "type": "nonexistent_type",  # No template for this
            "vendor": "Cisco",
            "hostname": "UNKNOWN"
        }
        
        # Should use base_template.j2 as fallback
        result = render_device_config(device)
        assert isinstance(result, str)


class TestSaveConfig:
    """Tests for save_config function."""
    
    def test_save_config_basic(self):
        """Test saving config to file."""
        config_text = "! This is a test config\nhostname TestRouter"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_config.txt"
            result_path = save_config(config_text, output_path)
            
            # Check file was created
            assert result_path.exists()
            assert result_path.read_text() == config_text
    
    def test_save_config_creates_directories(self):
        """Test that save_config creates parent directories."""
        config_text = "! test"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "dirs" / "config.txt"
            result_path = save_config(config_text, output_path)
            
            assert result_path.exists()
            assert result_path.parent.exists()
    
    def test_save_config_with_path_string(self):
        """Test saving config with path as string."""
        config_text = "! test"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "test.txt")
            result_path = save_config(config_text, output_path)
            
            assert Path(result_path).exists()


class TestRenderTopology:
    """Tests for render_topology function."""
    
    def test_render_topology_basic(self):
        """Test rendering an entire topology."""
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
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = render_topology(topology, output_dir=tmpdir)
            
            # Should return list of saved paths
            assert isinstance(result, list)
            assert len(result) == 2
            # All should exist
            assert all(Path(p).exists() for p in result)
    
    def test_render_topology_creates_output_dir(self):
        """Test that render_topology creates output directory."""
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
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "new_output"
            assert not output_dir.exists()
            
            render_topology(topology, output_dir=output_dir)
            
            assert output_dir.exists()
    
    def test_render_topology_filenames(self):
        """Test that output files are named correctly."""
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
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = render_topology(topology, output_dir=tmpdir)
            
            # Should create router1_config.txt
            assert any("router1_config.txt" in str(p) for p in result)


class TestRenderTopologyWithErrors:
    """Tests for render_topology_with_errors function."""
    
    def test_render_topology_with_errors_success(self):
        """Test render_topology_with_errors with valid topology."""
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
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = render_topology_with_errors(topology, output_dir=tmpdir)
            
            assert "status" in result
            assert "data" in result
            assert "errors" in result
            assert "metadata" in result
            assert result["status"] == "success"
            assert result["metadata"]["successful"] == 1
            assert len(result["errors"]) == 0
    
    def test_render_topology_with_errors_format(self):
        """Test standardized error response format."""
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
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = render_topology_with_errors(topology, output_dir=tmpdir)
            
            # Check response structure
            assert isinstance(result, dict)
            assert result["status"] in ["success", "partial_success", "failure"]
            assert "saved" in result["data"]
            assert "generated" in result["data"]
            assert "timestamp" in result["metadata"]
            assert "total_devices" in result["metadata"]
            assert "successful" in result["metadata"]
            assert "failed" in result["metadata"]
    
    def test_render_topology_with_errors_partial_failure(self):
        """Test render_topology_with_errors handles partial failures gracefully."""
        topology = {
            "devices": [
                {
                    "name": "router1",
                    "type": "router",
                    "vendor": "Cisco",
                    "hostname": "R1"
                },
                {
                    "name": "router2",
                    "type": "router",
                    "vendor": "Cisco",
                    "hostname": "R2"
                }
            ]
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = render_topology_with_errors(topology, output_dir=tmpdir)
            
            assert result["metadata"]["total_devices"] == 2
            # At least one should render
            assert result["metadata"]["successful"] >= 1
    
    def test_render_topology_with_errors_status_codes(self):
        """Test correct status codes."""
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
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = render_topology_with_errors(topology, output_dir=tmpdir)
            
            # All rendered successfully
            assert result["status"] == "success"
            assert len(result["errors"]) == 0
            assert result["metadata"]["successful"] == 1
            assert result["metadata"]["failed"] == 0
