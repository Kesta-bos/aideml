"""
Tests for the configuration service.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from services.config_service import ConfigService, ConfigurationError
from models.config_models import ConfigCategory, ConfigExportFormat
from models.validation_models import ValidationContext


class TestConfigService:
    """Test cases for ConfigService."""
    
    @pytest.fixture
    def config_service(self):
        """Create a ConfigService instance for testing."""
        with patch('services.config_service.Path') as mock_path:
            # Mock the AIDE config path to exist
            mock_config_path = MagicMock()
            mock_config_path.exists.return_value = True
            mock_path.return_value.parent.parent.parent.__truediv__.return_value = mock_config_path
            
            service = ConfigService()
            return service
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing."""
        return {
            "data_dir": "/path/to/data",
            "goal": "Test goal",
            "eval": "Test evaluation",
            "log_dir": "logs",
            "workspace_dir": "workspaces",
            "preprocess_data": True,
            "copy_data": True,
            "exp_name": "test-experiment",
            "exec": {
                "timeout": 3600,
                "agent_file_name": "runfile.py",
                "format_tb_ipython": False
            },
            "generate_report": True,
            "report": {
                "model": "gpt-4-turbo",
                "temp": 1.0
            },
            "agent": {
                "steps": 20,
                "k_fold_validation": 5,
                "expose_prediction": False,
                "data_preview": True,
                "code": {
                    "model": "gpt-4-turbo",
                    "temp": 0.5
                },
                "feedback": {
                    "model": "gpt-4-turbo",
                    "temp": 0.5
                },
                "search": {
                    "max_debug_depth": 3,
                    "debug_prob": 0.5,
                    "num_drafts": 5
                }
            }
        }
    
    def test_get_nested_value(self, config_service, sample_config):
        """Test getting nested values from configuration."""
        # Test simple value
        assert config_service._get_nested_value(sample_config, "data_dir") == "/path/to/data"
        
        # Test nested value
        assert config_service._get_nested_value(sample_config, "agent.steps") == 20
        
        # Test deeply nested value
        assert config_service._get_nested_value(sample_config, "agent.code.model") == "gpt-4-turbo"
        
        # Test non-existent value
        assert config_service._get_nested_value(sample_config, "nonexistent") is None
        assert config_service._get_nested_value(sample_config, "agent.nonexistent") is None
    
    def test_set_nested_value(self, config_service):
        """Test setting nested values in configuration."""
        config = {}
        
        # Test simple value
        config_service._set_nested_value(config, "simple", "value")
        assert config["simple"] == "value"
        
        # Test nested value
        config_service._set_nested_value(config, "nested.key", "nested_value")
        assert config["nested"]["key"] == "nested_value"
        
        # Test deeply nested value
        config_service._set_nested_value(config, "deep.nested.key", "deep_value")
        assert config["deep"]["nested"]["key"] == "deep_value"
    
    def test_get_category_fields(self, config_service):
        """Test getting field paths for categories."""
        project_fields = config_service._get_category_fields(ConfigCategory.PROJECT)
        assert "data_dir" in project_fields
        assert "goal" in project_fields
        assert "log_dir" in project_fields
        
        agent_fields = config_service._get_category_fields(ConfigCategory.AGENT)
        assert "agent" in agent_fields
        
        models_fields = config_service._get_category_fields(ConfigCategory.MODELS)
        assert "agent.code" in models_fields
        assert "agent.feedback" in models_fields
        assert "report" in models_fields
    
    def test_flatten_dict(self, config_service, sample_config):
        """Test flattening nested dictionary keys."""
        flat_keys = config_service._flatten_dict(sample_config)
        
        # Check that both simple and nested keys are included
        assert "data_dir" in flat_keys
        assert "agent.steps" in flat_keys
        assert "agent.code.model" in flat_keys
        assert "agent.search.max_debug_depth" in flat_keys
    
    @patch('services.config_service.OmegaConf')
    def test_get_current_config(self, mock_omegaconf, config_service, sample_config):
        """Test getting current configuration."""
        # Mock OmegaConf behavior
        mock_omegaconf.load.return_value = sample_config
        mock_omegaconf.to_container.return_value = sample_config
        
        result = config_service.get_current_config()
        assert result == sample_config
    
    def test_get_config_by_category(self, config_service, sample_config):
        """Test getting configuration by category."""
        with patch.object(config_service, 'get_current_config', return_value=sample_config):
            
            # Test project category
            project_config = config_service.get_config_by_category(ConfigCategory.PROJECT)
            assert "data_dir" in project_config
            assert "goal" in project_config
            assert "agent" not in project_config  # Should not include agent config
            
            # Test agent category
            agent_config = config_service.get_config_by_category(ConfigCategory.AGENT)
            assert "agent" in agent_config
            assert "data_dir" not in agent_config  # Should not include project config
    
    def test_get_categories(self, config_service):
        """Test getting configuration categories."""
        categories = config_service.get_categories()
        
        assert isinstance(categories, dict)
        assert "project" in categories
        assert "agent" in categories
        assert "models" in categories
        assert "execution" in categories
        
        # Check that descriptions are provided
        assert categories["project"] == "Project and Task Settings"
        assert categories["agent"] == "Agent Behavior Configuration"
    
    def test_get_default_config(self, config_service):
        """Test getting default configuration."""
        default_config = config_service._get_default_config()
        
        # Check that all required fields are present
        assert "data_dir" in default_config
        assert "agent" in default_config
        assert "exec" in default_config
        assert "report" in default_config
        
        # Check default values
        assert default_config["log_dir"] == "logs"
        assert default_config["workspace_dir"] == "workspaces"
        assert default_config["preprocess_data"] is True
        assert default_config["agent"]["steps"] == 20
        assert default_config["agent"]["k_fold_validation"] == 5
    
    def test_export_config_yaml(self, config_service, sample_config):
        """Test exporting configuration to YAML."""
        with patch.object(config_service, 'get_current_config', return_value=sample_config):
            yaml_output = config_service.export_config(ConfigExportFormat.YAML)
            
            assert isinstance(yaml_output, str)
            assert "data_dir:" in yaml_output
            assert "agent:" in yaml_output
            # Should be valid YAML format
            import yaml
            parsed = yaml.safe_load(yaml_output)
            assert parsed["data_dir"] == sample_config["data_dir"]
    
    def test_export_config_json(self, config_service, sample_config):
        """Test exporting configuration to JSON.""" 
        with patch.object(config_service, 'get_current_config', return_value=sample_config):
            json_output = config_service.export_config(ConfigExportFormat.JSON)
            
            assert isinstance(json_output, str)
            # Should be valid JSON format
            import json
            parsed = json.loads(json_output)
            assert parsed["data_dir"] == sample_config["data_dir"]
    
    def test_import_config_yaml(self, config_service):
        """Test importing configuration from YAML."""
        yaml_data = """
data_dir: /new/path
agent:
  steps: 30
  k_fold_validation: 3
"""
        with patch.object(config_service, 'validate_config') as mock_validate:
            mock_validate.return_value.valid = True
            mock_validate.return_value.errors = []
            
            with patch.object(config_service, '_save_aide_config'):
                result = config_service.import_config(yaml_data, merge=False, validate_only=True)
                
                assert result["data_dir"] == "/new/path"
                assert result["agent"]["steps"] == 30
                assert result["agent"]["k_fold_validation"] == 3
    
    def test_import_config_json(self, config_service):
        """Test importing configuration from JSON."""
        json_data = '{"data_dir": "/json/path", "agent": {"steps": 25}}'
        
        with patch.object(config_service, 'validate_config') as mock_validate:
            mock_validate.return_value.valid = True
            mock_validate.return_value.errors = []
            
            with patch.object(config_service, '_save_aide_config'):
                result = config_service.import_config(json_data, merge=False, validate_only=True)
                
                assert result["data_dir"] == "/json/path"
                assert result["agent"]["steps"] == 25
    
    def test_deep_merge(self, config_service):
        """Test deep merging of configurations."""
        base = {
            "a": 1,
            "b": {
                "c": 2,
                "d": 3
            }
        }
        
        override = {
            "b": {
                "d": 4,
                "e": 5
            },
            "f": 6
        }
        
        result = config_service._deep_merge(base, override)
        
        assert result["a"] == 1  # Preserved from base
        assert result["b"]["c"] == 2  # Preserved from base
        assert result["b"]["d"] == 4  # Overridden
        assert result["b"]["e"] == 5  # Added from override
        assert result["f"] == 6  # Added from override
    
    def test_remove_sensitive_fields(self, config_service):
        """Test removing sensitive fields from configuration."""
        config_with_sensitive = {
            "api_key": "secret123",
            "model": "gpt-4",
            "nested": {
                "password": "secret456",
                "normal_field": "value"
            }
        }
        
        cleaned = config_service._remove_sensitive_fields(config_with_sensitive)
        
        assert cleaned["api_key"] == "***REDACTED***"
        assert cleaned["model"] == "gpt-4"  # Not sensitive
        assert cleaned["nested"]["password"] == "***REDACTED***"
        assert cleaned["nested"]["normal_field"] == "value"  # Not sensitive


if __name__ == "__main__":
    pytest.main([__file__])