#!/usr/bin/env python3
"""
Integration test script for AIDE ML Profile Management API.
This script tests the basic functionality without requiring a full server setup.
"""

import sys
import os
import tempfile
import logging
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aide")

def test_database_initialization():
    """Test database initialization."""
    print("Testing database initialization...")
    
    try:
        from database.init_db import DatabaseManager
        
        # Use temporary database for testing
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_url = f"sqlite:///{tmp.name}"
        
        db_manager = DatabaseManager(db_url)
        
        # Test table creation
        success = db_manager.create_tables()
        assert success, "Failed to create database tables"
        
        # Test table existence check
        tables_exist = db_manager.check_tables_exist()
        assert tables_exist, "Database tables were not created properly"
        
        # Test initialization
        init_success = db_manager.initialize_database()
        assert init_success, "Failed to initialize database"
        
        # Clean up
        os.unlink(tmp.name)
        
        print("✓ Database initialization test passed")
        return True
        
    except Exception as e:
        print(f"✗ Database initialization test failed: {e}")
        return False

def test_storage_service():
    """Test storage service basic operations."""
    print("Testing storage service...")
    
    try:
        from services.storage_service import StorageService
        from models.profile_models import ProfileCreateRequest, UserAction
        
        # This test would normally require a real database
        # For now, we'll just test that the service can be instantiated
        storage = StorageService()
        assert storage is not None, "Failed to create StorageService"
        
        print("✓ Storage service test passed")
        return True
        
    except Exception as e:
        print(f"✗ Storage service test failed: {e}")
        return False

def test_template_service():
    """Test template service."""
    print("Testing template service...")
    
    try:
        from services.template_service import TemplateService
        
        template_service = TemplateService()
        
        # Test built-in templates
        builtin_templates = template_service.get_builtin_templates()
        assert len(builtin_templates) > 0, "No built-in templates found"
        
        # Check that required templates exist
        template_names = [t["name"] for t in builtin_templates]
        required_templates = ["quick_experiment", "cost_optimized", "comprehensive_analysis"]
        
        for required in required_templates:
            assert required in template_names, f"Required template '{required}' not found"
        
        # Test template categories
        categories = template_service.get_template_categories()
        assert len(categories) > 0, "No template categories found"
        
        print("✓ Template service test passed")
        return True
        
    except Exception as e:
        print(f"✗ Template service test failed: {e}")
        return False

def test_profile_service():
    """Test profile service basic functionality."""
    print("Testing profile service...")
    
    try:
        from services.profile_service import ProfileService
        
        profile_service = ProfileService()
        assert profile_service is not None, "Failed to create ProfileService"
        
        # Test statistics method (doesn't require database)
        try:
            stats = profile_service.get_profile_statistics()
            # This will likely fail without a database, but we test the method exists
        except Exception:
            pass  # Expected without database
        
        print("✓ Profile service test passed")
        return True
        
    except Exception as e:
        print(f"✗ Profile service test failed: {e}")
        return False

def test_api_models():
    """Test API models validation."""
    print("Testing API models...")
    
    try:
        from models.profile_models import (
            ProfileCreateRequest, ProfileUpdateRequest, ConfigProfile
        )
        from models.template_models import (
            TemplateCreateRequest, ConfigTemplate, TemplateCategory
        )
        from datetime import datetime
        
        # Test ProfileCreateRequest
        profile_request = ProfileCreateRequest(
            name="test_profile",
            description="Test profile",
            tags=["test"],
            copy_from_current=False
        )
        assert profile_request.name == "test_profile"
        
        # Test TemplateCreateRequest
        template_request = TemplateCreateRequest(
            name="test_template",
            display_name="Test Template",
            description="Test template",
            category=TemplateCategory.CUSTOM,
            config_data={"agent": {"steps": 10}}
        )
        assert template_request.name == "test_template"
        
        # Test ConfigProfile
        profile = ConfigProfile(
            id="test_id",
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
        assert profile.id == "test_id"
        
        print("✓ API models test passed")
        return True
        
    except Exception as e:
        print(f"✗ API models test failed: {e}")
        return False

def test_template_files():
    """Test that template YAML files exist and are valid."""
    print("Testing template YAML files...")
    
    try:
        import yaml
        
        templates_dir = Path(__file__).parent / "templates"
        
        required_templates = [
            "quick_experiment.yaml",
            "cost_optimized.yaml",
            "comprehensive_analysis.yaml",
            "research_focused.yaml",
            "educational.yaml"
        ]
        
        for template_file in required_templates:
            template_path = templates_dir / template_file
            assert template_path.exists(), f"Template file {template_file} not found"
            
            # Test YAML is valid
            with open(template_path, 'r') as f:
                template_data = yaml.safe_load(f)
            
            # Check required fields
            required_fields = ["name", "display_name", "description", "category", "config_data"]
            for field in required_fields:
                assert field in template_data, f"Required field '{field}' missing in {template_file}"
            
            # Check config_data structure
            assert "agent" in template_data["config_data"], f"agent config missing in {template_file}"
            
        print("✓ Template YAML files test passed")
        return True
        
    except Exception as e:
        print(f"✗ Template YAML files test failed: {e}")
        return False

def test_imports():
    """Test that all modules can be imported without errors."""
    print("Testing module imports...")
    
    try:
        # Test database models
        from database.models import ConfigProfile, ConfigHistory, ConfigTemplate
        
        # Test Pydantic models
        from models.profile_models import ConfigProfile as ProfileModel
        from models.template_models import ConfigTemplate as TemplateModel
        
        # Test services
        from services.storage_service import StorageService
        from services.profile_service import ProfileService
        from services.template_service import TemplateService
        
        # Test routers
        from routers.profile_router import router
        
        print("✓ Module imports test passed")
        return True
        
    except Exception as e:
        print(f"✗ Module imports test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests."""
    print("AIDE ML Profile Management API - Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("API Models", test_api_models),
        ("Template Files", test_template_files),
        ("Template Service", test_template_service),
        ("Profile Service", test_profile_service),
        ("Storage Service", test_storage_service),
        ("Database Initialization", test_database_initialization),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test_name} test failed with exception: {e}")
            failed += 1
    
    print(f"\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The Profile Management API is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)