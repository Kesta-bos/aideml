"""
Validation models and schemas for AIDE ML configuration.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional, Union
from enum import Enum


class ValidationType(str, Enum):
    """Types of validation checks."""
    REQUIRED = "required"
    TYPE = "type"
    RANGE = "range"
    PATTERN = "pattern"
    DEPENDENCY = "dependency"
    FILE_EXISTS = "file_exists"
    DIRECTORY_EXISTS = "directory_exists"
    API_KEY = "api_key"
    MODEL_COMPATIBILITY = "model_compatibility"


class ValidationRule(BaseModel):
    """Single validation rule definition."""
    field_path: str = Field(..., description="Dot-notation path to field (e.g., 'agent.steps')")
    rule_type: ValidationType = Field(..., description="Type of validation rule")
    required: bool = Field(False, description="Whether field is required")
    min_value: Optional[Union[int, float]] = Field(None, description="Minimum numeric value")
    max_value: Optional[Union[int, float]] = Field(None, description="Maximum numeric value")
    pattern: Optional[str] = Field(None, description="Regex pattern for string validation")
    allowed_values: Optional[List[Any]] = Field(None, description="List of allowed values")
    depends_on: Optional[str] = Field(None, description="Field this rule depends on")
    error_message: str = Field(..., description="Custom error message")
    
    class Config:
        schema_extra = {
            "example": {
                "field_path": "agent.steps",
                "rule_type": "range",
                "min_value": 1,
                "max_value": 100,
                "error_message": "Agent steps must be between 1 and 100"
            }
        }


class FieldSchema(BaseModel):
    """Schema definition for a configuration field."""
    name: str = Field(..., description="Field name")
    type: str = Field(..., description="Field data type")
    default: Any = Field(None, description="Default value")
    description: str = Field(..., description="Field description")
    category: str = Field(..., description="Configuration category")
    required: bool = Field(False, description="Whether field is required")
    sensitive: bool = Field(False, description="Whether field contains sensitive data")
    validation_rules: List[ValidationRule] = Field(default_factory=list, description="Validation rules")
    ui_hints: Dict[str, Any] = Field(default_factory=dict, description="UI rendering hints")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "steps",
                "type": "integer",
                "default": 20,
                "description": "Number of improvement iterations to run",
                "category": "agent",
                "required": True,
                "sensitive": False,
                "validation_rules": [
                    {
                        "field_path": "agent.steps",
                        "rule_type": "range",
                        "min_value": 1,
                        "max_value": 100,
                        "error_message": "Steps must be between 1 and 100"
                    }
                ],
                "ui_hints": {
                    "widget": "slider",
                    "step": 1,
                    "marks": {10: "Fast", 20: "Default", 50: "Thorough"}
                }
            }
        }


class ConfigurationSchema(BaseModel):
    """Complete configuration schema with all fields and validation rules."""
    version: str = Field("1.0", description="Schema version")
    categories: Dict[str, str] = Field(..., description="Category definitions")
    fields: List[FieldSchema] = Field(..., description="All configuration fields")
    dependencies: List[Dict[str, Any]] = Field(default_factory=list, description="Field dependencies")
    
    class Config:
        schema_extra = {
            "example": {
                "version": "1.0",
                "categories": {
                    "project": "Project Settings",
                    "agent": "Agent Configuration",
                    "execution": "Execution Settings"
                },
                "fields": [
                    {
                        "name": "data_dir",
                        "type": "string",
                        "category": "project",
                        "required": True,
                        "description": "Path to task data directory"
                    }
                ],
                "dependencies": [
                    {
                        "field": "goal",
                        "depends_on": "desc_file",
                        "condition": "if desc_file is None, goal is required"
                    }
                ]
            }
        }


class ValidationContext(BaseModel):
    """Context information for validation."""
    check_file_existence: bool = Field(True, description="Check if files/directories exist")
    check_api_keys: bool = Field(False, description="Validate API keys against providers")
    check_model_compatibility: bool = Field(False, description="Check model-API key compatibility")
    available_models: List[str] = Field(default_factory=list, description="List of available models")
    api_key_mapping: Dict[str, str] = Field(default_factory=dict, description="Provider to API key mapping")
    
    class Config:
        schema_extra = {
            "example": {
                "check_file_existence": True,
                "check_api_keys": True,
                "check_model_compatibility": True,
                "available_models": ["gpt-4-turbo", "claude-3-sonnet"],
                "api_key_mapping": {
                    "openai": "sk-...",
                    "anthropic": "sk-ant-..."
                }
            }
        }


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationIssue(BaseModel):
    """Single validation issue."""
    field_path: str = Field(..., description="Path to the problematic field")
    severity: ValidationSeverity = Field(..., description="Issue severity")
    rule_type: ValidationType = Field(..., description="Type of validation that failed")
    message: str = Field(..., description="Human-readable error message")
    current_value: Any = Field(None, description="Current field value")
    suggested_value: Any = Field(None, description="Suggested correction")
    fix_action: Optional[str] = Field(None, description="Automated fix action")
    
    class Config:
        schema_extra = {
            "example": {
                "field_path": "agent.steps",
                "severity": "error",
                "rule_type": "range",
                "message": "Steps value 150 exceeds maximum allowed value of 100",
                "current_value": 150,
                "suggested_value": 100,
                "fix_action": "clamp_to_max"
            }
        }


class ValidationReport(BaseModel):
    """Complete validation report."""
    valid: bool = Field(..., description="Overall validation status")
    total_issues: int = Field(0, description="Total number of issues found")
    errors: List[ValidationIssue] = Field(default_factory=list, description="Error-level issues")
    warnings: List[ValidationIssue] = Field(default_factory=list, description="Warning-level issues")
    info: List[ValidationIssue] = Field(default_factory=list, description="Info-level issues")
    suggestions: List[str] = Field(default_factory=list, description="General improvement suggestions")
    validation_time: float = Field(0.0, description="Time taken for validation in seconds")
    
    @validator('total_issues', always=True)
    def calculate_total_issues(cls, v, values):
        errors = values.get('errors', [])
        warnings = values.get('warnings', [])
        info = values.get('info', [])
        return len(errors) + len(warnings) + len(info)
    
    @validator('valid', always=True)
    def calculate_valid_status(cls, v, values):
        errors = values.get('errors', [])
        return len(errors) == 0
    
    class Config:
        schema_extra = {
            "example": {
                "valid": False,
                "total_issues": 2,
                "errors": [
                    {
                        "field_path": "data_dir",
                        "severity": "error",
                        "rule_type": "required",
                        "message": "Data directory is required",
                        "current_value": None
                    }
                ],
                "warnings": [
                    {
                        "field_path": "agent.temp",
                        "severity": "warning",
                        "rule_type": "range",
                        "message": "Temperature value is high, may produce inconsistent results",
                        "current_value": 1.8
                    }
                ],
                "info": [],
                "suggestions": [
                    "Consider using cross-validation for better evaluation",
                    "Enable data preview to help the agent understand the dataset"
                ],
                "validation_time": 0.15
            }
        }