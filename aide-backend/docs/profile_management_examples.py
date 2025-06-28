"""
AIDE ML Profile Management API Examples

This file contains practical examples of how to use the Profile Management API
for common tasks and workflows.
"""

import requests
import json
import yaml
from typing import Dict, List, Optional


class AIDEProfileClient:
    """Client for AIDE ML Profile Management API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/config"
    
    def create_profile(self, name: str, description: str = None, 
                      config_data: Dict = None, tags: List[str] = None,
                      copy_from_current: bool = True, set_as_active: bool = False) -> Dict:
        """Create a new configuration profile."""
        data = {
            "name": name,
            "description": description,
            "tags": tags or [],
            "copy_from_current": copy_from_current,
            "set_as_active": set_as_active
        }
        
        if config_data:
            data["config_data"] = config_data
        
        response = requests.post(f"{self.api_base}/profiles", json=data)
        response.raise_for_status()
        return response.json()
    
    def list_profiles(self, include_templates: bool = False) -> Dict:
        """List all configuration profiles."""
        params = {"include_templates": include_templates}
        response = requests.get(f"{self.api_base}/profiles", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_profile(self, profile_id: str) -> Dict:
        """Get a specific profile by ID."""
        response = requests.get(f"{self.api_base}/profiles/{profile_id}")
        response.raise_for_status()
        return response.json()
    
    def activate_profile(self, profile_id: str) -> Dict:
        """Activate a profile and apply its configuration."""
        response = requests.post(f"{self.api_base}/profiles/{profile_id}/activate")
        response.raise_for_status()
        return response.json()
    
    def list_templates(self, category: str = None) -> Dict:
        """List all available templates."""
        params = {"category": category} if category else {}
        response = requests.get(f"{self.api_base}/templates", params=params)
        response.raise_for_status()
        return response.json()
    
    def apply_template(self, template_name: str, target_profile_id: str = None,
                      merge_strategy: str = "replace", create_backup: bool = True) -> Dict:
        """Apply a template to current configuration or specific profile."""
        data = {
            "target_profile_id": target_profile_id,
            "merge_strategy": merge_strategy,
            "create_backup": create_backup
        }
        
        response = requests.post(f"{self.api_base}/templates/{template_name}/apply", json=data)
        response.raise_for_status()
        return response.json()
    
    def create_backup(self, name: str, description: str = None) -> Dict:
        """Create a backup of all configurations."""
        data = {"name": name, "description": description}
        response = requests.post(f"{self.api_base}/backup", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_history(self, profile_id: str = None, limit: int = 50) -> Dict:
        """Get configuration change history."""
        if profile_id:
            url = f"{self.api_base}/profiles/{profile_id}/history"
        else:
            url = f"{self.api_base}/history"
        
        params = {"limit": limit}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()


def example_1_basic_profile_management():
    """Example 1: Basic profile creation and management."""
    print("Example 1: Basic Profile Management")
    print("=" * 50)
    
    client = AIDEProfileClient()
    
    # 1. Create a new profile for quick experiments
    print("1. Creating a quick experiment profile...")
    quick_profile = client.create_profile(
        name="Quick Experiments",
        description="Profile optimized for fast prototyping",
        tags=["quick", "prototype", "development"],
        copy_from_current=True
    )
    profile_id = quick_profile["data"]["id"]
    print(f"   Created profile: {quick_profile['data']['name']} (ID: {profile_id})")
    
    # 2. List all profiles
    print("\n2. Listing all profiles...")
    profiles = client.list_profiles()
    for profile in profiles["data"]["profiles"]:
        status = "ACTIVE" if profile["is_active"] else "INACTIVE"
        print(f"   - {profile['name']} ({status}) - {len(profile['tags'])} tags")
    
    # 3. Activate the new profile
    print(f"\n3. Activating profile '{quick_profile['data']['name']}'...")
    activation_result = client.activate_profile(profile_id)
    print(f"   {activation_result['message']}")
    
    print("\nExample 1 completed!\n")


def example_2_template_usage():
    """Example 2: Working with templates."""
    print("Example 2: Template Usage")
    print("=" * 50)
    
    client = AIDEProfileClient()
    
    # 1. List available templates
    print("1. Available templates:")
    templates = client.list_templates()
    for template in templates["data"]["templates"]:
        print(f"   - {template['display_name']} ({template['name']})")
        print(f"     Category: {template['category']}")
        print(f"     Cost: {template.get('estimated_cost', 'N/A')}")
        print(f"     Time: {template.get('estimated_time', 'N/A')}")
        print()
    
    # 2. Apply a template for cost-optimized analysis
    print("2. Applying cost-optimized template...")
    template_result = client.apply_template(
        template_name="cost_optimized",
        merge_strategy="replace",
        create_backup=True
    )
    print(f"   {template_result['message']}")
    print(f"   Backup created: {template_result['data']['backup_id']}")
    
    # 3. Create a profile from the applied template
    print("\n3. Creating profile from applied template...")
    cost_profile = client.create_profile(
        name="Cost-Optimized Analysis",
        description="Budget-friendly configuration for regular analysis",
        tags=["cost-optimized", "budget", "production"],
        copy_from_current=True,
        set_as_active=True
    )
    print(f"   Created and activated profile: {cost_profile['data']['name']}")
    
    print("\nExample 2 completed!\n")


def example_3_experiment_workflow():
    """Example 3: Complete experiment workflow."""
    print("Example 3: Complete Experiment Workflow")
    print("=" * 50)
    
    client = AIDEProfileClient()
    
    # 1. Create backup before starting
    print("1. Creating backup before experiment...")
    backup = client.create_backup(
        name="Before Experiment Workflow",
        description="Backup created before running experiment workflow example"
    )
    print(f"   Backup created: {backup['data']['backup_id']}")
    
    # 2. Apply quick experiment template for initial exploration
    print("\n2. Setting up quick experiment for initial exploration...")
    client.apply_template("quick_experiment")
    
    exploration_profile = client.create_profile(
        name="Initial Exploration",
        description="Quick exploration of the dataset",
        tags=["exploration", "initial", "quick"],
        copy_from_current=True
    )
    exploration_id = exploration_profile["data"]["id"]
    print(f"   Created exploration profile: {exploration_id}")
    
    # 3. Create comprehensive analysis profile
    print("\n3. Setting up comprehensive analysis...")
    client.apply_template("comprehensive_analysis")
    
    comprehensive_profile = client.create_profile(
        name="Comprehensive Analysis",
        description="Deep analysis for final model",
        tags=["comprehensive", "final", "production"],
        copy_from_current=True
    )
    comprehensive_id = comprehensive_profile["data"]["id"]
    print(f"   Created comprehensive profile: {comprehensive_id}")
    
    # 4. Create research-focused profile for publication
    print("\n4. Setting up research-focused analysis...")
    client.apply_template("research_focused")
    
    research_profile = client.create_profile(
        name="Research Publication",
        description="Statistical analysis for academic publication",
        tags=["research", "academic", "publication"],
        copy_from_current=True
    )
    research_id = research_profile["data"]["id"]
    print(f"   Created research profile: {research_id}")
    
    # 5. Demonstrate switching between profiles
    print("\n5. Workflow execution simulation:")
    
    profiles_workflow = [
        (exploration_id, "Initial exploration phase"),
        (comprehensive_id, "Comprehensive analysis phase"),
        (research_id, "Research and publication phase")
    ]
    
    for profile_id, phase_description in profiles_workflow:
        print(f"   - {phase_description}...")
        client.activate_profile(profile_id)
        print(f"     Profile activated for {phase_description.lower()}")
    
    print("\nExample 3 completed!\n")


def example_4_history_and_comparison():
    """Example 4: History tracking and configuration comparison."""
    print("Example 4: History and Comparison")
    print("=" * 50)
    
    client = AIDEProfileClient()
    
    # 1. Get global history
    print("1. Recent configuration changes:")
    history = client.get_history(limit=10)
    
    for entry in history["data"]["history"][:5]:  # Show last 5 entries
        print(f"   - {entry['timestamp'][:19]}: {entry['change_description']}")
        print(f"     Action: {entry['user_action']}")
        if entry["changed_fields"]:
            print(f"     Changed fields: {', '.join(entry['changed_fields'])}")
        print()
    
    # 2. Compare templates
    print("2. Comparing quick_experiment vs comprehensive_analysis templates:")
    
    comparison_data = {
        "template_names": ["quick_experiment", "comprehensive_analysis"],
        "comparison_fields": ["agent.steps", "agent.code.model", "agent.search.num_drafts"]
    }
    
    response = requests.post(f"{client.api_base}/templates/compare", json=comparison_data)
    if response.status_code == 200:
        comparison = response.json()["data"]
        
        print("   Comparison results:")
        for comp in comparison["comparisons"]:
            print(f"   - {comp['display_name']}:")
            for field, value in comp["field_values"].items():
                print(f"     {field}: {value}")
        
        print(f"\n   Common fields: {', '.join(comparison['common_fields'])}")
        print(f"   Different fields: {', '.join(comparison['different_fields'])}")
    
    print("\nExample 4 completed!\n")


def example_5_custom_template_creation():
    """Example 5: Creating and using custom templates."""
    print("Example 5: Custom Template Creation")
    print("=" * 50)
    
    client = AIDEProfileClient()
    
    # 1. Create a custom template for specific use case
    print("1. Creating custom template for medium-budget analysis...")
    
    custom_template_data = {
        "name": "medium_budget_analysis",
        "display_name": "Medium Budget Analysis",
        "description": "Balanced configuration for moderate budget projects",
        "category": "custom",
        "config_data": {
            "agent": {
                "steps": 20,
                "k_fold_validation": 5,
                "expose_prediction": True,
                "data_preview": True,
                "code": {
                    "model": "gpt-4-turbo",
                    "temp": 0.4
                },
                "feedback": {
                    "model": "gpt-3.5-turbo",
                    "temp": 0.3
                },
                "search": {
                    "max_debug_depth": 3,
                    "debug_prob": 0.5,
                    "num_drafts": 5
                }
            },
            "exec": {
                "timeout": 4800,
                "agent_file_name": "runfile.py",
                "format_tb_ipython": False
            },
            "generate_report": True,
            "report": {
                "model": "gpt-4-turbo",
                "temp": 0.9
            }
        },
        "use_case": "Medium-budget projects requiring good quality",
        "estimated_cost": "$8-15",
        "estimated_time": "25-45 minutes",
        "complexity": "intermediate",
        "tags": ["medium-budget", "balanced", "custom"]
    }
    
    response = requests.post(f"{client.api_base}/templates", json=custom_template_data)
    if response.status_code == 200:
        template = response.json()
        print(f"   Created template: {template['data']['display_name']}")
        print(f"   Estimated cost: {template['data']['estimated_cost']}")
        print(f"   Estimated time: {template['data']['estimated_time']}")
    
    # 2. Apply the custom template
    print("\n2. Applying custom template...")
    client.apply_template("medium_budget_analysis")
    
    # 3. Create profile from custom template
    custom_profile = client.create_profile(
        name="Medium Budget Project",
        description="Profile using custom medium-budget template",
        tags=["custom", "medium-budget", "project"],
        copy_from_current=True
    )
    print(f"   Created profile: {custom_profile['data']['name']}")
    
    # 4. Save current configuration as another template
    print("\n3. Saving current configuration as new template...")
    
    save_template_data = {
        "name": "current_optimized",
        "display_name": "Current Optimized Configuration",
        "description": "Template based on current optimized settings",
        "category": "custom",
        "tags": ["optimized", "current", "snapshot"]
    }
    
    response = requests.post(f"{client.api_base}/templates/save-current", json=save_template_data)
    if response.status_code == 200:
        saved_template = response.json()
        print(f"   Saved template: {saved_template['data']['display_name']}")
    
    print("\nExample 5 completed!\n")


def example_6_backup_and_recovery():
    """Example 6: Backup and recovery operations."""
    print("Example 6: Backup and Recovery")
    print("=" * 50)
    
    client = AIDEProfileClient()
    
    # 1. Create comprehensive backup
    print("1. Creating comprehensive backup...")
    backup = client.create_backup(
        name="Comprehensive Backup",
        description="Full backup of all profiles, templates, and settings"
    )
    backup_id = backup["data"]["backup_id"]
    print(f"   Backup created: {backup_id}")
    
    # 2. List all backups
    print("\n2. Available backups:")
    response = requests.get(f"{client.api_base}/backups")
    if response.status_code == 200:
        backups = response.json()["data"]
        for backup_info in backups[:5]:  # Show last 5 backups
            print(f"   - {backup_info['name']} ({backup_info['id']})")
            print(f"     Created: {backup_info['created_at'][:19]}")
            print(f"     Size: {backup_info.get('file_size', 'Unknown')} bytes")
            print()
    
    # 3. Export specific profiles
    print("3. Exporting profiles to YAML...")
    
    # First get list of profiles to export
    profiles = client.list_profiles()
    profile_ids = [p["id"] for p in profiles["data"]["profiles"][:2]]  # Export first 2 profiles
    
    export_data = {
        "profile_ids": profile_ids,
        "include_history": False,
        "format": "yaml"
    }
    
    response = requests.post(f"{client.api_base}/export", json=export_data)
    if response.status_code == 200:
        exported_yaml = response.text
        print(f"   Exported {len(profile_ids)} profiles to YAML format")
        print(f"   YAML size: {len(exported_yaml)} characters")
        
        # Save to file for demonstration
        with open("exported_profiles.yaml", "w") as f:
            f.write(exported_yaml)
        print("   Saved to 'exported_profiles.yaml'")
    
    # 4. Demonstrate import (using the exported data)
    print("\n4. Demonstrating profile import...")
    
    # Modify the exported YAML slightly for import demo
    try:
        exported_data = yaml.safe_load(exported_yaml)
        if exported_data and "profiles" in exported_data:
            # Modify profile names to avoid conflicts
            for profile in exported_data["profiles"]:
                profile["name"] = f"Imported_{profile['name']}"
            
            modified_yaml = yaml.dump(exported_data)
            
            import_data = {
                "data": modified_yaml,
                "merge_strategy": "create_new",
                "set_as_active": False
            }
            
            response = requests.post(f"{client.api_base}/import", json=import_data)
            if response.status_code == 200:
                imported = response.json()
                print(f"   Successfully imported {len(imported['data'])} profiles")
                for profile in imported["data"]:
                    print(f"     - {profile['name']}")
    except Exception as e:
        print(f"   Import demonstration skipped: {e}")
    
    print("\nExample 6 completed!\n")


def example_7_api_integration():
    """Example 7: Integration with existing workflows."""
    print("Example 7: API Integration")
    print("=" * 50)
    
    client = AIDEProfileClient()
    
    # 1. Get recommendations based on use case
    print("1. Getting template recommendations...")
    
    params = {
        "use_case": "machine learning competition",
        "complexity": "advanced",
        "budget": "high"
    }
    
    response = requests.get(f"{client.api_base}/template-recommendations", params=params)
    if response.status_code == 200:
        recommendations = response.json()["data"]
        print(f"   Found {len(recommendations)} recommendations:")
        for template in recommendations:
            print(f"   - {template['display_name']}")
            print(f"     Use case: {template.get('use_case', 'N/A')}")
            print(f"     Complexity: {template['complexity']}")
            print()
    
    # 2. Get system statistics
    print("2. System statistics:")
    response = requests.get(f"{client.api_base}/statistics")
    if response.status_code == 200:
        stats = response.json()["data"]
        print(f"   Total profiles: {stats['total_profiles']}")
        print(f"   Active profiles: {stats['active_profiles']}")
        print(f"   Template profiles: {stats['template_profiles']}")
        print(f"   Default profile: {stats.get('default_profile', 'None')}")
        print(f"   Active profile: {stats.get('active_profile', 'None')}")
        print(f"   Recent changes: {stats['recent_changes']}")
    
    # 3. Sync current configuration
    print("\n3. Syncing current configuration with active profile...")
    response = requests.post(f"{client.api_base}/sync")
    if response.status_code == 200:
        sync_result = response.json()
        print(f"   {sync_result['message']}")
    
    # 4. Get template categories
    print("\n4. Available template categories:")
    response = requests.get(f"{client.api_base}/template-categories")
    if response.status_code == 200:
        categories = response.json()["data"]
        for category, description in categories.items():
            print(f"   - {category}: {description}")
    
    print("\nExample 7 completed!\n")


def main():
    """Run all examples."""
    print("AIDE ML Profile Management API Examples")
    print("=" * 60)
    print("This script demonstrates common usage patterns for the")
    print("AIDE ML Profile Management API.\n")
    
    print("Note: Make sure the AIDE ML backend is running on localhost:8000")
    print("before running these examples.\n")
    
    try:
        # Test connection
        response = requests.get("http://localhost:8000/health", timeout=5)
        response.raise_for_status()
        print("✓ Connection to AIDE ML backend successful\n")
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to AIDE ML backend: {e}")
        print("Please start the backend server first.\n")
        return
    
    # Run examples
    examples = [
        example_1_basic_profile_management,
        example_2_template_usage,
        example_3_experiment_workflow,
        example_4_history_and_comparison,
        example_5_custom_template_creation,
        example_6_backup_and_recovery,
        example_7_api_integration
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except requests.exceptions.RequestException as e:
            print(f"Error in example {i}: {e}")
            print(f"Skipping to next example...\n")
        except Exception as e:
            print(f"Unexpected error in example {i}: {e}")
            print(f"Skipping to next example...\n")
    
    print("All examples completed!")
    print("\nFor more information, see the API documentation:")
    print("http://localhost:8000/api/docs")


if __name__ == "__main__":
    main()