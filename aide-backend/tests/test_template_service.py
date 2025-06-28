"""
Tests for TemplateService functionality.
"""

import pytest
from unittest.mock import Mock, patch

from services.template_service import TemplateService, TemplateError
from services.storage_service import StorageService
from services.config_service import ConfigService
from models.template_models import (
    TemplateCreateRequest,
    TemplateApplyRequest,
    TemplateSaveRequest,
    TemplateComparisonRequest,
    TemplateCategory,
    TemplateComplexity
)
from models.config_models import ConfigValidationResult


class TestTemplateService:
    """Test TemplateService operations."""
    
    @pytest.fixture
    def mock_storage(self):
        """Mock storage service."""
        return Mock(spec=StorageService)
    
    @pytest.fixture
    def mock_config_service(self):
        """Mock config service."""
        mock = Mock(spec=ConfigService)
        mock.validate_config.return_value = ConfigValidationResult(valid=True, errors=[], warnings=[])
        mock.get_current_config.return_value = {"agent": {"steps": 20}}
        mock.update_config.return_value = {"agent": {"steps": 20}}
        return mock
    
    @pytest.fixture
    def template_service(self, mock_storage, mock_config_service):
        """TemplateService with mocked dependencies."""
        service = TemplateService()
        service.storage = mock_storage
        service.config_service = mock_config_service
        return service
    
    def test_get_builtin_templates(self, template_service):
        """Test getting built-in template definitions."""
        # Act
        templates = template_service.get_builtin_templates()
        
        # Assert
        assert len(templates) > 0
        assert any(t["name"] == "quick_experiment" for t in templates)
        assert any(t["name"] == "cost_optimized" for t in templates)
        assert any(t["name"] == "comprehensive_analysis" for t in templates)
        
        # Check structure of first template
        first_template = templates[0]
        required_keys = ["name", "display_name", "description", "category", "config_data"]
        for key in required_keys:
            assert key in first_template
    
    def test_create_template_success(self, template_service, mock_storage):
        """Test successful template creation."""
        # Arrange
        request = TemplateCreateRequest(
            name="custom_template",
            display_name="Custom Template",
            description="A custom template for testing",
            category=TemplateCategory.CUSTOM,
            config_data={"agent": {"steps": 15}},
            complexity=TemplateComplexity.INTERMEDIATE,
            tags=["custom", "test"]
        )
        
        from models.template_models import ConfigTemplate
        from datetime import datetime
        
        expected_template = ConfigTemplate(
            name="custom_template",
            display_name="Custom Template",
            description="A custom template for testing",
            category=TemplateCategory.CUSTOM,
            config_data={"agent": {"steps": 15}},
            complexity=TemplateComplexity.INTERMEDIATE,
            prerequisites=[],
            tags=["custom", "test"],
            is_builtin=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_storage.create_template.return_value = expected_template
        
        # Act
        result = template_service.create_template(request)
        
        # Assert
        assert result.name == "custom_template"
        assert result.display_name == "Custom Template"
        assert result.category == TemplateCategory.CUSTOM
        assert result.config_data == {"agent": {"steps": 15}}
        mock_storage.create_template.assert_called_once()
    
    def test_create_template_invalid_config(self, template_service, mock_config_service):
        """Test template creation with invalid configuration."""
        # Arrange
        request = TemplateCreateRequest(
            name="invalid_template",
            display_name="Invalid Template",
            description="Template with invalid config",
            category=TemplateCategory.CUSTOM,
            config_data={"invalid": "config"}
        )
        
        mock_config_service.validate_config.return_value = ConfigValidationResult(
            valid=False,
            errors=[Mock(message="Invalid configuration")],
            warnings=[]
        )
        
        # Act & Assert
        with pytest.raises(TemplateError, match="Invalid configuration"):
            template_service.create_template(request)
    
    def test_get_template_success(self, template_service, mock_storage):
        """Test successful template retrieval."""
        # Arrange
        template_name = "quick_experiment"
        
        from models.template_models import ConfigTemplate
        from datetime import datetime
        
        expected_template = ConfigTemplate(
            name=template_name,
            display_name="Quick Experiment",
            description="Fast configuration for rapid prototyping",
            category=TemplateCategory.QUICK_EXPERIMENT,
            config_data={"agent": {"steps": 5}},
            complexity=TemplateComplexity.BEGINNER,
            prerequisites=[],
            tags=["quick", "prototype"],
            is_builtin=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_storage.get_template.return_value = expected_template
        
        # Act
        result = template_service.get_template(template_name)
        
        # Assert
        assert result.name == template_name
        assert result.display_name == "Quick Experiment"
        assert result.is_builtin is True
        mock_storage.get_template.assert_called_once_with(template_name)
    
    def test_get_template_not_found(self, template_service, mock_storage):
        """Test template retrieval when template doesn't exist."""
        # Arrange
        template_name = "nonexistent_template"
        mock_storage.get_template.return_value = None
        
        # Act & Assert
        with pytest.raises(TemplateError, match="Template 'nonexistent_template' not found"):
            template_service.get_template(template_name)
    
    def test_list_templates(self, template_service, mock_storage):
        """Test listing templates."""
        # Arrange
        from models.template_models import ConfigTemplate
        from datetime import datetime
        
        templates = [
            ConfigTemplate(
                name="template1",
                display_name="Template 1",
                description="First template",
                category=TemplateCategory.QUICK_EXPERIMENT,
                config_data={},
                complexity=TemplateComplexity.BEGINNER,
                prerequisites=[],
                tags=[],
                is_builtin=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            ConfigTemplate(
                name="template2",
                display_name="Template 2",
                description="Second template",
                category=TemplateCategory.COST_OPTIMIZED,
                config_data={},
                complexity=TemplateComplexity.INTERMEDIATE,
                prerequisites=[],
                tags=[],
                is_builtin=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        mock_storage.list_templates.return_value = templates
        
        # Act
        result = template_service.list_templates()
        
        # Assert
        assert result.total_count == 2
        assert len(result.templates) == 2
        assert len(result.categories) == 2
        assert TemplateCategory.QUICK_EXPERIMENT.value in result.categories
        assert TemplateCategory.COST_OPTIMIZED.value in result.categories
    
    def test_apply_template_to_global_config(self, template_service, mock_storage, mock_config_service):
        """Test applying template to global configuration."""
        # Arrange
        request = TemplateApplyRequest(
            template_name="quick_experiment",
            merge_strategy="replace",
            create_backup=True
        )
        
        from models.template_models import ConfigTemplate
        from datetime import datetime
        
        template = ConfigTemplate(
            name="quick_experiment",
            display_name="Quick Experiment",
            description="Fast configuration",
            category=TemplateCategory.QUICK_EXPERIMENT,
            config_data={"agent": {"steps": 5}},
            complexity=TemplateComplexity.BEGINNER,
            prerequisites=[],
            tags=[],
            is_builtin=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_storage.get_template.return_value = template
        mock_storage.create_backup.return_value = "backup_123"
        mock_storage.add_history_entry.return_value = Mock()
        
        # Act
        result = template_service.apply_template(request)
        
        # Assert
        assert result["success"] is True
        assert result["template"].name == "quick_experiment"
        assert result["backup_id"] == "backup_123"
        assert "message" in result
        
        # Verify services were called
        mock_storage.get_template.assert_called_once_with("quick_experiment")
        mock_storage.create_backup.assert_called_once()
        mock_config_service.update_config.assert_called_once()
    
    def test_save_as_template_from_current_config(self, template_service, mock_storage, mock_config_service):
        """Test saving current configuration as template."""
        # Arrange
        request = TemplateSaveRequest(
            name="my_custom_template",
            display_name="My Custom Template",
            description="Template from current config",
            category=TemplateCategory.CUSTOM,
            tags=["custom"]
        )
        
        current_config = {"agent": {"steps": 20}}
        mock_config_service.get_current_config.return_value = current_config
        mock_storage.get_active_profile.return_value = None
        
        from models.template_models import ConfigTemplate
        from datetime import datetime
        
        expected_template = ConfigTemplate(
            name="my_custom_template",
            display_name="My Custom Template",
            description="Template from current config",
            category=TemplateCategory.CUSTOM,
            config_data=current_config,
            complexity=TemplateComplexity.BEGINNER,
            prerequisites=[],
            tags=["custom"],
            is_builtin=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_storage.create_template.return_value = expected_template
        
        # Act
        result = template_service.save_as_template(request)
        
        # Assert
        assert result.name == "my_custom_template"
        assert result.config_data == current_config
        mock_config_service.get_current_config.assert_called_once()
    
    def test_compare_templates(self, template_service, mock_storage):
        """Test template comparison functionality."""
        # Arrange
        request = TemplateComparisonRequest(
            template_names=["quick_experiment", "cost_optimized"]
        )
        
        from models.template_models import ConfigTemplate
        from datetime import datetime
        
        template1 = ConfigTemplate(
            name="quick_experiment",
            display_name="Quick Experiment",
            description="Fast config",
            category=TemplateCategory.QUICK_EXPERIMENT,
            config_data={"agent": {"steps": 5, "k_fold_validation": 3}},
            complexity=TemplateComplexity.BEGINNER,
            prerequisites=[],
            tags=[],
            is_builtin=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        template2 = ConfigTemplate(
            name="cost_optimized",
            display_name="Cost Optimized",
            description="Budget config",
            category=TemplateCategory.COST_OPTIMIZED,
            config_data={"agent": {"steps": 10, "k_fold_validation": 3}},
            complexity=TemplateComplexity.BEGINNER,
            prerequisites=[],
            tags=[],
            is_builtin=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_storage.get_template.side_effect = [template1, template2]
        
        # Act
        result = template_service.compare_templates(request)
        
        # Assert
        assert len(result.comparisons) == 2
        assert result.comparisons[0].template_name == "quick_experiment"
        assert result.comparisons[1].template_name == "cost_optimized"
        
        # Check that common and different fields are identified
        assert "agent.k_fold_validation" in result.common_fields
        assert "agent.steps" in result.different_fields
    
    def test_get_template_recommendations(self, template_service, mock_storage):
        """Test template recommendation functionality."""
        # Arrange
        from models.template_models import ConfigTemplate
        from datetime import datetime
        
        templates = [
            ConfigTemplate(
                name="quick_experiment",
                display_name="Quick Experiment",
                description="Fast prototyping",
                category=TemplateCategory.QUICK_EXPERIMENT,
                config_data={},
                use_case="Rapid prototyping, initial exploration",
                complexity=TemplateComplexity.BEGINNER,
                prerequisites=[],
                tags=["quick", "prototype"],
                is_builtin=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            ConfigTemplate(
                name="cost_optimized",
                display_name="Cost Optimized",
                description="Budget-friendly",
                category=TemplateCategory.COST_OPTIMIZED,
                config_data={},
                use_case="Budget-conscious projects",
                complexity=TemplateComplexity.BEGINNER,
                prerequisites=[],
                tags=["budget", "efficient"],
                is_builtin=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        mock_storage.list_templates.return_value = templates
        
        # Act
        result = template_service.get_template_recommendations(
            use_case="prototyping",
            complexity="beginner",
            budget="low"
        )
        
        # Assert
        assert len(result) > 0
        # Should recommend quick_experiment for prototyping and cost_optimized for low budget
        recommended_names = [t.name for t in result]
        assert "quick_experiment" in recommended_names or "cost_optimized" in recommended_names
    
    def test_export_template(self, template_service, mock_storage):
        """Test template export functionality."""
        # Arrange
        template_name = "quick_experiment"
        
        from models.template_models import ConfigTemplate
        from datetime import datetime
        
        template = ConfigTemplate(
            name=template_name,
            display_name="Quick Experiment",
            description="Fast configuration",
            category=TemplateCategory.QUICK_EXPERIMENT,
            config_data={"agent": {"steps": 5}},
            complexity=TemplateComplexity.BEGINNER,
            prerequisites=["Basic understanding"],
            tags=["quick", "prototype"],
            is_builtin=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_storage.get_template.return_value = template
        
        # Act
        yaml_result = template_service.export_template(template_name, "yaml")
        json_result = template_service.export_template(template_name, "json")
        
        # Assert
        assert isinstance(yaml_result, str)
        assert isinstance(json_result, str)
        assert "Quick Experiment" in yaml_result
        assert "Quick Experiment" in json_result
        assert template_name in yaml_result
        assert template_name in json_result
    
    def test_get_template_categories(self, template_service):
        """Test getting template categories."""
        # Act
        categories = template_service.get_template_categories()
        
        # Assert
        assert isinstance(categories, dict)
        assert len(categories) > 0
        assert "quick_experiment" in categories
        assert "cost_optimized" in categories
        assert "comprehensive_analysis" in categories
        
        # Check that values are descriptions
        for category, description in categories.items():
            assert isinstance(description, str)
            assert len(description) > 0


def test_template_service_integration():
    """Integration test for TemplateService with real dependencies."""
    # This would be an integration test that uses real services
    # For now, we'll skip this as it requires a real database setup
    pass


if __name__ == "__main__":
    pytest.main([__file__])