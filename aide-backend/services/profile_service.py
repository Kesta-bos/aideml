"""
Profile management service for AIDE ML configuration profiles.
Handles business logic for configuration profiles, history, and profile operations.
"""

import json
import yaml
import logging
from typing import List, Optional, Dict, Any, Tuple
from copy import deepcopy

from services.storage_service import StorageService, StorageError
from services.config_service import ConfigService, ConfigurationError
from models.profile_models import (
    ConfigProfile,
    ConfigHistory,
    ProfileCreateRequest,
    ProfileUpdateRequest,
    ProfileListResponse,
    HistoryListResponse,
    UserAction,
    SearchProfilesRequest,
    ConfigDiff,
    ConfigDiffResponse,
    RollbackRequest,
    ProfileExportRequest,
    ProfileImportRequest
)
from models.config_models import ConfigValidationResult


logger = logging.getLogger("aide")


class ProfileError(Exception):
    """Profile management errors."""
    pass


class ProfileService:
    """Service for managing configuration profiles."""
    
    def __init__(self):
        self.storage = StorageService()
        self.config_service = ConfigService()
    
    # Profile CRUD Operations
    
    def create_profile(self, request: ProfileCreateRequest) -> ConfigProfile:
        """Create a new configuration profile."""
        try:
            # Get current config if copying from current
            config_data = request.config_data
            if request.copy_from_current and not config_data:
                config_data = self.config_service.get_current_config()
            
            # Validate the configuration data
            if config_data:
                validation_result = self.config_service.validate_config(config_data)
                if not validation_result.valid:
                    error_messages = [error.message for error in validation_result.errors]
                    raise ProfileError(f"Invalid configuration: {'; '.join(error_messages)}")
            
            # Create the profile
            profile = self.storage.create_profile(request, config_data)
            
            logger.info(f"Created profile '{profile.name}' with ID {profile.id}")
            return profile
            
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
        except ConfigurationError as e:
            raise ProfileError(f"Configuration error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating profile: {e}")
            raise ProfileError(f"Failed to create profile: {e}")
    
    def get_profile(self, profile_id: str) -> ConfigProfile:
        """Get a profile by ID."""
        try:
            profile = self.storage.get_profile(profile_id)
            if not profile:
                raise ProfileError(f"Profile {profile_id} not found")
            return profile
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
    
    def get_profile_by_name(self, name: str) -> ConfigProfile:
        """Get a profile by name."""
        try:
            profile = self.storage.get_profile_by_name(name)
            if not profile:
                raise ProfileError(f"Profile '{name}' not found")
            return profile
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
    
    def update_profile(self, profile_id: str, request: ProfileUpdateRequest) -> ConfigProfile:
        """Update an existing profile."""
        try:
            # Validate configuration data if provided
            if request.config_data:
                validation_result = self.config_service.validate_config(request.config_data)
                if not validation_result.valid:
                    error_messages = [error.message for error in validation_result.errors]
                    raise ProfileError(f"Invalid configuration: {'; '.join(error_messages)}")
            
            profile = self.storage.update_profile(profile_id, request)
            logger.info(f"Updated profile '{profile.name}' (ID: {profile_id})")
            return profile
            
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
        except ConfigurationError as e:
            raise ProfileError(f"Configuration error: {e}")
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile."""
        try:
            # Get profile info for logging
            profile = self.storage.get_profile(profile_id)
            if not profile:
                return False
            
            success = self.storage.delete_profile(profile_id)
            if success:
                logger.info(f"Deleted profile '{profile.name}' (ID: {profile_id})")
            return success
            
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
    
    def list_profiles(self, include_templates: bool = False) -> ProfileListResponse:
        """List all profiles with metadata."""
        try:
            profiles = self.storage.list_profiles(include_templates)
            
            # Find active and default profiles
            active_profile_id = None
            default_profile_id = None
            
            for profile in profiles:
                if profile.is_active:
                    active_profile_id = profile.id
                if profile.is_default:
                    default_profile_id = profile.id
            
            return ProfileListResponse(
                profiles=profiles,
                total_count=len(profiles),
                active_profile_id=active_profile_id,
                default_profile_id=default_profile_id
            )
            
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
    
    def search_profiles(self, request: SearchProfilesRequest) -> ProfileListResponse:
        """Search profiles with filters and pagination."""
        try:
            profiles, total_count = self.storage.search_profiles(request)
            
            # Find active and default profiles from the search results
            active_profile_id = None
            default_profile_id = None
            
            for profile in profiles:
                if profile.is_active:
                    active_profile_id = profile.id
                if profile.is_default:
                    default_profile_id = profile.id
            
            return ProfileListResponse(
                profiles=profiles,
                total_count=total_count,
                active_profile_id=active_profile_id,
                default_profile_id=default_profile_id
            )
            
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
    
    # Profile Activation and Management
    
    def activate_profile(self, profile_id: str) -> Dict[str, Any]:
        """Activate a profile and apply its configuration."""
        try:
            # Activate the profile in storage
            profile = self.storage.activate_profile(profile_id)
            
            # Apply the profile's configuration to the current system
            config_result = self.config_service.update_config(profile.config_data)
            
            logger.info(f"Activated profile '{profile.name}' (ID: {profile_id})")
            
            return {
                "profile": profile,
                "applied_config": config_result,
                "message": f"Profile '{profile.name}' activated successfully"
            }
            
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
        except ConfigurationError as e:
            raise ProfileError(f"Configuration error: {e}")
    
    def get_active_profile(self) -> Optional[ConfigProfile]:
        """Get the currently active profile."""
        try:
            return self.storage.get_active_profile()
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
    
    def set_default_profile(self, profile_id: str) -> ConfigProfile:
        """Set a profile as the default."""
        try:
            profile = self.storage.set_default_profile(profile_id)
            logger.info(f"Set profile '{profile.name}' as default (ID: {profile_id})")
            return profile
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
    
    def get_default_profile(self) -> Optional[ConfigProfile]:
        """Get the default profile."""
        try:
            return self.storage.get_default_profile()
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
    
    # History Management
    
    def get_profile_history(self, profile_id: str, limit: int = 50) -> HistoryListResponse:
        """Get history for a specific profile."""
        try:
            # Verify profile exists
            profile = self.storage.get_profile(profile_id)
            if not profile:
                raise ProfileError(f"Profile {profile_id} not found")
            
            history = self.storage.get_history(profile_id, limit)
            
            return HistoryListResponse(
                history=history,
                total_count=len(history),
                profile_id=profile_id
            )
            
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
    
    def get_global_history(self, limit: int = 50) -> HistoryListResponse:
        """Get global configuration history."""
        try:
            history = self.storage.get_history(None, limit)
            
            return HistoryListResponse(
                history=history,
                total_count=len(history),
                profile_id=None
            )
            
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
    
    def rollback_to_version(self, request: RollbackRequest) -> Dict[str, Any]:
        """Rollback configuration to a specific history entry."""
        try:
            # Get the history entry
            history_entry = self.storage.get_history_entry(request.history_id)
            if not history_entry:
                raise ProfileError(f"History entry {request.history_id} not found")
            
            # Create backup if requested
            backup_id = None
            if request.create_backup:
                backup_id = self.storage.create_backup(
                    name=f"Backup before rollback to {request.history_id}",
                    description=f"Automatic backup created before rolling back to {history_entry.change_description}"
                )
            
            # Apply the historical configuration
            if history_entry.profile_id:
                # Update specific profile
                profile_request = ProfileUpdateRequest(config_data=history_entry.config_data)
                profile = self.storage.update_profile(history_entry.profile_id, profile_request)
                
                # Add history entry for rollback
                self.storage.add_history_entry(
                    profile_id=history_entry.profile_id,
                    config_data=history_entry.config_data,
                    change_description=f"Rolled back to: {history_entry.change_description}",
                    user_action=UserAction.ROLLBACK,
                    changed_fields=[]
                )
                
                result_config = profile.config_data
            else:
                # Update global configuration
                result_config = self.config_service.update_config(history_entry.config_data)
                
                # Add global history entry for rollback
                self.storage.add_history_entry(
                    profile_id=None,
                    config_data=history_entry.config_data,
                    change_description=f"Global rollback to: {history_entry.change_description}",
                    user_action=UserAction.ROLLBACK,
                    changed_fields=[]
                )
            
            logger.info(f"Rolled back to history entry {request.history_id}")
            
            return {
                "success": True,
                "history_entry": history_entry,
                "applied_config": result_config,
                "backup_id": backup_id,
                "message": f"Successfully rolled back to: {history_entry.change_description}"
            }
            
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
        except ConfigurationError as e:
            raise ProfileError(f"Configuration error: {e}")
    
    # Configuration Comparison
    
    def compare_profiles(self, profile_id_1: str, profile_id_2: str) -> ConfigDiffResponse:
        """Compare configurations between two profiles."""
        try:
            profile1 = self.storage.get_profile(profile_id_1)
            profile2 = self.storage.get_profile(profile_id_2)
            
            if not profile1:
                raise ProfileError(f"Profile {profile_id_1} not found")
            if not profile2:
                raise ProfileError(f"Profile {profile_id_2} not found")
            
            differences = self._compare_configs(profile1.config_data, profile2.config_data)
            
            summary = f"{len(differences)} differences found between '{profile1.name}' and '{profile2.name}'"
            
            return ConfigDiffResponse(
                differences=differences,
                summary=summary,
                from_version=f"{profile1.name} (v{profile1.version})",
                to_version=f"{profile2.name} (v{profile2.version})"
            )
            
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
    
    def compare_with_history(self, history_id_1: str, history_id_2: str) -> ConfigDiffResponse:
        """Compare configurations between two history entries."""
        try:
            history1 = self.storage.get_history_entry(history_id_1)
            history2 = self.storage.get_history_entry(history_id_2)
            
            if not history1:
                raise ProfileError(f"History entry {history_id_1} not found")
            if not history2:
                raise ProfileError(f"History entry {history_id_2} not found")
            
            differences = self._compare_configs(history1.config_data, history2.config_data)
            
            summary = f"{len(differences)} differences found between history entries"
            
            return ConfigDiffResponse(
                differences=differences,
                summary=summary,
                from_version=f"History {history_id_1}",
                to_version=f"History {history_id_2}"
            )
            
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
    
    # Import/Export Operations
    
    def export_profiles(self, request: ProfileExportRequest) -> str:
        """Export profiles to YAML or JSON format."""
        try:
            export_data = {
                "profiles": [],
                "exported_at": json.dumps(datetime.utcnow(), default=str),
                "version": "1.0"
            }
            
            for profile_id in request.profile_ids:
                profile = self.storage.get_profile(profile_id)
                if not profile:
                    raise ProfileError(f"Profile {profile_id} not found")
                
                profile_data = {
                    "name": profile.name,
                    "description": profile.description,
                    "config_data": profile.config_data,
                    "tags": profile.tags,
                    "is_default": profile.is_default,
                    "version": profile.version,
                    "created_at": profile.created_at.isoformat(),
                    "updated_at": profile.updated_at.isoformat()
                }
                
                if request.include_history:
                    history = self.storage.get_history(profile_id, 50)
                    profile_data["history"] = [
                        {
                            "change_description": h.change_description,
                            "user_action": h.user_action.value,
                            "changed_fields": h.changed_fields,
                            "timestamp": h.timestamp.isoformat()
                        }
                        for h in history
                    ]
                
                export_data["profiles"].append(profile_data)
            
            if request.format.lower() == "json":
                return json.dumps(export_data, indent=2)
            else:
                return yaml.dump(export_data, default_flow_style=False, indent=2)
            
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
    
    def import_profiles(self, request: ProfileImportRequest) -> List[ConfigProfile]:
        """Import profiles from YAML or JSON data."""
        try:
            # Parse the data
            try:
                if request.data.strip().startswith('{'):
                    import_data = json.loads(request.data)
                else:
                    import_data = yaml.safe_load(request.data)
            except (json.JSONDecodeError, yaml.YAMLError) as e:
                raise ProfileError(f"Invalid data format: {e}")
            
            if not isinstance(import_data, dict) or "profiles" not in import_data:
                raise ProfileError("Invalid profile data structure")
            
            imported_profiles = []
            
            for profile_data in import_data["profiles"]:
                # Validate required fields
                if "name" not in profile_data or "config_data" not in profile_data:
                    raise ProfileError("Profile data missing required fields")
                
                # Handle merge strategy
                profile_name = profile_data["name"]
                existing_profile = self.storage.get_profile_by_name(profile_name)
                
                if existing_profile and request.merge_strategy == "create_new":
                    # Create new profile with modified name
                    profile_name = f"{profile_name}_imported"
                    counter = 1
                    while self.storage.get_profile_by_name(profile_name):
                        profile_name = f"{profile_data['name']}_imported_{counter}"
                        counter += 1
                
                # Validate configuration
                validation_result = self.config_service.validate_config(profile_data["config_data"])
                if not validation_result.valid:
                    error_messages = [error.message for error in validation_result.errors]
                    raise ProfileError(f"Invalid configuration in profile '{profile_name}': {'; '.join(error_messages)}")
                
                if existing_profile and request.merge_strategy == "overwrite":
                    # Update existing profile
                    update_request = ProfileUpdateRequest(
                        name=profile_name,
                        description=profile_data.get("description"),
                        config_data=profile_data["config_data"],
                        tags=profile_data.get("tags", [])
                    )
                    profile = self.storage.update_profile(existing_profile.id, update_request)
                else:
                    # Create new profile
                    create_request = ProfileCreateRequest(
                        name=profile_name,
                        description=profile_data.get("description"),
                        config_data=profile_data["config_data"],
                        tags=profile_data.get("tags", []),
                        copy_from_current=False,
                        set_as_active=request.set_as_active and len(import_data["profiles"]) == 1
                    )
                    profile = self.storage.create_profile(create_request, profile_data["config_data"])
                
                imported_profiles.append(profile)
            
            logger.info(f"Imported {len(imported_profiles)} profiles")
            return imported_profiles
            
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
        except ConfigurationError as e:
            raise ProfileError(f"Configuration error: {e}")
    
    # Helper Methods
    
    def _compare_configs(self, config1: Dict[str, Any], config2: Dict[str, Any]) -> List[ConfigDiff]:
        """Compare two configuration dictionaries and return differences."""
        differences = []
        
        def compare_recursive(obj1: Any, obj2: Any, path: str = ""):
            if isinstance(obj1, dict) and isinstance(obj2, dict):
                all_keys = set(obj1.keys()) | set(obj2.keys())
                for key in all_keys:
                    key_path = f"{path}.{key}" if path else key
                    
                    if key not in obj1:
                        differences.append(ConfigDiff(
                            field_path=key_path,
                            old_value=None,
                            new_value=obj2[key],
                            change_type="added"
                        ))
                    elif key not in obj2:
                        differences.append(ConfigDiff(
                            field_path=key_path,
                            old_value=obj1[key],
                            new_value=None,
                            change_type="removed"
                        ))
                    else:
                        compare_recursive(obj1[key], obj2[key], key_path)
            elif obj1 != obj2:
                differences.append(ConfigDiff(
                    field_path=path,
                    old_value=obj1,
                    new_value=obj2,
                    change_type="modified"
                ))
        
        compare_recursive(config1, config2)
        return differences
    
    def sync_current_config(self) -> Optional[str]:
        """Sync current AIDE configuration with active profile."""
        try:
            active_profile = self.get_active_profile()
            if not active_profile:
                logger.info("No active profile to sync with")
                return None
            
            current_config = self.config_service.get_current_config()
            
            # Check if configurations are different
            differences = self._compare_configs(active_profile.config_data, current_config)
            
            if differences:
                # Update active profile with current configuration
                update_request = ProfileUpdateRequest(config_data=current_config)
                updated_profile = self.storage.update_profile(active_profile.id, update_request)
                
                logger.info(f"Synced current configuration to active profile '{updated_profile.name}'")
                return f"Synced {len(differences)} changes to profile '{updated_profile.name}'"
            else:
                logger.info("Current configuration already matches active profile")
                return "Configuration already in sync"
                
        except Exception as e:
            logger.error(f"Error syncing configuration: {e}")
            raise ProfileError(f"Failed to sync configuration: {e}")
    
    def cleanup_old_data(self, retention_days: int = 30) -> Dict[str, int]:
        """Clean up old profile data and history."""
        try:
            # Clean up old history entries
            cleaned_history = self.storage.cleanup_old_history(retention_days)
            
            # Future: Could add cleanup for old backups, unused profiles, etc.
            
            return {
                "cleaned_history_entries": cleaned_history,
                "retention_days": retention_days
            }
            
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")
        
    def get_profile_statistics(self) -> Dict[str, Any]:
        """Get statistics about profiles and usage."""
        try:
            all_profiles = self.storage.list_profiles(include_templates=True)
            
            stats = {
                "total_profiles": len(all_profiles),
                "active_profiles": len([p for p in all_profiles if not p.is_template]),
                "template_profiles": len([p for p in all_profiles if p.is_template]),
                "default_profile": next((p.name for p in all_profiles if p.is_default), None),
                "active_profile": next((p.name for p in all_profiles if p.is_active), None),
                "total_tags": len(set(tag for p in all_profiles for tag in p.tags)),
                "most_recent_profile": max(all_profiles, key=lambda p: p.updated_at).name if all_profiles else None
            }
            
            # Get history statistics
            recent_history = self.storage.get_history(limit=100)
            stats["recent_changes"] = len(recent_history)
            stats["most_active_profile"] = None
            
            if recent_history:
                from collections import Counter
                profile_activity = Counter(h.profile_id for h in recent_history if h.profile_id)
                if profile_activity:
                    most_active_id = profile_activity.most_common(1)[0][0]
                    most_active_profile = self.storage.get_profile(most_active_id)
                    stats["most_active_profile"] = most_active_profile.name if most_active_profile else None
            
            return stats
            
        except StorageError as e:
            raise ProfileError(f"Storage error: {e}")


# Import datetime for export functionality
from datetime import datetime