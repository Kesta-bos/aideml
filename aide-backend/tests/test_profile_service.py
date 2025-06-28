"""
Tests for ProfileService functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from services.profile_service import ProfileService, ProfileError
from services.storage_service import StorageService
from services.config_service import ConfigService
from models.profile_models import (
    ProfileCreateRequest,
    ProfileUpdateRequest,
    SearchProfilesRequest,
    UserAction
)
from models.config_models import ConfigValidationResult


class TestProfileService:
    """Test ProfileService operations."""
    
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
        return mock
    
    @pytest.fixture
    def profile_service(self, mock_storage, mock_config_service):
        """ProfileService with mocked dependencies."""
        service = ProfileService()
        service.storage = mock_storage
        service.config_service = mock_config_service
        return service
    
    def test_create_profile_success(self, profile_service, mock_storage):
        """Test successful profile creation."""
        # Arrange
        request = ProfileCreateRequest(
            name="test_profile",
            description="Test profile",
            copy_from_current=False,
            config_data={"agent": {"steps": 10}}
        )
        
        from models.profile_models import ConfigProfile
        from datetime import datetime
        
        expected_profile = ConfigProfile(
            id="test_id",
            name="test_profile",
            description="Test profile",
            config_data={"agent": {"steps": 10}},
            tags=[],
            is_default=False,
            is_template=False,
            is_active=False,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_storage.create_profile.return_value = expected_profile
        
        # Act
        result = profile_service.create_profile(request)
        
        # Assert
        assert result.name == "test_profile"
        assert result.config_data == {"agent": {"steps": 10}}
        mock_storage.create_profile.assert_called_once()
    
    def test_create_profile_invalid_config(self, profile_service, mock_config_service):
        """Test profile creation with invalid configuration."""
        # Arrange
        request = ProfileCreateRequest(
            name="invalid_profile",
            config_data={"invalid": "config"}
        )
        
        mock_config_service.validate_config.return_value = ConfigValidationResult(
            valid=False,
            errors=[Mock(message="Invalid configuration")],
            warnings=[]
        )
        
        # Act & Assert
        with pytest.raises(ProfileError, match="Invalid configuration"):
            profile_service.create_profile(request)
    
    def test_get_profile_success(self, profile_service, mock_storage):
        """Test successful profile retrieval."""
        # Arrange
        profile_id = "test_id"
        
        from models.profile_models import ConfigProfile
        from datetime import datetime
        
        expected_profile = ConfigProfile(
            id=profile_id,
            name="test_profile",
            config_data={"agent": {"steps": 10}},
            tags=[],
            is_default=False,
            is_template=False,
            is_active=False,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_storage.get_profile.return_value = expected_profile
        
        # Act
        result = profile_service.get_profile(profile_id)
        
        # Assert
        assert result.id == profile_id
        assert result.name == "test_profile"
        mock_storage.get_profile.assert_called_once_with(profile_id)
    
    def test_get_profile_not_found(self, profile_service, mock_storage):
        """Test profile retrieval when profile doesn't exist."""
        # Arrange
        profile_id = "nonexistent_id"
        mock_storage.get_profile.return_value = None
        
        # Act & Assert
        with pytest.raises(ProfileError, match="Profile nonexistent_id not found"):
            profile_service.get_profile(profile_id)
    
    def test_list_profiles(self, profile_service, mock_storage):
        """Test listing profiles."""
        # Arrange
        from models.profile_models import ConfigProfile
        from datetime import datetime
        
        profiles = [
            ConfigProfile(
                id="profile1",
                name="Profile 1",
                config_data={},
                tags=[],
                is_default=True,
                is_template=False,
                is_active=False,
                version=1,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            ConfigProfile(
                id="profile2",
                name="Profile 2",
                config_data={},
                tags=[],
                is_default=False,
                is_template=False,
                is_active=True,
                version=1,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        mock_storage.list_profiles.return_value = profiles
        
        # Act
        result = profile_service.list_profiles()
        
        # Assert
        assert result.total_count == 2
        assert result.default_profile_id == "profile1"
        assert result.active_profile_id == "profile2"
        assert len(result.profiles) == 2
    
    def test_update_profile_success(self, profile_service, mock_storage):
        """Test successful profile update."""
        # Arrange
        profile_id = "test_id"
        request = ProfileUpdateRequest(
            name="updated_name",
            config_data={"agent": {"steps": 15}}
        )
        
        from models.profile_models import ConfigProfile
        from datetime import datetime
        
        updated_profile = ConfigProfile(
            id=profile_id,
            name="updated_name",
            config_data={"agent": {"steps": 15}},
            tags=[],
            is_default=False,
            is_template=False,
            is_active=False,
            version=2,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_storage.update_profile.return_value = updated_profile
        
        # Act
        result = profile_service.update_profile(profile_id, request)
        
        # Assert
        assert result.name == "updated_name"
        assert result.version == 2
        mock_storage.update_profile.assert_called_once_with(profile_id, request)
    
    def test_delete_profile_success(self, profile_service, mock_storage):
        """Test successful profile deletion."""
        # Arrange
        profile_id = "test_id"
        
        from models.profile_models import ConfigProfile
        from datetime import datetime
        
        profile = ConfigProfile(
            id=profile_id,
            name="test_profile",
            config_data={},
            tags=[],
            is_default=False,
            is_template=False,
            is_active=False,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_storage.get_profile.return_value = profile
        mock_storage.delete_profile.return_value = True
        
        # Act
        result = profile_service.delete_profile(profile_id)
        
        # Assert
        assert result is True
        mock_storage.delete_profile.assert_called_once_with(profile_id)
    
    def test_activate_profile_success(self, profile_service, mock_storage, mock_config_service):
        """Test successful profile activation."""
        # Arrange
        profile_id = "test_id"
        
        from models.profile_models import ConfigProfile
        from datetime import datetime
        
        profile = ConfigProfile(
            id=profile_id,
            name="test_profile",
            config_data={"agent": {"steps": 25}},
            tags=[],
            is_default=False,
            is_template=False,
            is_active=True,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_storage.activate_profile.return_value = profile
        mock_config_service.update_config.return_value = {"agent": {"steps": 25}}
        
        # Act
        result = profile_service.activate_profile(profile_id)
        
        # Assert
        assert result["profile"].id == profile_id
        assert result["profile"].is_active is True
        assert "message" in result
        mock_storage.activate_profile.assert_called_once_with(profile_id)
        mock_config_service.update_config.assert_called_once_with({"agent": {"steps": 25}})
    
    def test_search_profiles(self, profile_service, mock_storage):
        """Test profile search functionality."""
        # Arrange
        request = SearchProfilesRequest(
            query="test",
            tags=["tag1"],
            page=1,
            limit=10
        )
        
        from models.profile_models import ConfigProfile
        from datetime import datetime
        
        profiles = [
            ConfigProfile(
                id="profile1",
                name="Test Profile",
                config_data={},
                tags=["tag1"],
                is_default=False,
                is_template=False,
                is_active=False,
                version=1,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        mock_storage.search_profiles.return_value = (profiles, 1)
        
        # Act
        result = profile_service.search_profiles(request)
        
        # Assert
        assert result.total_count == 1
        assert len(result.profiles) == 1
        assert result.profiles[0].name == "Test Profile"
        mock_storage.search_profiles.assert_called_once_with(request)


def test_profile_service_integration():
    """Integration test for ProfileService with real dependencies."""
    # This would be an integration test that uses real services
    # For now, we'll skip this as it requires a real database setup
    pass


if __name__ == "__main__":
    pytest.main([__file__])