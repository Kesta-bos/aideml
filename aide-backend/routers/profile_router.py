"""
FastAPI router for configuration profile management.
Provides comprehensive API endpoints for profiles, templates, history, and backups.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from fastapi.responses import PlainTextResponse
from typing import List, Optional, Dict, Any
import logging

from services.profile_service import ProfileService, ProfileError
from services.template_service import TemplateService, TemplateError
from services.storage_service import StorageService, StorageError
from models.profile_models import (
    ConfigProfile,
    ConfigHistory,
    ProfileCreateRequest,
    ProfileUpdateRequest,
    ProfileListResponse,
    HistoryListResponse,
    SearchProfilesRequest,
    ConfigDiffResponse,
    RollbackRequest,
    ProfileExportRequest,
    ProfileImportRequest
)
from models.template_models import (
    ConfigTemplate,
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TemplateApplyRequest,
    TemplateSaveRequest,
    TemplateListResponse,
    TemplateComparisonRequest,
    TemplateComparisonResponse
)
from models.config_models import ApiResponse


logger = logging.getLogger("aide")

# Create router
router = APIRouter(prefix="/api/config", tags=["Configuration Profiles"])

# Service dependencies
def get_profile_service() -> ProfileService:
    return ProfileService()

def get_template_service() -> TemplateService:
    return TemplateService()

def get_storage_service() -> StorageService:
    return StorageService()


# Profile Management Endpoints

@router.post("/profiles")
async def create_profile(
    request: ProfileCreateRequest,
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Create a new configuration profile."""
    try:
        profile = profile_service.create_profile(request)
        return ApiResponse(
            success=True,
            data=profile,
            message=f"Profile '{profile.name}' created successfully"
        )
    except ProfileError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/profiles", )
async def list_profiles(
    include_templates: bool = Query(False, description="Include template profiles"),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """List all configuration profiles."""
    try:
        profiles_response = profile_service.list_profiles(include_templates)
        return ApiResponse(
            success=True,
            data=profiles_response,
            message=f"Retrieved {profiles_response.total_count} profiles"
        )
    except ProfileError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error listing profiles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/profiles/search", )
async def search_profiles(
    request: SearchProfilesRequest,
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Search profiles with filters and pagination."""
    try:
        profiles_response = profile_service.search_profiles(request)
        return ApiResponse(
            success=True,
            data=profiles_response,
            message=f"Found {profiles_response.total_count} matching profiles"
        )
    except ProfileError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error searching profiles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/profiles/{profile_id}", )
async def get_profile(
    profile_id: str = Path(..., description="Profile ID"),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get a specific profile by ID."""
    try:
        profile = profile_service.get_profile(profile_id)
        return ApiResponse(
            success=True,
            data=profile,
            message=f"Profile '{profile.name}' retrieved successfully"
        )
    except ProfileError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/profiles/{profile_id}", )
async def update_profile(
    profile_id: str = Path(..., description="Profile ID"),
    request: ProfileUpdateRequest = Body(...),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update an existing profile."""
    try:
        profile = profile_service.update_profile(profile_id, request)
        return ApiResponse(
            success=True,
            data=profile,
            message=f"Profile '{profile.name}' updated successfully"
        )
    except ProfileError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error updating profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/profiles/{profile_id}", )
async def delete_profile(
    profile_id: str = Path(..., description="Profile ID"),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Delete a profile."""
    try:
        success = profile_service.delete_profile(profile_id)
        if not success:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return ApiResponse(
            success=True,
            data={"id": profile_id, "status": "deleted"},
            message="Profile deleted successfully"
        )
    except ProfileError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error deleting profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/profiles/{profile_id}/activate", )
async def activate_profile(
    profile_id: str = Path(..., description="Profile ID"),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Activate a profile and apply its configuration."""
    try:
        result = profile_service.activate_profile(profile_id)
        return ApiResponse(
            success=True,
            data=result,
            message=result["message"]
        )
    except ProfileError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error activating profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/profiles/active/current", )
async def get_active_profile(
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get the currently active profile."""
    try:
        profile = profile_service.get_active_profile()
        return ApiResponse(
            success=True,
            data=profile,
            message="Active profile retrieved" if profile else "No active profile"
        )
    except ProfileError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting active profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/profiles/{profile_id}/set-default", )
async def set_default_profile(
    profile_id: str = Path(..., description="Profile ID"),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Set a profile as the default."""
    try:
        profile = profile_service.set_default_profile(profile_id)
        return ApiResponse(
            success=True,
            data=profile,
            message=f"Profile '{profile.name}' set as default"
        )
    except ProfileError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error setting default profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# History Management Endpoints

@router.get("/history", )
async def get_global_history(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of entries"),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get global configuration change history."""
    try:
        history_response = profile_service.get_global_history(limit)
        return ApiResponse(
            success=True,
            data=history_response,
            message=f"Retrieved {history_response.total_count} history entries"
        )
    except ProfileError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting global history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/profiles/{profile_id}/history", )
async def get_profile_history(
    profile_id: str = Path(..., description="Profile ID"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of entries"),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get history for a specific profile."""
    try:
        history_response = profile_service.get_profile_history(profile_id, limit)
        return ApiResponse(
            success=True,
            data=history_response,
            message=f"Retrieved {history_response.total_count} history entries for profile"
        )
    except ProfileError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting profile history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/rollback", )
async def rollback_configuration(
    request: RollbackRequest,
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Rollback configuration to a specific history entry."""
    try:
        result = profile_service.rollback_to_version(request)
        return ApiResponse(
            success=True,
            data=result,
            message=result["message"]
        )
    except ProfileError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during rollback: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/diff/profiles/{profile_id_1}/{profile_id_2}", )
async def compare_profiles(
    profile_id_1: str = Path(..., description="First profile ID"),
    profile_id_2: str = Path(..., description="Second profile ID"),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Compare configurations between two profiles."""
    try:
        diff_response = profile_service.compare_profiles(profile_id_1, profile_id_2)
        return ApiResponse(
            success=True,
            data=diff_response,
            message=diff_response.summary
        )
    except ProfileError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error comparing profiles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/diff/history/{history_id_1}/{history_id_2}", )
async def compare_history_entries(
    history_id_1: str = Path(..., description="First history entry ID"),
    history_id_2: str = Path(..., description="Second history entry ID"),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Compare configurations between two history entries."""
    try:
        diff_response = profile_service.compare_with_history(history_id_1, history_id_2)
        return ApiResponse(
            success=True,
            data=diff_response,
            message=diff_response.summary
        )
    except ProfileError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error comparing history entries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Template Management Endpoints

@router.get("/templates", )
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    template_service: TemplateService = Depends(get_template_service)
):
    """List all configuration templates."""
    try:
        templates_response = template_service.list_templates(category)
        return ApiResponse(
            success=True,
            data=templates_response,
            message=f"Retrieved {templates_response.total_count} templates"
        )
    except TemplateError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error listing templates: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/templates/{template_name}", )
async def get_template(
    template_name: str = Path(..., description="Template name"),
    template_service: TemplateService = Depends(get_template_service)
):
    """Get a specific template by name."""
    try:
        template = template_service.get_template(template_name)
        return ApiResponse(
            success=True,
            data=template,
            message=f"Template '{template.display_name}' retrieved successfully"
        )
    except TemplateError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting template: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/templates", )
async def create_custom_template(
    request: TemplateCreateRequest,
    template_service: TemplateService = Depends(get_template_service)
):
    """Create a new custom template."""
    try:
        template = template_service.create_template(request)
        return ApiResponse(
            success=True,
            data=template,
            message=f"Custom template '{template.display_name}' created successfully"
        )
    except TemplateError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating template: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/templates/{template_name}", )
async def delete_template(
    template_name: str = Path(..., description="Template name"),
    template_service: TemplateService = Depends(get_template_service)
):
    """Delete a custom template."""
    try:
        success = template_service.delete_template(template_name)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return ApiResponse(
            success=True,
            data={"name": template_name, "status": "deleted"},
            message="Template deleted successfully"
        )
    except TemplateError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error deleting template: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/templates/{template_name}/apply", )
async def apply_template(
    template_name: str = Path(..., description="Template name"),
    request: TemplateApplyRequest = Body(...),
    template_service: TemplateService = Depends(get_template_service)
):
    """Apply a template to current configuration or specific profile."""
    try:
        # Set template name from path
        request.template_name = template_name
        result = template_service.apply_template(request)
        return ApiResponse(
            success=True,
            data=result,
            message=result["message"]
        )
    except TemplateError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error applying template: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/templates/save-current", )
async def save_current_as_template(
    request: TemplateSaveRequest,
    template_service: TemplateService = Depends(get_template_service)
):
    """Save current configuration as a new template."""
    try:
        template = template_service.save_as_template(request)
        return ApiResponse(
            success=True,
            data=template,
            message=f"Current configuration saved as template '{template.display_name}'"
        )
    except TemplateError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error saving template: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/templates/compare", )
async def compare_templates(
    request: TemplateComparisonRequest,
    template_service: TemplateService = Depends(get_template_service)
):
    """Compare configurations between multiple templates."""
    try:
        comparison_response = template_service.compare_templates(request)
        return ApiResponse(
            success=True,
            data=comparison_response,
            message=f"Compared {len(request.template_names)} templates"
        )
    except TemplateError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error comparing templates: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/templates/{template_name}/export", response_class=PlainTextResponse)
async def export_template(
    template_name: str = Path(..., description="Template name"),
    format: str = Query("yaml", regex="^(yaml|json)$", description="Export format"),
    template_service: TemplateService = Depends(get_template_service)
):
    """Export a template to YAML or JSON format."""
    try:
        export_data = template_service.export_template(template_name, format)
        media_type = "application/x-yaml" if format == "yaml" else "application/json"
        return PlainTextResponse(content=export_data, media_type=media_type)
    except TemplateError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error exporting template: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Backup and Restore Endpoints

@router.post("/backup", )
async def create_backup(
    name: str = Body(..., embed=True, description="Backup name"),
    description: Optional[str] = Body(None, embed=True, description="Backup description"),
    storage_service: StorageService = Depends(get_storage_service)
):
    """Create a complete configuration backup."""
    try:
        backup_id = storage_service.create_backup(name, description)
        return ApiResponse(
            success=True,
            data={"backup_id": backup_id, "name": name},
            message="Backup created successfully"
        )
    except StorageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating backup: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/backups", )
async def list_backups(
    storage_service: StorageService = Depends(get_storage_service)
):
    """List all available backups."""
    try:
        backups = storage_service.list_backups()
        return ApiResponse(
            success=True,
            data=backups,
            message=f"Retrieved {len(backups)} backups"
        )
    except StorageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error listing backups: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/restore/{backup_id}", )
async def restore_backup(
    backup_id: str = Path(..., description="Backup ID"),
    storage_service: StorageService = Depends(get_storage_service)
):
    """Restore configuration from backup."""
    try:
        success = storage_service.restore_backup(backup_id)
        if not success:
            raise HTTPException(status_code=404, detail="Backup not found")
        
        return ApiResponse(
            success=True,
            data={"backup_id": backup_id, "status": "restored"},
            message="Configuration restored from backup successfully"
        )
    except StorageError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error restoring backup: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Import/Export Endpoints

@router.post("/export", response_class=PlainTextResponse)
async def export_profiles(
    request: ProfileExportRequest,
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Export profiles to YAML or JSON format."""
    try:
        export_data = profile_service.export_profiles(request)
        media_type = "application/x-yaml" if request.format == "yaml" else "application/json"
        return PlainTextResponse(content=export_data, media_type=media_type)
    except ProfileError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error exporting profiles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/import", )
async def import_profiles(
    request: ProfileImportRequest,
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Import profiles from YAML or JSON data."""
    try:
        imported_profiles = profile_service.import_profiles(request)
        return ApiResponse(
            success=True,
            data=imported_profiles,
            message=f"Successfully imported {len(imported_profiles)} profiles"
        )
    except ProfileError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error importing profiles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Utility Endpoints

@router.post("/sync", )
async def sync_current_config(
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Sync current AIDE configuration with active profile."""
    try:
        result = profile_service.sync_current_config()
        return ApiResponse(
            success=True,
            data={"status": "synced", "message": result or "No changes needed"},
            message=result or "Configuration is already in sync"
        )
    except ProfileError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error syncing configuration: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/statistics", )
async def get_profile_statistics(
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get statistics about profiles and usage."""
    try:
        stats = profile_service.get_profile_statistics()
        return ApiResponse(
            success=True,
            data=stats,
            message="Profile statistics retrieved successfully"
        )
    except ProfileError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/cleanup", )
async def cleanup_old_data(
    retention_days: int = Body(30, embed=True, ge=1, le=365, description="Retention period in days"),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Clean up old profile data and history."""
    try:
        cleanup_result = profile_service.cleanup_old_data(retention_days)
        return ApiResponse(
            success=True,
            data=cleanup_result,
            message=f"Cleaned up old data (retention: {retention_days} days)"
        )
    except ProfileError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during cleanup: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/template-categories", )
async def get_template_categories(
    template_service: TemplateService = Depends(get_template_service)
):
    """Get available template categories with descriptions."""
    try:
        categories = template_service.get_template_categories()
        return ApiResponse(
            success=True,
            data=categories,
            message="Template categories retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting template categories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/template-recommendations", )
async def get_template_recommendations(
    use_case: Optional[str] = Query(None, description="Use case description"),
    complexity: Optional[str] = Query(None, description="Complexity level"),
    budget: Optional[str] = Query(None, description="Budget level (low/medium/high)"),
    template_service: TemplateService = Depends(get_template_service)
):
    """Get template recommendations based on criteria."""
    try:
        recommendations = template_service.get_template_recommendations(use_case, complexity, budget)
        return ApiResponse(
            success=True,
            data=recommendations,
            message=f"Found {len(recommendations)} template recommendations"
        )
    except TemplateError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")