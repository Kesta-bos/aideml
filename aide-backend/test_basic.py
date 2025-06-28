#!/usr/bin/env python3
"""
Basic test script for AIDE ML Profile Management API components.
Tests components that don't require database dependencies.
"""

import sys
import yaml
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_api_models():
    """Test API models validation."""
    print("Testing API models...")
    
    try:
        from models.profile_models import (
            ProfileCreateRequest, ProfileUpdateRequest, ConfigProfile,
            UserAction, SearchProfilesRequest
        )
        from models.template_models import (
            TemplateCreateRequest, ConfigTemplate, TemplateCategory,
            TemplateComplexity, TemplateApplyRequest
        )
        from datetime import datetime
        
        # Test ProfileCreateRequest
        profile_request = ProfileCreateRequest(
            name="test_profile",
            description="Test profile",
            tags=["test", "example"],
            copy_from_current=False
        )
        assert profile_request.name == "test_profile"
        assert "test" in profile_request.tags
        
        # Test TemplateCreateRequest
        template_request = TemplateCreateRequest(
            name="test_template",
            display_name="Test Template",
            description="Test template description",
            category=TemplateCategory.CUSTOM,
            config_data={"agent": {"steps": 10, "code": {"model": "gpt-4-turbo"}}}
        )
        assert template_request.name == "test_template"
        assert template_request.category == TemplateCategory.CUSTOM
        
        # Test SearchProfilesRequest
        search_request = SearchProfilesRequest(
            query="test",
            tags=["example"],
            page=1,
            limit=10
        )
        assert search_request.query == "test"
        assert search_request.page == 1
        
        # Test TemplateApplyRequest
        apply_request = TemplateApplyRequest(
            template_name="quick_experiment",
            merge_strategy="replace",
            create_backup=True
        )
        assert apply_request.template_name == "quick_experiment"
        assert apply_request.create_backup is True
        
        print("✓ API models validation passed")
        return True
        
    except Exception as e:
        print(f"✗ API models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_files():
    """Test that template YAML files exist and have correct structure."""
    print("Testing template YAML files...")
    
    try:
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
            
            # Test YAML is valid and well-formed
            with open(template_path, 'r') as f:
                template_data = yaml.safe_load(f)
            
            # Check required top-level fields
            required_fields = ["name", "display_name", "description", "category", "config_data"]
            for field in required_fields:
                assert field in template_data, f"Required field '{field}' missing in {template_file}"
            
            # Check config_data structure
            config_data = template_data["config_data"]
            assert "agent" in config_data, f"agent config missing in {template_file}"
            
            agent_config = config_data["agent"]
            agent_required = ["steps", "code", "feedback", "search"]
            for field in agent_required:
                assert field in agent_config, f"agent.{field} missing in {template_file}"
            
            # Validate model specifications
            code_config = agent_config["code"]
            assert "model" in code_config, f"agent.code.model missing in {template_file}"
            assert "temp" in code_config, f"agent.code.temp missing in {template_file}"
            
            # Validate reasonable values
            assert 1 <= agent_config["steps"] <= 100, f"Invalid steps value in {template_file}"
            assert 0.0 <= code_config["temp"] <= 2.0, f"Invalid temperature in {template_file}"
            
            print(f"  ✓ {template_file} is valid")
        
        print("✓ All template YAML files are valid")
        return True
        
    except Exception as e:
        print(f"✗ Template YAML files test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_content():
    """Test template content for consistency and completeness."""
    print("Testing template content consistency...")
    
    try:
        templates_dir = Path(__file__).parent / "templates"
        
        templates = {}
        for template_file in templates_dir.glob("*.yaml"):
            with open(template_file, 'r') as f:
                template_data = yaml.safe_load(f)
                templates[template_data["name"]] = template_data
        
        # Test that we have the expected built-in templates
        expected_templates = [
            "quick_experiment",
            "cost_optimized", 
            "comprehensive_analysis",
            "research_focused",
            "educational"
        ]
        
        for expected in expected_templates:
            assert expected in templates, f"Missing expected template: {expected}"
        
        # Test template progression (steps should generally increase)
        quick_steps = templates["quick_experiment"]["config_data"]["agent"]["steps"]
        cost_steps = templates["cost_optimized"]["config_data"]["agent"]["steps"]
        comprehensive_steps = templates["comprehensive_analysis"]["config_data"]["agent"]["steps"]
        
        assert quick_steps < cost_steps < comprehensive_steps, \
            "Template complexity progression is incorrect"
        
        # Test model usage patterns
        quick_model = templates["quick_experiment"]["config_data"]["agent"]["code"]["model"]
        comprehensive_model = templates["comprehensive_analysis"]["config_data"]["agent"]["code"]["model"]
        
        # Quick should use more cost-effective model
        assert "gpt-3.5" in quick_model or "gpt-4" in comprehensive_model, \
            "Model selection doesn't follow expected cost patterns"
        
        # Test that all templates have reasonable timeout values
        for name, template in templates.items():
            if "exec" in template["config_data"]:
                timeout = template["config_data"]["exec"]["timeout"]
                assert 300 <= timeout <= 10800, f"Unreasonable timeout in {name}: {timeout}"
        
        print("✓ Template content consistency checks passed")
        return True
        
    except Exception as e:
        print(f"✗ Template content test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_validation():
    """Test configuration validation logic."""
    print("Testing configuration validation...")
    
    try:
        # Test that we can import config models without database dependencies
        from models.config_models import (
            ConfigSchema, StageConfigModel, SearchConfigModel, 
            AgentConfigModel, ExecConfigModel
        )
        
        # Test StageConfigModel validation
        stage_config = StageConfigModel(model="gpt-4-turbo", temp=0.5)
        assert stage_config.model == "gpt-4-turbo"
        assert stage_config.temp == 0.5
        
        # Test SearchConfigModel validation
        search_config = SearchConfigModel(
            max_debug_depth=3,
            debug_prob=0.5,
            num_drafts=5
        )
        assert search_config.max_debug_depth == 3
        assert 0.0 <= search_config.debug_prob <= 1.0
        
        # Test ExecConfigModel validation
        exec_config = ExecConfigModel(
            timeout=3600,
            agent_file_name="runfile.py"
        )
        assert exec_config.timeout == 3600
        
        # Test AgentConfigModel with nested configs
        agent_config = AgentConfigModel(
            steps=20,
            k_fold_validation=5,
            code=stage_config,
            feedback=stage_config,
            search=search_config
        )
        assert agent_config.steps == 20
        assert agent_config.code.model == "gpt-4-turbo"
        
        print("✓ Configuration validation passed")
        return True
        
    except Exception as e:
        print(f"✗ Configuration validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enum_definitions():
    """Test enum definitions and values."""
    print("Testing enum definitions...")
    
    try:
        from models.profile_models import UserAction
        from models.template_models import TemplateCategory, TemplateComplexity
        from models.config_models import ModelProvider, ConfigCategory
        
        # Test UserAction enum
        assert UserAction.MANUAL_EDIT == "manual_edit"
        assert UserAction.TEMPLATE_APPLY == "template_apply"
        assert UserAction.PROFILE_SWITCH == "profile_switch"
        
        # Test TemplateCategory enum
        assert TemplateCategory.QUICK_EXPERIMENT == "quick_experiment"
        assert TemplateCategory.COST_OPTIMIZED == "cost_optimized"
        assert TemplateCategory.COMPREHENSIVE_ANALYSIS == "comprehensive_analysis"
        
        # Test TemplateComplexity enum
        assert TemplateComplexity.BEGINNER == "beginner"
        assert TemplateComplexity.INTERMEDIATE == "intermediate"
        assert TemplateComplexity.ADVANCED == "advanced"
        assert TemplateComplexity.EXPERT == "expert"
        
        # Test ModelProvider enum
        assert ModelProvider.OPENAI == "openai"
        assert ModelProvider.ANTHROPIC == "anthropic"
        
        print("✓ Enum definitions test passed")
        return True
        
    except Exception as e:
        print(f"✗ Enum definitions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_structure():
    """Test that required files exist."""
    print("Testing file structure...")
    
    try:
        backend_dir = Path(__file__).parent
        
        # Check key directories exist
        required_dirs = [
            "models",
            "services", 
            "routers",
            "database",
            "templates",
            "tests",
            "docs"
        ]
        
        for dir_name in required_dirs:
            dir_path = backend_dir / dir_name
            assert dir_path.exists(), f"Required directory '{dir_name}' not found"
            assert dir_path.is_dir(), f"'{dir_name}' is not a directory"
        
        # Check key files exist
        required_files = [
            "main.py",
            "requirements.txt",
            "models/profile_models.py",
            "models/template_models.py",
            "services/profile_service.py",
            "services/template_service.py",
            "routers/profile_router.py",
            "database/models.py",
            "database/init_db.py"
        ]
        
        for file_path in required_files:
            full_path = backend_dir / file_path
            assert full_path.exists(), f"Required file '{file_path}' not found"
            assert full_path.is_file(), f"'{file_path}' is not a file"
        
        print("✓ File structure test passed")
        return True
        
    except Exception as e:
        print(f"✗ File structure test failed: {e}")
        return False

def main():
    """Run all basic tests."""
    print("AIDE ML Profile Management API - Basic Tests")
    print("=" * 60)
    print("Testing components that don't require database dependencies...\n")
    
    tests = [
        ("API Models", test_api_models),
        ("Template YAML Files", test_template_files),
        ("Template Content", test_template_content),
        ("Configuration Validation", test_config_validation),
        ("Enum Definitions", test_enum_definitions),
        ("File Structure", test_file_structure),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test_name} test failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All basic tests passed!")
        print("\nThe Profile Management API core components are working correctly.")
        print("To test full functionality, install SQLAlchemy and run the integration tests:")
        print("  pip install sqlalchemy==2.0.23")
        print("  python test_integration.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)