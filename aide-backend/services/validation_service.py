"""
Configuration validation service for AIDE ML.
Handles validation rules, schema checking, and error reporting.
"""

import re
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import time

from models.validation_models import (
    ValidationReport,
    ValidationIssue,
    ValidationSeverity,
    ValidationType,
    ValidationContext,
    ValidationRule,
    FieldSchema,
    ConfigurationSchema
)


logger = logging.getLogger("aide")


class ValidationService:
    """Service for validating AIDE ML configuration."""
    
    def __init__(self):
        self.schema = self._build_configuration_schema()
    
    def _build_configuration_schema(self) -> ConfigurationSchema:
        """Build the complete configuration schema with validation rules."""
        
        categories = {
            "project": "Project and Task Settings",
            "agent": "Agent Behavior Configuration",
            "execution": "Code Execution Settings",
            "models": "AI Model Configuration",
            "search": "Tree Search Parameters",
            "reporting": "Report Generation Settings"
        }
        
        fields = [
            # Project settings
            FieldSchema(
                name="data_dir",
                type="string",
                description="Path to the task data directory",
                category="project",
                required=False,  # Can be None, but if provided must exist
                validation_rules=[
                    ValidationRule(
                        field_path="data_dir",
                        rule_type=ValidationType.DIRECTORY_EXISTS,
                        error_message="Data directory must exist"
                    )
                ],
                ui_hints={"widget": "directory_picker"}
            ),
            FieldSchema(
                name="desc_file",
                type="string",
                description="Path to task description file",
                category="project",
                required=False,
                validation_rules=[
                    ValidationRule(
                        field_path="desc_file",
                        rule_type=ValidationType.FILE_EXISTS,
                        error_message="Description file must exist"
                    )
                ],
                ui_hints={"widget": "file_picker", "extensions": [".md", ".txt"]}
            ),
            FieldSchema(
                name="goal",
                type="string",
                description="Task goal description",
                category="project",
                required=False,  # Required only if desc_file is None
                validation_rules=[
                    ValidationRule(
                        field_path="goal",
                        rule_type=ValidationType.DEPENDENCY,
                        depends_on="desc_file",
                        error_message="Goal is required when description file is not provided"
                    )
                ],
                ui_hints={"widget": "textarea", "rows": 3}
            ),
            FieldSchema(
                name="eval",
                type="string",
                description="Evaluation criteria description",
                category="project",
                required=False,
                ui_hints={"widget": "textarea", "rows": 2}
            ),
            FieldSchema(
                name="log_dir",
                type="string",
                default="logs",
                description="Directory for experiment logs",
                category="project",
                required=True,
                ui_hints={"widget": "directory_picker"}
            ),
            FieldSchema(
                name="workspace_dir",
                type="string",
                default="workspaces",
                description="Directory for agent workspaces",
                category="project",
                required=True,
                ui_hints={"widget": "directory_picker"}
            ),
            FieldSchema(
                name="preprocess_data",
                type="boolean",
                default=True,
                description="Automatically unzip archives in data directory",
                category="project",
                required=True,
                ui_hints={"widget": "switch"}
            ),
            FieldSchema(
                name="copy_data",
                type="boolean",
                default=True,
                description="Copy data to workspace (vs symlink)",
                category="project",
                required=True,
                ui_hints={"widget": "switch"}
            ),
            FieldSchema(
                name="exp_name",
                type="string",
                description="Experiment name (auto-generated if not provided)",
                category="project",
                required=False,
                validation_rules=[
                    ValidationRule(
                        field_path="exp_name",
                        rule_type=ValidationType.PATTERN,
                        pattern=r"^[a-zA-Z0-9_-]+$",
                        error_message="Experiment name can only contain letters, numbers, hyphens, and underscores"
                    )
                ],
                ui_hints={"widget": "text", "placeholder": "auto-generated"}
            ),
            
            # Agent settings
            FieldSchema(
                name="agent.steps",
                type="integer",
                default=20,
                description="Number of improvement iterations",
                category="agent",
                required=True,
                validation_rules=[
                    ValidationRule(
                        field_path="agent.steps",
                        rule_type=ValidationType.RANGE,
                        min_value=1,
                        max_value=100,
                        error_message="Agent steps must be between 1 and 100"
                    )
                ],
                ui_hints={
                    "widget": "slider",
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "marks": {5: "Fast", 20: "Default", 50: "Thorough", 100: "Extensive"}
                }
            ),
            FieldSchema(
                name="agent.k_fold_validation",
                type="integer",
                default=5,
                description="K-fold cross-validation splits",
                category="agent",
                required=True,
                validation_rules=[
                    ValidationRule(
                        field_path="agent.k_fold_validation",
                        rule_type=ValidationType.RANGE,
                        min_value=1,
                        max_value=10,
                        error_message="K-fold validation must be between 1 and 10"
                    )
                ],
                ui_hints={
                    "widget": "select",
                    "options": [
                        {"value": 1, "label": "No CV (1)"},
                        {"value": 3, "label": "3-fold"},
                        {"value": 5, "label": "5-fold (default)"},
                        {"value": 10, "label": "10-fold"}
                    ]
                }
            ),
            FieldSchema(
                name="agent.expose_prediction",
                type="boolean",
                default=False,
                description="Generate prediction function",
                category="agent",
                required=True,
                ui_hints={"widget": "switch"}
            ),
            FieldSchema(
                name="agent.data_preview",
                type="boolean",
                default=True,
                description="Provide data preview to agent",
                category="agent",
                required=True,
                ui_hints={"widget": "switch"}
            ),
            
            # Model settings
            FieldSchema(
                name="agent.code.model",
                type="string",
                default="gpt-4-turbo",
                description="Model for code generation",
                category="models",
                required=True,
                validation_rules=[
                    ValidationRule(
                        field_path="agent.code.model",
                        rule_type=ValidationType.MODEL_COMPATIBILITY,
                        error_message="Model must be available with configured API keys"
                    )
                ],
                ui_hints={"widget": "model_select", "provider_group": "coding"}
            ),
            FieldSchema(
                name="agent.code.temp",
                type="number",
                default=0.5,
                description="Temperature for code generation",
                category="models",
                required=True,
                validation_rules=[
                    ValidationRule(
                        field_path="agent.code.temp",
                        rule_type=ValidationType.RANGE,
                        min_value=0.0,
                        max_value=2.0,
                        error_message="Temperature must be between 0.0 and 2.0"
                    )
                ],
                ui_hints={
                    "widget": "slider",
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "marks": {0.0: "Deterministic", 0.5: "Balanced", 1.0: "Creative", 2.0: "Very Creative"}
                }
            ),
            FieldSchema(
                name="agent.feedback.model",
                type="string",
                default="gpt-4-turbo",
                description="Model for feedback evaluation",
                category="models",
                required=True,
                validation_rules=[
                    ValidationRule(
                        field_path="agent.feedback.model",
                        rule_type=ValidationType.MODEL_COMPATIBILITY,
                        error_message="Model must be available with configured API keys"
                    )
                ],
                ui_hints={"widget": "model_select", "provider_group": "feedback"}
            ),
            FieldSchema(
                name="agent.feedback.temp",
                type="number",
                default=0.5,
                description="Temperature for feedback evaluation",
                category="models",
                required=True,
                validation_rules=[
                    ValidationRule(
                        field_path="agent.feedback.temp",
                        rule_type=ValidationType.RANGE,
                        min_value=0.0,
                        max_value=2.0,
                        error_message="Temperature must be between 0.0 and 2.0"
                    )
                ],
                ui_hints={
                    "widget": "slider",
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                }
            ),
            FieldSchema(
                name="report.model",
                type="string",
                default="gpt-4-turbo",
                description="Model for report generation",
                category="models",
                required=True,
                validation_rules=[
                    ValidationRule(
                        field_path="report.model",
                        rule_type=ValidationType.MODEL_COMPATIBILITY,
                        error_message="Model must be available with configured API keys"
                    )
                ],
                ui_hints={"widget": "model_select", "provider_group": "reporting"}
            ),
            FieldSchema(
                name="report.temp",
                type="number",
                default=1.0,
                description="Temperature for report generation",
                category="models",
                required=True,
                validation_rules=[
                    ValidationRule(
                        field_path="report.temp",
                        rule_type=ValidationType.RANGE,
                        min_value=0.0,
                        max_value=2.0,
                        error_message="Temperature must be between 0.0 and 2.0"
                    )
                ],
                ui_hints={
                    "widget": "slider",
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                }
            ),
            
            # Search parameters
            FieldSchema(
                name="agent.search.max_debug_depth",
                type="integer",
                default=3,
                description="Maximum depth for debugging attempts",
                category="search",
                required=True,
                validation_rules=[
                    ValidationRule(
                        field_path="agent.search.max_debug_depth",
                        rule_type=ValidationType.RANGE,
                        min_value=1,
                        max_value=10,
                        error_message="Max debug depth must be between 1 and 10"
                    )
                ],
                ui_hints={
                    "widget": "slider",
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "marks": {1: "Shallow", 3: "Default", 5: "Deep", 10: "Very Deep"}
                }
            ),
            FieldSchema(
                name="agent.search.debug_prob",
                type="number",
                default=0.5,
                description="Probability of debugging vs new attempt",
                category="search",
                required=True,
                validation_rules=[
                    ValidationRule(
                        field_path="agent.search.debug_prob",
                        rule_type=ValidationType.RANGE,
                        min_value=0.0,
                        max_value=1.0,
                        error_message="Debug probability must be between 0.0 and 1.0"
                    )
                ],
                ui_hints={
                    "widget": "slider",
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "marks": {0.0: "Never Debug", 0.5: "Balanced", 1.0: "Always Debug"}
                }
            ),
            FieldSchema(
                name="agent.search.num_drafts",
                type="integer",
                default=5,
                description="Number of initial draft solutions",
                category="search",
                required=True,
                validation_rules=[
                    ValidationRule(
                        field_path="agent.search.num_drafts",
                        rule_type=ValidationType.RANGE,
                        min_value=1,
                        max_value=20,
                        error_message="Number of drafts must be between 1 and 20"
                    )
                ],
                ui_hints={
                    "widget": "slider",
                    "min": 1,
                    "max": 20,
                    "step": 1,
                    "marks": {1: "Single", 5: "Default", 10: "Many", 20: "Exhaustive"}
                }
            ),
            
            # Execution settings
            FieldSchema(
                name="exec.timeout",
                type="integer",
                default=3600,
                description="Execution timeout in seconds",
                category="execution",
                required=True,
                validation_rules=[
                    ValidationRule(
                        field_path="exec.timeout",
                        rule_type=ValidationType.RANGE,
                        min_value=60,
                        max_value=7200,
                        error_message="Timeout must be between 60 and 7200 seconds"
                    )
                ],
                ui_hints={
                    "widget": "duration_picker",
                    "units": "seconds",
                    "presets": [
                        {"value": 300, "label": "5 minutes"},
                        {"value": 900, "label": "15 minutes"},
                        {"value": 1800, "label": "30 minutes"},
                        {"value": 3600, "label": "1 hour (default)"},
                        {"value": 7200, "label": "2 hours"}
                    ]
                }
            ),
            FieldSchema(
                name="exec.agent_file_name",
                type="string",
                default="runfile.py",
                description="Name of the generated script file",
                category="execution",
                required=True,
                validation_rules=[
                    ValidationRule(
                        field_path="exec.agent_file_name",
                        rule_type=ValidationType.PATTERN,
                        pattern=r"^[a-zA-Z0-9_-]+\.py$",
                        error_message="File name must be a valid Python file (*.py)"
                    )
                ],
                ui_hints={"widget": "text", "suffix": ".py"}
            ),
            FieldSchema(
                name="exec.format_tb_ipython",
                type="boolean",
                default=False,
                description="Format tracebacks with IPython style",
                category="execution",
                required=True,
                ui_hints={"widget": "switch"}
            ),
            
            # Reporting settings
            FieldSchema(
                name="generate_report",
                type="boolean",
                default=True,
                description="Generate final experiment report",
                category="reporting",
                required=True,
                ui_hints={"widget": "switch"}
            )
        ]
        
        dependencies = [
            {
                "field": "goal",
                "depends_on": "desc_file",
                "condition": "if desc_file is None, goal is required"
            },
            {
                "field": "eval",
                "depends_on": "goal",
                "condition": "eval is recommended when goal is provided"
            }
        ]
        
        return ConfigurationSchema(
            version="1.0",
            categories=categories,
            fields=fields,
            dependencies=dependencies
        )
    
    def validate_configuration(self, config: Dict[str, Any], context: ValidationContext) -> ValidationReport:
        """Validate a complete configuration."""
        start_time = time.time()
        
        errors = []
        warnings = []
        info = []
        suggestions = []
        
        # Validate each field according to its schema
        for field_schema in self.schema.fields:
            field_value = self._get_nested_value(config, field_schema.name)
            field_issues = self._validate_field(field_schema, field_value, config, context)
            
            for issue in field_issues:
                if issue.severity == ValidationSeverity.ERROR:
                    errors.append(issue)
                elif issue.severity == ValidationSeverity.WARNING:
                    warnings.append(issue)
                else:
                    info.append(issue)
        
        # Check dependencies
        dependency_issues = self._validate_dependencies(config)
        errors.extend([issue for issue in dependency_issues if issue.severity == ValidationSeverity.ERROR])
        warnings.extend([issue for issue in dependency_issues if issue.severity == ValidationSeverity.WARNING])
        
        # Generate suggestions
        suggestions = self._generate_suggestions(config, errors, warnings)
        
        validation_time = time.time() - start_time
        
        return ValidationReport(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            suggestions=suggestions,
            validation_time=validation_time
        )
    
    def _validate_field(self, field_schema: FieldSchema, value: Any, config: Dict[str, Any], context: ValidationContext) -> List[ValidationIssue]:
        """Validate a single field."""
        issues = []
        
        # Check if required field is missing
        if field_schema.required and value is None:
            issues.append(ValidationIssue(
                field_path=field_schema.name,
                severity=ValidationSeverity.ERROR,
                rule_type=ValidationType.REQUIRED,
                message=f"{field_schema.name} is required",
                current_value=value
            ))
            return issues  # Skip other validations if required field is missing
        
        # Skip validation if value is None and field is not required
        if value is None and not field_schema.required:
            return issues
        
        # Apply validation rules
        for rule in field_schema.validation_rules:
            issue = self._apply_validation_rule(rule, value, config, context)
            if issue:
                issues.append(issue)
        
        return issues
    
    def _apply_validation_rule(self, rule: ValidationRule, value: Any, config: Dict[str, Any], context: ValidationContext) -> Optional[ValidationIssue]:
        """Apply a single validation rule."""
        try:
            if rule.rule_type == ValidationType.RANGE:
                if isinstance(value, (int, float)):
                    if rule.min_value is not None and value < rule.min_value:
                        return ValidationIssue(
                            field_path=rule.field_path,
                            severity=ValidationSeverity.ERROR,
                            rule_type=rule.rule_type,
                            message=rule.error_message,
                            current_value=value,
                            suggested_value=rule.min_value
                        )
                    if rule.max_value is not None and value > rule.max_value:
                        return ValidationIssue(
                            field_path=rule.field_path,
                            severity=ValidationSeverity.ERROR,
                            rule_type=rule.rule_type,
                            message=rule.error_message,
                            current_value=value,
                            suggested_value=rule.max_value
                        )
            
            elif rule.rule_type == ValidationType.PATTERN:
                if isinstance(value, str) and rule.pattern:
                    if not re.match(rule.pattern, value):
                        return ValidationIssue(
                            field_path=rule.field_path,
                            severity=ValidationSeverity.ERROR,
                            rule_type=rule.rule_type,
                            message=rule.error_message,
                            current_value=value
                        )
            
            elif rule.rule_type == ValidationType.FILE_EXISTS:
                if context.check_file_existence and isinstance(value, str):
                    if not Path(value).exists():
                        return ValidationIssue(
                            field_path=rule.field_path,
                            severity=ValidationSeverity.ERROR,
                            rule_type=rule.rule_type,
                            message=rule.error_message,
                            current_value=value
                        )
            
            elif rule.rule_type == ValidationType.DIRECTORY_EXISTS:
                if context.check_file_existence and isinstance(value, str):
                    if not Path(value).is_dir():
                        return ValidationIssue(
                            field_path=rule.field_path,
                            severity=ValidationSeverity.ERROR,
                            rule_type=rule.rule_type,
                            message=rule.error_message,
                            current_value=value
                        )
            
            elif rule.rule_type == ValidationType.MODEL_COMPATIBILITY:
                if context.check_model_compatibility and isinstance(value, str):
                    if value not in context.available_models:
                        return ValidationIssue(
                            field_path=rule.field_path,
                            severity=ValidationSeverity.WARNING,
                            rule_type=rule.rule_type,
                            message=f"Model '{value}' may not be available with current API keys",
                            current_value=value
                        )
            
        except Exception as e:
            logger.error(f"Error applying validation rule {rule.rule_type} to {rule.field_path}: {e}")
            return ValidationIssue(
                field_path=rule.field_path,
                severity=ValidationSeverity.ERROR,
                rule_type=rule.rule_type,
                message=f"Validation error: {e}",
                current_value=value
            )
        
        return None
    
    def _validate_dependencies(self, config: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate field dependencies."""
        issues = []
        
        # Check goal/desc_file dependency
        goal = self._get_nested_value(config, "goal")
        desc_file = self._get_nested_value(config, "desc_file")
        
        if not goal and not desc_file:
            issues.append(ValidationIssue(
                field_path="goal",
                severity=ValidationSeverity.ERROR,
                rule_type=ValidationType.DEPENDENCY,
                message="Either 'goal' or 'desc_file' must be provided",
                current_value=None
            ))
        
        # Check eval recommendation
        eval_value = self._get_nested_value(config, "eval")
        if goal and not eval_value:
            issues.append(ValidationIssue(
                field_path="eval",
                severity=ValidationSeverity.WARNING,
                rule_type=ValidationType.DEPENDENCY,
                message="Evaluation criteria is recommended when goal is provided",
                current_value=None
            ))
        
        return issues
    
    def _generate_suggestions(self, config: Dict[str, Any], errors: List[ValidationIssue], warnings: List[ValidationIssue]) -> List[str]:
        """Generate helpful suggestions based on configuration."""
        suggestions = []
        
        # Suggest enabling data preview if disabled
        if not self._get_nested_value(config, "agent.data_preview", True):
            suggestions.append("Consider enabling data preview to help the agent understand your dataset")
        
        # Suggest reasonable step count
        steps = self._get_nested_value(config, "agent.steps", 20)
        if steps < 10:
            suggestions.append("Consider using at least 10 steps for better solution quality")
        elif steps > 50:
            suggestions.append("High step count may increase execution time significantly")
        
        # Suggest CV for better evaluation
        cv = self._get_nested_value(config, "agent.k_fold_validation", 5)
        if cv == 1:
            suggestions.append("Consider using cross-validation (k_fold_validation > 1) for more reliable evaluation")
        
        # Temperature suggestions
        code_temp = self._get_nested_value(config, "agent.code.temp", 0.5)
        if code_temp > 1.0:
            suggestions.append("High temperature for code generation may produce inconsistent results")
        
        return suggestions
    
    def _get_nested_value(self, config: Dict[str, Any], path: str, default: Any = None) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_configuration_schema(self) -> Dict[str, Any]:
        """Get the complete configuration schema as dictionary."""
        return {
            "version": self.schema.version,
            "categories": self.schema.categories,
            "fields": [field.dict() for field in self.schema.fields],
            "dependencies": self.schema.dependencies
        }