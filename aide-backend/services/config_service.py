"""
Configuration management service for AIDE ML.
Handles loading, saving, and manipulating configuration settings.
"""

import os
import sys
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from copy import deepcopy
import time

# Add the aide module to the path to import AIDE's config utilities
sys.path.append(str(Path(__file__).parent.parent.parent / "aide"))

from omegaconf import OmegaConf, DictConfig
from models.config_models import (
    ConfigSchema, 
    ConfigCategory, 
    ConfigUpdateRequest,
    ConfigExportFormat,
    ConfigImportRequest,
    ModelInfo,
    ModelProvider
)
from models.validation_models import ValidationReport, ValidationContext
from services.validation_service import ValidationService
from services.model_compatibility_service import ModelCompatibilityService


logger = logging.getLogger("aide")


class ConfigurationError(Exception):
    """Configuration-related errors."""
    pass


class ConfigService:
    """Service for managing AIDE ML configuration."""
    
    def __init__(self):
        # Try multiple possible paths for AIDE config
        possible_paths = [
            Path(__file__).parent.parent.parent / "aide" / "utils" / "config.yaml",  # Development
            Path("/app/aide/utils/config.yaml"),  # Docker container
            Path(__file__).parent.parent / "aide" / "utils" / "config.yaml",  # Alternative
        ]
        
        self.aide_config_path = None
        for path in possible_paths:
            if path.exists():
                self.aide_config_path = path
                break
        
        if self.aide_config_path is None:
            # Create a default config if none found
            default_config_path = Path(__file__).parent.parent / "aide_config.yaml"
            self._create_default_config(default_config_path)
            self.aide_config_path = default_config_path
        
        self.validation_service = ValidationService()
        self.model_service = ModelCompatibilityService()
        self._config_cache = None
        self._cache_timestamp = 0
    
    def _create_default_config(self, config_path: Path) -> None:
        """Create a default AIDE configuration file."""
        default_config = {
            'data_dir': None,
            'desc_file': None,
            'goal': None,
            'eval': None,
            'log_dir': 'logs',
            'workspace_dir': 'workspaces',
            'preprocess_data': True,
            'copy_data': True,
            'exp_name': None,
            'exec': {
                'timeout': 3600,
                'agent_file_name': 'runfile.py',
                'format_tb_ipython': False
            },
            'generate_report': True,
            'report': {
                'model': 'gpt-4-turbo',
                'temp': 1.0
            },
            'agent': {
                'steps': 20,
                'k_fold_validation': 5,
                'expose_prediction': False,
                'data_preview': True,
                'code': {
                    'model': 'gpt-4-turbo',
                    'temp': 0.5
                },
                'feedback': {
                    'model': 'gpt-4-turbo',
                    'temp': 0.5
                },
                'search': {
                    'max_debug_depth': 3,
                    'debug_prob': 0.5,
                    'num_drafts': 5
                }
            }
        }
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            import yaml
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
    
    def _load_aide_config(self) -> DictConfig:
        """Load configuration from AIDE's config.yaml file."""
        try:
            return OmegaConf.load(self.aide_config_path)
        except Exception as e:
            raise ConfigurationError(f"Failed to load AIDE config: {e}")
    
    def _save_aide_config(self, config: DictConfig) -> None:
        """Save configuration to AIDE's config.yaml file."""
        try:
            OmegaConf.save(config, self.aide_config_path)
            # Clear cache after saving
            self._config_cache = None
        except Exception as e:
            raise ConfigurationError(f"Failed to save AIDE config: {e}")
    
    def _get_cached_config(self) -> DictConfig:
        """Get cached configuration or load from file."""
        current_time = time.time()
        file_mtime = self.aide_config_path.stat().st_mtime
        
        # Check if cache is valid (file hasn't changed and cache is less than 30 seconds old)
        if (self._config_cache is not None and 
            self._cache_timestamp > file_mtime and 
            current_time - self._cache_timestamp < 30):
            return self._config_cache
        
        # Load fresh config and update cache
        self._config_cache = self._load_aide_config()
        self._cache_timestamp = current_time
        return self._config_cache
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get current configuration as dictionary."""
        try:
            config = self._get_cached_config()
            return OmegaConf.to_container(config, resolve=True)
        except Exception as e:
            logger.error(f"Error loading current config: {e}")
            raise ConfigurationError(f"Failed to load current configuration: {e}")
    
    def get_config_by_category(self, category: ConfigCategory) -> Dict[str, Any]:
        """Get configuration for specific category."""
        config = self.get_current_config()
        
        category_mapping = {
            ConfigCategory.PROJECT: ["data_dir", "desc_file", "goal", "eval", "log_dir", "workspace_dir", "preprocess_data", "copy_data", "exp_name"],
            ConfigCategory.AGENT: ["agent"],
            ConfigCategory.EXECUTION: ["exec"],
            ConfigCategory.MODELS: ["agent.code", "agent.feedback", "report"],
            ConfigCategory.SEARCH: ["agent.search"],
            ConfigCategory.REPORTING: ["generate_report", "report"]
        }
        
        if category not in category_mapping:
            raise ValueError(f"Unknown category: {category}")
        
        result = {}
        for field_path in category_mapping[category]:
            value = self._get_nested_value(config, field_path)
            if value is not None:
                self._set_nested_value(result, field_path, value)
        
        return result
    
    def _get_nested_value(self, config: Dict[str, Any], path: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _set_nested_value(self, config: Dict[str, Any], path: str, value: Any) -> None:
        """Set value in nested dictionary using dot notation."""
        keys = path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def update_config(self, updates: Dict[str, Any], category: Optional[ConfigCategory] = None) -> Dict[str, Any]:
        """Update configuration with new values."""
        try:
            # Load current config
            current_config = self._load_aide_config()
            
            # If category is specified, only update that category
            if category:
                # Validate that updates are appropriate for the category
                valid_fields = self._get_category_fields(category)
                for field_path in self._flatten_dict(updates):
                    if not any(field_path.startswith(vf) for vf in valid_fields):
                        raise ValueError(f"Field '{field_path}' is not valid for category '{category}'")
            
            # Apply updates
            updated_config = self._apply_updates(current_config, updates)
            
            # Validate the updated configuration
            validation_result = self.validate_config(OmegaConf.to_container(updated_config, resolve=True))
            if not validation_result.valid:
                error_messages = [error.message for error in validation_result.errors]
                raise ConfigurationError(f"Configuration validation failed: {'; '.join(error_messages)}")
            
            # Save the updated configuration
            self._save_aide_config(updated_config)
            
            return OmegaConf.to_container(updated_config, resolve=True)
            
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            raise ConfigurationError(f"Failed to update configuration: {e}")
    
    def _get_category_fields(self, category: ConfigCategory) -> List[str]:
        """Get list of field paths for a category."""
        category_mapping = {
            ConfigCategory.PROJECT: ["data_dir", "desc_file", "goal", "eval", "log_dir", "workspace_dir", "preprocess_data", "copy_data", "exp_name"],
            ConfigCategory.AGENT: ["agent"],
            ConfigCategory.EXECUTION: ["exec"],
            ConfigCategory.MODELS: ["agent.code", "agent.feedback", "report"],
            ConfigCategory.SEARCH: ["agent.search"],
            ConfigCategory.REPORTING: ["generate_report", "report"]
        }
        return category_mapping.get(category, [])
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = "", sep: str = ".") -> List[str]:
        """Get list of all field paths in a nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep))
            else:
                items.append(new_key)
        return items
    
    def _apply_updates(self, config: DictConfig, updates: Dict[str, Any]) -> DictConfig:
        """Apply updates to configuration."""
        # Convert updates to OmegaConf format
        updates_conf = OmegaConf.create(updates)
        
        # Merge with current config
        updated_config = OmegaConf.merge(config, updates_conf)
        
        return updated_config
    
    def validate_config(self, config: Dict[str, Any], context: Optional[ValidationContext] = None) -> ValidationReport:
        """Validate configuration against schema and rules."""
        if context is None:
            context = ValidationContext()
        
        return self.validation_service.validate_configuration(config, context)
    
    def reset_to_defaults(self) -> Dict[str, Any]:
        """Reset configuration to default values."""
        try:
            # Load the default schema
            default_config = self._get_default_config()
            
            # Convert to OmegaConf and save
            default_omegaconf = OmegaConf.create(default_config)
            self._save_aide_config(default_omegaconf)
            
            return default_config
            
        except Exception as e:
            logger.error(f"Error resetting config to defaults: {e}")
            raise ConfigurationError(f"Failed to reset configuration: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "data_dir": None,
            "desc_file": None,
            "goal": None,
            "eval": None,
            "log_dir": "logs",
            "workspace_dir": "workspaces",
            "preprocess_data": True,
            "copy_data": True,
            "exp_name": None,
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
    
    def export_config(self, format: ConfigExportFormat = ConfigExportFormat.YAML, include_sensitive: bool = False) -> str:
        """Export configuration to string format."""
        try:
            config = self.get_current_config()
            
            if not include_sensitive:
                # Remove sensitive fields (none in AIDE config currently, but prepared for future)
                config = self._remove_sensitive_fields(config)
            
            if format == ConfigExportFormat.YAML:
                return yaml.dump(config, default_flow_style=False, indent=2)
            elif format == ConfigExportFormat.JSON:
                return json.dumps(config, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting config: {e}")
            raise ConfigurationError(f"Failed to export configuration: {e}")
    
    def import_config(self, config_data: str, merge: bool = True, validate_only: bool = False) -> Dict[str, Any]:
        """Import configuration from string data."""
        try:
            # Parse the configuration data
            try:
                # Try YAML first
                imported_config = yaml.safe_load(config_data)
            except yaml.YAMLError:
                try:
                    # Try JSON if YAML fails
                    imported_config = json.loads(config_data)
                except json.JSONDecodeError as e:
                    raise ConfigurationError(f"Invalid configuration format: {e}")
            
            if not isinstance(imported_config, dict):
                raise ConfigurationError("Configuration must be a dictionary/object")
            
            # Validate the imported configuration
            validation_result = self.validate_config(imported_config)
            if not validation_result.valid:
                error_messages = [error.message for error in validation_result.errors]
                raise ConfigurationError(f"Imported configuration is invalid: {'; '.join(error_messages)}")
            
            if validate_only:
                return imported_config
            
            # Apply the configuration
            if merge:
                # Merge with existing configuration
                current_config = self.get_current_config()
                final_config = self._deep_merge(current_config, imported_config)
            else:
                # Replace existing configuration
                final_config = imported_config
            
            # Save the configuration
            final_omegaconf = OmegaConf.create(final_config)
            self._save_aide_config(final_omegaconf)
            
            return final_config
            
        except Exception as e:
            logger.error(f"Error importing config: {e}")
            if not isinstance(e, ConfigurationError):
                raise ConfigurationError(f"Failed to import configuration: {e}")
            raise
    
    def _remove_sensitive_fields(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive fields from configuration."""
        # Currently AIDE config doesn't store API keys directly,
        # but this method is prepared for future use
        cleaned_config = deepcopy(config)
        
        # List of sensitive field patterns
        sensitive_patterns = ["api_key", "secret", "token", "password"]
        
        def remove_sensitive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in list(obj.items()):
                    current_path = f"{path}.{key}" if path else key
                    if any(pattern in key.lower() for pattern in sensitive_patterns):
                        obj[key] = "***REDACTED***"
                    else:
                        remove_sensitive(value, current_path)
        
        remove_sensitive(cleaned_config)
        return cleaned_config
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = deepcopy(base)
        
        def merge_recursive(target, source):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    merge_recursive(target[key], value)
                else:
                    target[key] = value
        
        merge_recursive(result, override)
        return result
    
    def get_supported_models(self) -> List[ModelInfo]:
        """Get list of supported AI models."""
        return self.model_service.get_supported_models()
    
    def get_models_by_provider(self, provider: ModelProvider) -> List[ModelInfo]:
        """Get models for specific provider."""
        return self.model_service.get_models_by_provider(provider)
    
    def get_configuration_schema(self) -> Dict[str, Any]:
        """Get complete configuration schema for UI generation."""
        return self.validation_service.get_configuration_schema()
    
    def get_categories(self) -> Dict[str, str]:
        """Get configuration categories with descriptions."""
        return {
            "project": "Project and Task Settings",
            "agent": "Agent Behavior Configuration", 
            "execution": "Code Execution Settings",
            "models": "AI Model Configuration",
            "search": "Tree Search Parameters",
            "reporting": "Report Generation Settings"
        }