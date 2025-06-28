"""
Pydantic models for configuration profiles and history management.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

from models.config_models import ConfigSchema


class ProfileStatus(str, Enum):
    """Profile status options."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class UserAction(str, Enum):
    """Types of user actions that can trigger configuration changes."""
    MANUAL_EDIT = "manual_edit"
    TEMPLATE_APPLY = "template_apply"
    IMPORT_CONFIG = "import_config"
    PROFILE_SWITCH = "profile_switch"
    ROLLBACK = "rollback"
    RESET_DEFAULTS = "reset_defaults"
    BULK_UPDATE = "bulk_update"


class ConfigProfile(BaseModel):
    """Configuration profile model."""
    id: str = Field(..., description="Unique profile identifier")
    name: str = Field(..., min_length=1, max_length=255, description="Profile name")
    description: Optional[str] = Field(None, description="Profile description")
    config_data: Dict[str, Any] = Field(..., description="Configuration data")
    tags: List[str] = Field(default_factory=list, description="Profile tags for organization")
    is_default: bool = Field(False, description="Whether this is the default profile")
    is_template: bool = Field(False, description="Whether this profile is a template")
    is_active: bool = Field(False, description="Whether this profile is currently active")
    version: int = Field(1, ge=1, description="Profile version number")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate profile name."""
        if not v.strip():
            raise ValueError("Profile name cannot be empty")
        if len(v.strip()) > 255:
            raise ValueError("Profile name too long")
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags list."""
        if v is None:
            return []
        # Remove duplicates and empty tags
        return list(set(tag.strip() for tag in v if tag and tag.strip()))
    
    class Config:
        schema_extra = {
            "example": {
                "id": "profile_123",
                "name": "Quick Analysis",
                "description": "Fast configuration for quick data analysis",
                "config_data": {
                    "agent": {
                        "steps": 10,
                        "code": {"model": "gpt-3.5-turbo", "temp": 0.7}
                    }
                },
                "tags": ["quick", "analysis", "gpt-3.5"],
                "is_default": False,
                "is_template": False,
                "is_active": True,
                "version": 1
            }
        }


class ConfigHistory(BaseModel):
    """Configuration change history model."""
    id: str = Field(..., description="Unique history entry identifier")
    profile_id: Optional[str] = Field(None, description="Associated profile ID (null for global changes)")
    config_data: Dict[str, Any] = Field(..., description="Configuration data at this point")
    change_description: str = Field(..., description="Description of the change")
    changed_fields: List[str] = Field(default_factory=list, description="List of changed field paths")
    user_action: UserAction = Field(..., description="Type of user action")
    previous_config: Optional[Dict[str, Any]] = Field(None, description="Previous configuration for rollback")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Change timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "history_456",
                "profile_id": "profile_123",
                "config_data": {"agent": {"steps": 15}},
                "change_description": "Updated agent steps from 10 to 15",
                "changed_fields": ["agent.steps"],
                "user_action": "manual_edit",
                "previous_config": {"agent": {"steps": 10}},
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class ProfileCreateRequest(BaseModel):
    """Request model for creating a new profile."""
    name: str = Field(..., min_length=1, max_length=255, description="Profile name")
    description: Optional[str] = Field(None, description="Profile description")
    config_data: Optional[Dict[str, Any]] = Field(None, description="Initial configuration data")
    tags: List[str] = Field(default_factory=list, description="Profile tags")
    copy_from_current: bool = Field(True, description="Copy configuration from current active profile")
    set_as_active: bool = Field(False, description="Set this profile as active after creation")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "My Custom Profile",
                "description": "Custom configuration for specific use case",
                "tags": ["custom", "experiment"],
                "copy_from_current": True,
                "set_as_active": False
            }
        }


class ProfileUpdateRequest(BaseModel):
    """Request model for updating a profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="New profile name")
    description: Optional[str] = Field(None, description="New profile description")
    config_data: Optional[Dict[str, Any]] = Field(None, description="New configuration data")
    tags: Optional[List[str]] = Field(None, description="New profile tags")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Updated Profile Name",
                "description": "Updated description",
                "tags": ["updated", "modified"]
            }
        }


class ProfileListResponse(BaseModel):
    """Response model for profile listing."""
    profiles: List[ConfigProfile] = Field(..., description="List of profiles")
    total_count: int = Field(..., description="Total number of profiles")
    active_profile_id: Optional[str] = Field(None, description="Currently active profile ID")
    default_profile_id: Optional[str] = Field(None, description="Default profile ID")
    
    class Config:
        schema_extra = {
            "example": {
                "profiles": [],
                "total_count": 5,
                "active_profile_id": "profile_123",
                "default_profile_id": "profile_456"
            }
        }


class HistoryListResponse(BaseModel):
    """Response model for history listing."""
    history: List[ConfigHistory] = Field(..., description="List of history entries")
    total_count: int = Field(..., description="Total number of history entries")
    profile_id: Optional[str] = Field(None, description="Profile ID if filtered by profile")
    
    class Config:
        schema_extra = {
            "example": {
                "history": [],
                "total_count": 25,
                "profile_id": "profile_123"
            }
        }


class ConfigDiff(BaseModel):
    """Configuration difference model."""
    field_path: str = Field(..., description="Path to the changed field")
    old_value: Any = Field(None, description="Previous value")
    new_value: Any = Field(None, description="New value")
    change_type: str = Field(..., description="Type of change: added, removed, modified")
    
    class Config:
        schema_extra = {
            "example": {
                "field_path": "agent.steps",
                "old_value": 10,
                "new_value": 15,
                "change_type": "modified"
            }
        }


class ConfigDiffResponse(BaseModel):
    """Response model for configuration diff."""
    differences: List[ConfigDiff] = Field(..., description="List of differences")
    summary: str = Field(..., description="Summary of changes")
    from_version: str = Field(..., description="Source version identifier")
    to_version: str = Field(..., description="Target version identifier")
    
    class Config:
        schema_extra = {
            "example": {
                "differences": [],
                "summary": "2 fields changed",
                "from_version": "v1",
                "to_version": "v2"
            }
        }


class RollbackRequest(BaseModel):
    """Request model for configuration rollback."""
    history_id: str = Field(..., description="History entry ID to rollback to")
    create_backup: bool = Field(True, description="Create backup before rollback")
    
    class Config:
        schema_extra = {
            "example": {
                "history_id": "history_456",
                "create_backup": True
            }
        }


class ProfileExportRequest(BaseModel):
    """Request model for profile export."""
    profile_ids: List[str] = Field(..., description="List of profile IDs to export")
    include_history: bool = Field(False, description="Include change history")
    format: str = Field("yaml", description="Export format (yaml, json)")
    
    class Config:
        schema_extra = {
            "example": {
                "profile_ids": ["profile_123", "profile_456"],
                "include_history": False,
                "format": "yaml"
            }
        }


class ProfileImportRequest(BaseModel):
    """Request model for profile import."""
    data: str = Field(..., description="Profile data in YAML or JSON format")
    merge_strategy: str = Field("create_new", description="Strategy: create_new, overwrite, merge")
    set_as_active: bool = Field(False, description="Set imported profile as active")
    
    class Config:
        schema_extra = {
            "example": {
                "data": "name: Imported Profile\nconfig_data:\n  agent:\n    steps: 20",
                "merge_strategy": "create_new",
                "set_as_active": False
            }
        }


class SearchProfilesRequest(BaseModel):
    """Request model for searching profiles."""
    query: Optional[str] = Field(None, description="Search query for name/description")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    category: Optional[str] = Field(None, description="Filter by category")
    is_template: Optional[bool] = Field(None, description="Filter by template status")
    date_from: Optional[datetime] = Field(None, description="Filter by creation date from")
    date_to: Optional[datetime] = Field(None, description="Filter by creation date to")
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "quick",
                "tags": ["analysis", "fast"],
                "is_template": False,
                "page": 1,
                "limit": 20
            }
        }