"""
Pydantic models for AIDE ML configuration management.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union, Generic, TypeVar
from pathlib import Path
from enum import Enum
from datetime import datetime

# Generic type for API responses  
T = TypeVar('T')


class ModelProvider(str, Enum):
    """Supported AI model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"


class ConfigCategory(str, Enum):
    """Configuration categories for organization."""
    PROJECT = "project"
    AGENT = "agent"
    EXECUTION = "execution"
    MODELS = "models"
    SEARCH = "search"
    REPORTING = "reporting"


class StageConfigModel(BaseModel):
    """LLM configuration for specific stages."""
    model: str = Field(..., description="Model name or identifier")
    temp: float = Field(0.5, ge=0.0, le=2.0, description="Temperature for model generation")
    
    class Config:
        schema_extra = {
            "example": {
                "model": "gpt-4-turbo",
                "temp": 0.5
            }
        }


class SearchConfigModel(BaseModel):
    """Tree search algorithm configuration."""
    max_debug_depth: int = Field(3, ge=1, le=10, description="Maximum depth for debugging attempts")
    debug_prob: float = Field(0.5, ge=0.0, le=1.0, description="Probability of debugging vs new attempt")
    num_drafts: int = Field(5, ge=1, le=20, description="Number of initial draft solutions")
    
    class Config:
        schema_extra = {
            "example": {
                "max_debug_depth": 3,
                "debug_prob": 0.5,
                "num_drafts": 5
            }
        }


class AgentConfigModel(BaseModel):
    """Agent behavior and workflow configuration."""
    steps: int = Field(20, ge=1, le=100, description="Number of improvement iterations")
    k_fold_validation: int = Field(5, ge=1, le=10, description="K-fold cross-validation splits")
    expose_prediction: bool = Field(False, description="Generate prediction function")
    data_preview: bool = Field(True, description="Provide data preview to agent")
    
    code: StageConfigModel = Field(..., description="LLM settings for code generation")
    feedback: StageConfigModel = Field(..., description="LLM settings for feedback evaluation")
    search: SearchConfigModel = Field(..., description="Tree search parameters")
    
    class Config:
        schema_extra = {
            "example": {
                "steps": 20,
                "k_fold_validation": 5,
                "expose_prediction": False,
                "data_preview": True,
                "code": {"model": "gpt-4-turbo", "temp": 0.5},
                "feedback": {"model": "gpt-4-turbo", "temp": 0.5},
                "search": {"max_debug_depth": 3, "debug_prob": 0.5, "num_drafts": 5}
            }
        }


class ExecConfigModel(BaseModel):
    """Code execution environment configuration."""
    timeout: int = Field(3600, ge=60, le=7200, description="Execution timeout in seconds")
    agent_file_name: str = Field("runfile.py", description="Name of the generated script file")
    format_tb_ipython: bool = Field(False, description="Format tracebacks with IPython style")
    
    class Config:
        schema_extra = {
            "example": {
                "timeout": 3600,
                "agent_file_name": "runfile.py",
                "format_tb_ipython": False
            }
        }


class ConfigSchema(BaseModel):
    """Complete AIDE ML configuration schema."""
    
    # Project settings
    data_dir: Optional[str] = Field(None, description="Path to task data directory")
    desc_file: Optional[str] = Field(None, description="Path to task description file")
    goal: Optional[str] = Field(None, description="Task goal description")
    eval: Optional[str] = Field(None, description="Evaluation criteria description")
    
    # Directory settings
    log_dir: str = Field("logs", description="Directory for experiment logs")
    workspace_dir: str = Field("workspaces", description="Directory for agent workspaces")
    
    # Data processing
    preprocess_data: bool = Field(True, description="Automatically unzip archives in data directory")
    copy_data: bool = Field(True, description="Copy data to workspace (vs symlink)")
    
    # Experiment settings
    exp_name: Optional[str] = Field(None, description="Experiment name (auto-generated if None)")
    
    # Component configurations
    exec: ExecConfigModel = Field(..., description="Code execution settings")
    generate_report: bool = Field(True, description="Generate final experiment report")
    report: StageConfigModel = Field(..., description="LLM settings for report generation")
    agent: AgentConfigModel = Field(..., description="Agent behavior configuration")
    
    @validator('data_dir')
    def validate_data_dir(cls, v):
        if v is not None:
            path = Path(v)
            if not path.exists():
                raise ValueError(f"Data directory does not exist: {v}")
        return v
    
    @validator('desc_file')
    def validate_desc_file(cls, v):
        if v is not None:
            path = Path(v)
            if not path.exists():
                raise ValueError(f"Description file does not exist: {v}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "data_dir": "/path/to/data",
                "goal": "Predict house prices using the given dataset",
                "eval": "Mean absolute error on test set",
                "log_dir": "logs",
                "workspace_dir": "workspaces",
                "preprocess_data": True,
                "copy_data": True,
                "exp_name": "house-price-prediction",
                "exec": {
                    "timeout": 3600,
                    "agent_file_name": "runfile.py",
                    "format_tb_ipython": False
                },
                "generate_report": True,
                "report": {"model": "gpt-4-turbo", "temp": 1.0},
                "agent": {
                    "steps": 20,
                    "k_fold_validation": 5,
                    "expose_prediction": False,
                    "data_preview": True,
                    "code": {"model": "gpt-4-turbo", "temp": 0.5},
                    "feedback": {"model": "gpt-4-turbo", "temp": 0.5},
                    "search": {"max_debug_depth": 3, "debug_prob": 0.5, "num_drafts": 5}
                }
            }
        }


class ConfigUpdateRequest(BaseModel):
    """Request model for updating configuration."""
    category: Optional[ConfigCategory] = Field(None, description="Specific category to update")
    config: Dict[str, Any] = Field(..., description="Configuration values to update")
    
    class Config:
        schema_extra = {
            "example": {
                "category": "agent",
                "config": {
                    "steps": 25,
                    "k_fold_validation": 3
                }
            }
        }


class ConfigValidationError(BaseModel):
    """Configuration validation error details."""
    field: str = Field(..., description="Field name that failed validation")
    message: str = Field(..., description="Error message")
    value: Any = Field(None, description="Invalid value that caused the error")
    
    class Config:
        schema_extra = {
            "example": {
                "field": "agent.steps",
                "message": "Steps must be between 1 and 100",
                "value": 150
            }
        }


class ConfigValidationResult(BaseModel):
    """Result of configuration validation."""
    valid: bool = Field(..., description="Whether configuration is valid")
    errors: List[ConfigValidationError] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    
    class Config:
        schema_extra = {
            "example": {
                "valid": False,
                "errors": [
                    {
                        "field": "agent.steps",
                        "message": "Steps must be between 1 and 100",
                        "value": 150
                    }
                ],
                "warnings": ["Using default temperature value"]
            }
        }


class ModelInfo(BaseModel):
    """Information about supported AI models."""
    name: str = Field(..., description="Model name or identifier")
    provider: ModelProvider = Field(..., description="Model provider")
    display_name: str = Field(..., description="Human-readable model name")
    description: str = Field(..., description="Model description")
    supports_function_calling: bool = Field(False, description="Whether model supports function calling")
    max_tokens: Optional[int] = Field(None, description="Maximum token limit")
    cost_per_1k_tokens: Optional[float] = Field(None, description="Cost per 1000 tokens (USD)")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "gpt-4-turbo",
                "provider": "openai",
                "display_name": "GPT-4 Turbo",
                "description": "Latest GPT-4 model with improved performance",
                "supports_function_calling": True,
                "max_tokens": 128000,
                "cost_per_1k_tokens": 0.01
            }
        }


class ModelCompatibilityCheck(BaseModel):
    """Model and API key compatibility check request."""
    provider: ModelProvider = Field(..., description="Model provider")
    model: str = Field(..., description="Model name")
    api_key: str = Field(..., description="API key to validate")
    
    class Config:
        schema_extra = {
            "example": {
                "provider": "openai",
                "model": "gpt-4-turbo",
                "api_key": "sk-..."
            }
        }


class ModelCompatibilityResult(BaseModel):
    """Result of model compatibility check."""
    compatible: bool = Field(..., description="Whether model and API key are compatible")
    model_available: bool = Field(..., description="Whether model is available with this key")
    api_key_valid: bool = Field(..., description="Whether API key is valid")
    message: str = Field(..., description="Detailed result message")
    estimated_cost: Optional[float] = Field(None, description="Estimated cost for typical experiment")
    
    class Config:
        schema_extra = {
            "example": {
                "compatible": True,
                "model_available": True,
                "api_key_valid": True,
                "message": "Model and API key are compatible",
                "estimated_cost": 2.50
            }
        }


class ConfigExportFormat(str, Enum):
    """Supported configuration export formats."""
    YAML = "yaml"
    JSON = "json"


class ConfigExportRequest(BaseModel):
    """Configuration export request."""
    format: ConfigExportFormat = Field(ConfigExportFormat.YAML, description="Export format")
    include_sensitive: bool = Field(False, description="Include sensitive data like API keys")
    
    class Config:
        schema_extra = {
            "example": {
                "format": "yaml",
                "include_sensitive": False
            }
        }


class ConfigImportRequest(BaseModel):
    """Configuration import request."""
    config_data: str = Field(..., description="Configuration data in YAML or JSON format")
    merge: bool = Field(True, description="Merge with existing config vs replace completely")
    validate_only: bool = Field(False, description="Only validate without applying changes")
    
    class Config:
        schema_extra = {
            "example": {
                "config_data": "agent:\n  steps: 25\n  k_fold_validation: 3",
                "merge": True,
                "validate_only": False
            }
        }


class ApiResponse(BaseModel, Generic[T]):
    """Generic API response wrapper."""
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[T] = Field(None, description="Response data")
    message: str = Field(..., description="Human-readable message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)