"""
Configuration management API router for AIDE ML.
Provides all configuration-related endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Any, List, Optional

from models.config_models import (
    ConfigSchema,
    ConfigCategory,
    ConfigUpdateRequest,
    ConfigValidationResult,
    ConfigExportRequest,
    ConfigImportRequest,
    ModelInfo,
    ModelProvider,
    ModelCompatibilityCheck,
    ModelCompatibilityResult,
    ConfigExportFormat
)
from models.validation_models import ValidationContext, ValidationReport
from models.config_models import ApiResponse
from services.config_service import ConfigService, ConfigurationError
from services.validation_service import ValidationService
from services.model_compatibility_service import ModelCompatibilityService


logger = logging.getLogger("aide")

# Initialize router
router = APIRouter(prefix="/api/config", tags=["configuration"])

# Initialize services
config_service = ConfigService()
validation_service = ValidationService()
model_service = ModelCompatibilityService()


@router.get("/schema")
async def get_config_schema():
    """Get complete configuration schema with validation rules and UI hints."""
    try:
        schema = config_service.get_configuration_schema()
        return ApiResponse(
            success=True,
            data=schema,
            message="Configuration schema retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting config schema: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get configuration schema: {e}")


@router.get("/categories")
async def get_config_categories():
    """Get configuration categories with descriptions."""
    try:
        categories = config_service.get_categories()
        return ApiResponse(
            success=True,
            data=categories,
            message="Configuration categories retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting config categories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get configuration categories: {e}")


@router.get("/models")
async def get_supported_models(provider: Optional[ModelProvider] = None):
    """Get supported AI models, optionally filtered by provider."""
    try:
        if provider:
            models = model_service.get_models_by_provider(provider)
        else:
            models = model_service.get_supported_models()
        
        return ApiResponse(
            success=True,
            data=[model.dict() for model in models],
            message=f"Retrieved {len(models)} supported models"
        )
    except Exception as e:
        logger.error(f"Error getting supported models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get supported models: {e}")


@router.get("/models/recommendations")
async def get_recommended_models(task_type: str = Query("general", description="Type of task: general, coding, feedback, reporting, budget")):
    """Get recommended models for specific task types."""
    try:
        models = model_service.get_recommended_models_for_task(task_type)
        return ApiResponse(
            success=True,
            data=[model.dict() for model in models],
            message=f"Retrieved {len(models)} recommended models for {task_type} tasks"
        )
    except Exception as e:
        logger.error(f"Error getting recommended models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommended models: {e}")


@router.get("")
async def get_current_config():
    """Get current configuration values."""
    try:
        config = config_service.get_current_config()
        return ApiResponse(
            success=True,
            data=config,
            message="Current configuration retrieved successfully"
        )
    except ConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting current config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get current configuration: {e}")


@router.get("/{category}")
async def get_config_category(category: ConfigCategory):
    """Get configuration for specific category."""
    try:
        config = config_service.get_config_by_category(category)
        return ApiResponse(
            success=True,
            data=config,
            message=f"Configuration for category '{category}' retrieved successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting config category {category}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get configuration category: {e}")


@router.put("")
async def update_full_config(updates: Dict[str, Any]):
    """Update complete configuration."""
    try:
        updated_config = config_service.update_config(updates)
        return ApiResponse(
            success=True,
            data=updated_config,
            message="Configuration updated successfully"
        )
    except ConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating full config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {e}")


@router.patch("/{category}")
async def update_config_category(category: ConfigCategory, updates: Dict[str, Any]):
    """Update specific category configuration."""
    try:
        updated_config = config_service.update_config(updates, category)
        return ApiResponse(
            success=True,
            data=updated_config,
            message=f"Configuration category '{category}' updated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating config category {category}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update configuration category: {e}")


@router.post("/validate")
async def validate_config(
    config: Dict[str, Any],
    check_files: bool = Query(True, description="Check if files and directories exist"),
    check_api_keys: bool = Query(False, description="Validate API keys"),
    check_models: bool = Query(False, description="Check model compatibility")
):
    """Validate configuration against schema and rules."""
    try:
        context = ValidationContext(
            check_file_existence=check_files,
            check_api_keys=check_api_keys,
            check_model_compatibility=check_models
        )
        
        validation_result = config_service.validate_config(config, context)
        
        return ApiResponse(
            success=validation_result.valid,
            data=validation_result.dict(),
            message="Configuration validation completed"
        )
    except Exception as e:
        logger.error(f"Error validating config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate configuration: {e}")


@router.post("/reset")
async def reset_config_to_defaults():
    """Reset configuration to default values."""
    try:
        default_config = config_service.reset_to_defaults()
        return ApiResponse(
            success=True,
            data=default_config,
            message="Configuration reset to defaults successfully"
        )
    except ConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error resetting config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset configuration: {e}")


@router.get("/export")
async def export_config(
    format: ConfigExportFormat = Query(ConfigExportFormat.YAML, description="Export format"),
    include_sensitive: bool = Query(False, description="Include sensitive data")
):
    """Export configuration to YAML or JSON format."""
    try:
        exported_config = config_service.export_config(format, include_sensitive)
        
        content_type = "application/x-yaml" if format == ConfigExportFormat.YAML else "application/json"
        filename = f"aide_config.{format.value}"
        
        from fastapi.responses import Response
        return Response(
            content=exported_config,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export configuration: {e}")


@router.post("/import")
async def import_config(request: ConfigImportRequest):
    """Import configuration from YAML or JSON data."""
    try:
        if request.validate_only:
            # Only validate, don't apply
            imported_config = config_service.import_config(
                request.config_data, 
                merge=request.merge,
                validate_only=True
            )
            return ApiResponse(
                success=True,
                data=imported_config,
                message="Configuration validated successfully (not applied)"
            )
        else:
            # Validate and apply
            imported_config = config_service.import_config(
                request.config_data,
                merge=request.merge,
                validate_only=False
            )
            return ApiResponse(
                success=True,
                data=imported_config,
                message="Configuration imported successfully"
            )
    except ConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error importing config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to import configuration: {e}")


@router.get("/defaults")
async def get_default_config():
    """Get default configuration values."""
    try:
        # Get defaults without applying them
        default_config = config_service._get_default_config()
        return ApiResponse(
            success=True,
            data=default_config,
            message="Default configuration retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting default config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get default configuration: {e}")


@router.post("/check-model-compatibility")
async def check_model_compatibility(request: ModelCompatibilityCheck):
    """Check compatibility between model and API key."""
    try:
        compatibility_result = await model_service.check_model_compatibility(request)
        
        return ApiResponse(
            success=compatibility_result.compatible,
            data=compatibility_result.dict(),
            message=compatibility_result.message
        )
    except Exception as e:
        logger.error(f"Error checking model compatibility: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check model compatibility: {e}")


@router.get("/model-requirements/{model_name}")
async def get_model_requirements(model_name: str):
    """Get API key requirements for a specific model."""
    try:
        model_info = model_service.get_model_info(model_name)
        if not model_info:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
        
        requirements = {
            "model": model_info.name,
            "provider": model_info.provider,
            "api_key_required": True,
            "api_key_env_var": f"{model_info.provider.upper()}_API_KEY",
            "supports_function_calling": model_info.supports_function_calling,
            "max_tokens": model_info.max_tokens,
            "estimated_cost_per_experiment": model_service._estimate_experiment_cost(model_info)
        }
        
        return ApiResponse(
            success=True,
            data=requirements,
            message=f"Requirements for model '{model_name}' retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model requirements: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model requirements: {e}")


@router.get("/validation-rules")
async def get_validation_rules():
    """Get all validation rules for configuration fields."""
    try:
        schema = config_service.get_configuration_schema()
        
        # Extract validation rules from schema
        validation_rules = {}
        for field in schema["fields"]:
            if field["validation_rules"]:
                validation_rules[field["name"]] = field["validation_rules"]
        
        return ApiResponse(
            success=True,
            data=validation_rules,
            message="Validation rules retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting validation rules: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get validation rules: {e}")


@router.get("/field-info/{field_path:path}")
async def get_field_info(field_path: str):
    """Get detailed information about a specific configuration field."""
    try:
        schema = config_service.get_configuration_schema()
        
        # Find the field in the schema
        field_info = None
        for field in schema["fields"]:
            if field["name"] == field_path:
                field_info = field
                break
        
        if not field_info:
            raise HTTPException(status_code=404, detail=f"Field '{field_path}' not found")
        
        return ApiResponse(
            success=True,
            data=field_info,
            message=f"Information for field '{field_path}' retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting field info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get field information: {e}")