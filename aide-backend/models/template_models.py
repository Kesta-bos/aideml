"""
Pydantic models for configuration templates.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TemplateCategory(str, Enum):
    """Template categories for organization."""
    QUICK_EXPERIMENT = "quick_experiment"
    COST_OPTIMIZED = "cost_optimized"
    COMPREHENSIVE_ANALYSIS = "comprehensive_analysis"
    PRODUCTION_READY = "production_ready"
    RESEARCH = "research"
    EDUCATIONAL = "educational"
    CUSTOM = "custom"


class TemplateComplexity(str, Enum):
    """Template complexity levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ConfigTemplate(BaseModel):
    """Configuration template model."""
    name: str = Field(..., description="Template identifier")
    display_name: str = Field(..., description="Human-readable template name")
    description: str = Field(..., description="Template description")
    category: TemplateCategory = Field(..., description="Template category")
    config_data: Dict[str, Any] = Field(..., description="Template configuration data")
    use_case: Optional[str] = Field(None, description="Specific use case description")
    estimated_cost: Optional[str] = Field(None, description="Estimated cost range")
    estimated_time: Optional[str] = Field(None, description="Estimated execution time")
    complexity: TemplateComplexity = Field(TemplateComplexity.BEGINNER, description="Template complexity level")
    prerequisites: List[str] = Field(default_factory=list, description="Required prerequisites")
    tags: List[str] = Field(default_factory=list, description="Template tags")
    is_builtin: bool = Field(False, description="Whether this is a built-in template")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('name')
    def validate_name(cls, v):
        """Validate template name."""
        if not v or not v.strip():
            raise ValueError("Template name cannot be empty")
        # Only allow alphanumeric, underscore, and hyphen
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Template name can only contain letters, numbers, underscores, and hyphens")
        return v.strip().lower()
    
    class Config:
        schema_extra = {
            "example": {
                "name": "quick_experiment",
                "display_name": "Quick Experiment",
                "description": "Fast configuration for rapid prototyping",
                "category": "quick_experiment",
                "config_data": {
                    "agent": {
                        "steps": 5,
                        "code": {"model": "gpt-3.5-turbo", "temp": 0.7}
                    }
                },
                "use_case": "Rapid prototyping and initial exploration",
                "estimated_cost": "$1-3",
                "estimated_time": "5-10 minutes",
                "complexity": "beginner",
                "tags": ["quick", "prototype", "beginner"]
            }
        }


class TemplateCreateRequest(BaseModel):
    """Request model for creating a custom template."""
    name: str = Field(..., description="Template identifier")
    display_name: str = Field(..., description="Human-readable template name")
    description: str = Field(..., description="Template description")
    category: TemplateCategory = Field(TemplateCategory.CUSTOM, description="Template category")
    config_data: Dict[str, Any] = Field(..., description="Template configuration data")
    use_case: Optional[str] = Field(None, description="Specific use case description")
    estimated_cost: Optional[str] = Field(None, description="Estimated cost range")
    estimated_time: Optional[str] = Field(None, description="Estimated execution time")
    complexity: TemplateComplexity = Field(TemplateComplexity.BEGINNER, description="Template complexity level")
    prerequisites: List[str] = Field(default_factory=list, description="Required prerequisites")
    tags: List[str] = Field(default_factory=list, description="Template tags")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "my_custom_template",
                "display_name": "My Custom Template",
                "description": "Custom template for specific use case",
                "category": "custom",
                "config_data": {"agent": {"steps": 15}},
                "use_case": "Specific analysis workflow",
                "tags": ["custom", "analysis"]
            }
        }


class TemplateUpdateRequest(BaseModel):
    """Request model for updating a template."""
    display_name: Optional[str] = Field(None, description="New display name")
    description: Optional[str] = Field(None, description="New description")
    category: Optional[TemplateCategory] = Field(None, description="New category")
    config_data: Optional[Dict[str, Any]] = Field(None, description="New configuration data")
    use_case: Optional[str] = Field(None, description="New use case description")
    estimated_cost: Optional[str] = Field(None, description="New estimated cost")
    estimated_time: Optional[str] = Field(None, description="New estimated time")
    complexity: Optional[TemplateComplexity] = Field(None, description="New complexity level")
    prerequisites: Optional[List[str]] = Field(None, description="New prerequisites")
    tags: Optional[List[str]] = Field(None, description="New tags")
    
    class Config:
        schema_extra = {
            "example": {
                "display_name": "Updated Template Name",
                "description": "Updated description",
                "tags": ["updated", "modified"]
            }
        }


class TemplateApplyRequest(BaseModel):
    """Request model for applying a template."""
    template_name: str = Field(..., description="Template name to apply")
    target_profile_id: Optional[str] = Field(None, description="Target profile ID (uses active if none)")
    merge_strategy: str = Field("replace", description="Merge strategy: replace, merge, overlay")
    create_backup: bool = Field(True, description="Create backup before applying")
    
    class Config:
        schema_extra = {
            "example": {
                "template_name": "quick_experiment",
                "merge_strategy": "replace",
                "create_backup": True
            }
        }


class TemplateSaveRequest(BaseModel):
    """Request model for saving current config as template."""
    name: str = Field(..., description="Template name")
    display_name: str = Field(..., description="Display name")
    description: str = Field(..., description="Template description")
    category: TemplateCategory = Field(TemplateCategory.CUSTOM, description="Template category")
    use_case: Optional[str] = Field(None, description="Use case description")
    complexity: TemplateComplexity = Field(TemplateComplexity.INTERMEDIATE, description="Complexity level")
    tags: List[str] = Field(default_factory=list, description="Template tags")
    source_profile_id: Optional[str] = Field(None, description="Source profile ID (uses active if none)")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "my_workflow_template",
                "display_name": "My Workflow Template",
                "description": "Template based on my current workflow",
                "category": "custom",
                "tags": ["workflow", "custom"]
            }
        }


class TemplateListResponse(BaseModel):
    """Response model for template listing."""
    templates: List[ConfigTemplate] = Field(..., description="List of templates")
    total_count: int = Field(..., description="Total number of templates")
    categories: List[str] = Field(..., description="Available categories")
    
    class Config:
        schema_extra = {
            "example": {
                "templates": [],
                "total_count": 8,
                "categories": ["quick_experiment", "cost_optimized", "comprehensive_analysis"]
            }
        }


class TemplateComparisonRequest(BaseModel):
    """Request model for comparing templates."""
    template_names: List[str] = Field(..., min_items=2, max_items=5, description="Template names to compare")
    comparison_fields: Optional[List[str]] = Field(None, description="Specific fields to compare")
    
    class Config:
        schema_extra = {
            "example": {
                "template_names": ["quick_experiment", "comprehensive_analysis"],
                "comparison_fields": ["agent.steps", "agent.code.model"]
            }
        }


class TemplateComparison(BaseModel):
    """Template comparison result."""
    template_name: str = Field(..., description="Template name")
    display_name: str = Field(..., description="Template display name")
    field_values: Dict[str, Any] = Field(..., description="Field values for comparison")
    
    class Config:
        schema_extra = {
            "example": {
                "template_name": "quick_experiment",
                "display_name": "Quick Experiment",
                "field_values": {"agent.steps": 5, "agent.code.model": "gpt-3.5-turbo"}
            }
        }


class TemplateComparisonResponse(BaseModel):
    """Response model for template comparison."""
    comparisons: List[TemplateComparison] = Field(..., description="Template comparisons")
    common_fields: List[str] = Field(..., description="Fields common to all templates")
    different_fields: List[str] = Field(..., description="Fields that differ between templates")
    
    class Config:
        schema_extra = {
            "example": {
                "comparisons": [],
                "common_fields": ["agent.code.temp"],
                "different_fields": ["agent.steps", "agent.code.model"]
            }
        }