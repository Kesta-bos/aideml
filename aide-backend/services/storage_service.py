"""
Storage service for persistent configuration data management.
Handles database operations for profiles, history, templates, and backups.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import and_, or_, desc, func

from database.init_db import get_database_manager
from database.models import (
    ConfigProfile as DBConfigProfile,
    ConfigHistory as DBConfigHistory,
    ConfigTemplate as DBConfigTemplate,
    ConfigBackup as DBConfigBackup,
    ConfigSetting as DBConfigSetting
)
from models.profile_models import (
    ConfigProfile,
    ConfigHistory,
    ProfileCreateRequest,
    ProfileUpdateRequest,
    UserAction,
    SearchProfilesRequest
)
from models.template_models import ConfigTemplate, TemplateCreateRequest


logger = logging.getLogger("aide")


class StorageError(Exception):
    """Storage operation errors."""
    pass


class StorageService:
    """Service for persistent storage operations."""
    
    def __init__(self):
        self.db_manager = get_database_manager()
    
    def _get_session(self) -> Session:
        """Get database session."""
        return self.db_manager.get_session()
    
    # Profile Management Methods
    
    def create_profile(self, request: ProfileCreateRequest, config_data: Dict[str, Any] = None) -> ConfigProfile:
        """Create a new configuration profile."""
        with self._get_session() as session:
            try:
                # Check if name already exists
                existing = session.query(DBConfigProfile).filter_by(name=request.name).first()
                if existing:
                    raise StorageError(f"Profile with name '{request.name}' already exists")
                
                # Use provided config_data or get from current if copy_from_current is True
                final_config_data = config_data or request.config_data or {}
                
                # Create database profile
                db_profile = DBConfigProfile(
                    name=request.name,
                    description=request.description,
                    config_data=final_config_data,
                    tags=request.tags,
                    is_active=request.set_as_active
                )
                
                # If setting as active, deactivate other profiles
                if request.set_as_active:
                    session.query(DBConfigProfile).update({"is_active": False})
                
                session.add(db_profile)
                session.commit()
                session.refresh(db_profile)
                
                # Create history entry
                self._add_history_entry(
                    session,
                    profile_id=db_profile.id,
                    config_data=final_config_data,
                    change_description=f"Profile '{request.name}' created",
                    user_action=UserAction.MANUAL_EDIT,
                    changed_fields=[]
                )
                
                session.commit()
                
                return self._db_profile_to_model(db_profile)
                
            except IntegrityError as e:
                session.rollback()
                raise StorageError(f"Profile creation failed: {e}")
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error creating profile: {e}")
                raise StorageError(f"Database error: {e}")
    
    def get_profile(self, profile_id: str) -> Optional[ConfigProfile]:
        """Get a profile by ID."""
        with self._get_session() as session:
            try:
                db_profile = session.query(DBConfigProfile).filter_by(id=profile_id).first()
                return self._db_profile_to_model(db_profile) if db_profile else None
            except SQLAlchemyError as e:
                logger.error(f"Database error getting profile {profile_id}: {e}")
                raise StorageError(f"Database error: {e}")
    
    def get_profile_by_name(self, name: str) -> Optional[ConfigProfile]:
        """Get a profile by name."""
        with self._get_session() as session:
            try:
                db_profile = session.query(DBConfigProfile).filter_by(name=name).first()
                return self._db_profile_to_model(db_profile) if db_profile else None
            except SQLAlchemyError as e:
                logger.error(f"Database error getting profile by name {name}: {e}")
                raise StorageError(f"Database error: {e}")
    
    def update_profile(self, profile_id: str, request: ProfileUpdateRequest) -> ConfigProfile:
        """Update an existing profile."""
        with self._get_session() as session:
            try:
                db_profile = session.query(DBConfigProfile).filter_by(id=profile_id).first()
                if not db_profile:
                    raise StorageError(f"Profile {profile_id} not found")
                
                # Store previous config for history
                previous_config = db_profile.config_data.copy()
                changed_fields = []
                
                # Update fields
                if request.name is not None and request.name != db_profile.name:
                    # Check name uniqueness
                    existing = session.query(DBConfigProfile).filter(
                        and_(DBConfigProfile.name == request.name, DBConfigProfile.id != profile_id)
                    ).first()
                    if existing:
                        raise StorageError(f"Profile with name '{request.name}' already exists")
                    db_profile.name = request.name
                    changed_fields.append("name")
                
                if request.description is not None:
                    db_profile.description = request.description
                    changed_fields.append("description")
                
                if request.config_data is not None:
                    # Deep compare config data to find changed fields
                    config_changes = self._find_config_changes(previous_config, request.config_data)
                    changed_fields.extend(config_changes)
                    db_profile.config_data = request.config_data
                
                if request.tags is not None:
                    db_profile.tags = request.tags
                    changed_fields.append("tags")
                
                # Update version and timestamp
                db_profile.version += 1
                db_profile.updated_at = datetime.utcnow()
                
                session.commit()
                
                # Add history entry if there were changes
                if changed_fields:
                    self._add_history_entry(
                        session,
                        profile_id=profile_id,
                        config_data=db_profile.config_data,
                        change_description=f"Profile '{db_profile.name}' updated: {', '.join(changed_fields)}",
                        user_action=UserAction.MANUAL_EDIT,
                        changed_fields=changed_fields,
                        previous_config=previous_config
                    )
                    session.commit()
                
                session.refresh(db_profile)
                return self._db_profile_to_model(db_profile)
                
            except IntegrityError as e:
                session.rollback()
                raise StorageError(f"Profile update failed: {e}")
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error updating profile: {e}")
                raise StorageError(f"Database error: {e}")
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile."""
        with self._get_session() as session:
            try:
                db_profile = session.query(DBConfigProfile).filter_by(id=profile_id).first()
                if not db_profile:
                    return False
                
                # Don't allow deletion of active or default profiles
                if db_profile.is_active:
                    raise StorageError("Cannot delete active profile")
                if db_profile.is_default:
                    raise StorageError("Cannot delete default profile")
                
                session.delete(db_profile)
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error deleting profile: {e}")
                raise StorageError(f"Database error: {e}")
    
    def list_profiles(self, include_templates: bool = False) -> List[ConfigProfile]:
        """List all profiles."""
        with self._get_session() as session:
            try:
                query = session.query(DBConfigProfile)
                if not include_templates:
                    query = query.filter_by(is_template=False)
                
                db_profiles = query.order_by(desc(DBConfigProfile.updated_at)).all()
                return [self._db_profile_to_model(p) for p in db_profiles]
                
            except SQLAlchemyError as e:
                logger.error(f"Database error listing profiles: {e}")
                raise StorageError(f"Database error: {e}")
    
    def search_profiles(self, request: SearchProfilesRequest) -> Tuple[List[ConfigProfile], int]:
        """Search profiles with filters and pagination."""
        with self._get_session() as session:
            try:
                query = session.query(DBConfigProfile)
                
                # Apply filters
                if request.query:
                    search_pattern = f"%{request.query}%"
                    query = query.filter(
                        or_(
                            DBConfigProfile.name.ilike(search_pattern),
                            DBConfigProfile.description.ilike(search_pattern)
                        )
                    )
                
                if request.tags:
                    # SQLite JSON filtering - this is a simplified approach
                    for tag in request.tags:
                        query = query.filter(DBConfigProfile.tags.contains(tag))
                
                if request.is_template is not None:
                    query = query.filter_by(is_template=request.is_template)
                
                if request.date_from:
                    query = query.filter(DBConfigProfile.created_at >= request.date_from)
                
                if request.date_to:
                    query = query.filter(DBConfigProfile.created_at <= request.date_to)
                
                # Get total count
                total_count = query.count()
                
                # Apply pagination
                offset = (request.page - 1) * request.limit
                db_profiles = query.order_by(desc(DBConfigProfile.updated_at)).offset(offset).limit(request.limit).all()
                
                profiles = [self._db_profile_to_model(p) for p in db_profiles]
                return profiles, total_count
                
            except SQLAlchemyError as e:
                logger.error(f"Database error searching profiles: {e}")
                raise StorageError(f"Database error: {e}")
    
    def activate_profile(self, profile_id: str) -> ConfigProfile:
        """Activate a profile (deactivate others)."""
        with self._get_session() as session:
            try:
                # Check if profile exists
                db_profile = session.query(DBConfigProfile).filter_by(id=profile_id).first()
                if not db_profile:
                    raise StorageError(f"Profile {profile_id} not found")
                
                # Deactivate all profiles
                session.query(DBConfigProfile).update({"is_active": False})
                
                # Activate the target profile
                db_profile.is_active = True
                session.commit()
                
                # Add history entry
                self._add_history_entry(
                    session,
                    profile_id=profile_id,
                    config_data=db_profile.config_data,
                    change_description=f"Profile '{db_profile.name}' activated",
                    user_action=UserAction.PROFILE_SWITCH,
                    changed_fields=["is_active"]
                )
                
                session.commit()
                session.refresh(db_profile)
                return self._db_profile_to_model(db_profile)
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error activating profile: {e}")
                raise StorageError(f"Database error: {e}")
    
    def get_active_profile(self) -> Optional[ConfigProfile]:
        """Get the currently active profile."""
        with self._get_session() as session:
            try:
                db_profile = session.query(DBConfigProfile).filter_by(is_active=True).first()
                return self._db_profile_to_model(db_profile) if db_profile else None
            except SQLAlchemyError as e:
                logger.error(f"Database error getting active profile: {e}")
                raise StorageError(f"Database error: {e}")
    
    def get_default_profile(self) -> Optional[ConfigProfile]:
        """Get the default profile."""
        with self._get_session() as session:
            try:
                db_profile = session.query(DBConfigProfile).filter_by(is_default=True).first()
                return self._db_profile_to_model(db_profile) if db_profile else None
            except SQLAlchemyError as e:
                logger.error(f"Database error getting default profile: {e}")
                raise StorageError(f"Database error: {e}")
    
    def set_default_profile(self, profile_id: str) -> ConfigProfile:
        """Set a profile as default."""
        with self._get_session() as session:
            try:
                # Check if profile exists
                db_profile = session.query(DBConfigProfile).filter_by(id=profile_id).first()
                if not db_profile:
                    raise StorageError(f"Profile {profile_id} not found")
                
                # Unset current default
                session.query(DBConfigProfile).update({"is_default": False})
                
                # Set new default
                db_profile.is_default = True
                session.commit()
                session.refresh(db_profile)
                return self._db_profile_to_model(db_profile)
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error setting default profile: {e}")
                raise StorageError(f"Database error: {e}")
    
    # History Management Methods
    
    def add_history_entry(self, profile_id: Optional[str], config_data: Dict[str, Any], 
                         change_description: str, user_action: UserAction, 
                         changed_fields: List[str] = None, previous_config: Dict[str, Any] = None) -> ConfigHistory:
        """Add a configuration change to history."""
        with self._get_session() as session:
            try:
                history_entry = self._add_history_entry(
                    session, profile_id, config_data, change_description, 
                    user_action, changed_fields, previous_config
                )
                session.commit()
                session.refresh(history_entry)
                return self._db_history_to_model(history_entry)
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error adding history entry: {e}")
                raise StorageError(f"Database error: {e}")
    
    def get_history(self, profile_id: Optional[str] = None, limit: int = 50) -> List[ConfigHistory]:
        """Get configuration change history."""
        with self._get_session() as session:
            try:
                query = session.query(DBConfigHistory)
                if profile_id:
                    query = query.filter_by(profile_id=profile_id)
                
                db_entries = query.order_by(desc(DBConfigHistory.timestamp)).limit(limit).all()
                return [self._db_history_to_model(entry) for entry in db_entries]
                
            except SQLAlchemyError as e:
                logger.error(f"Database error getting history: {e}")
                raise StorageError(f"Database error: {e}")
    
    def get_history_entry(self, history_id: str) -> Optional[ConfigHistory]:
        """Get a specific history entry."""
        with self._get_session() as session:
            try:
                db_entry = session.query(DBConfigHistory).filter_by(id=history_id).first()
                return self._db_history_to_model(db_entry) if db_entry else None
            except SQLAlchemyError as e:
                logger.error(f"Database error getting history entry: {e}")
                raise StorageError(f"Database error: {e}")
    
    def cleanup_old_history(self, retention_days: int = 30, max_entries_per_profile: int = 100):
        """Clean up old history entries."""
        with self._get_session() as session:
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
                
                # Delete entries older than retention period
                deleted_count = session.query(DBConfigHistory).filter(
                    DBConfigHistory.timestamp < cutoff_date
                ).delete()
                
                # For each profile, keep only the latest N entries
                profiles = session.query(DBConfigProfile).all()
                for profile in profiles:
                    # Get history entries for this profile ordered by timestamp descending
                    entries = session.query(DBConfigHistory).filter_by(
                        profile_id=profile.id
                    ).order_by(desc(DBConfigHistory.timestamp)).all()
                    
                    # Delete entries beyond the limit
                    if len(entries) > max_entries_per_profile:
                        entries_to_delete = entries[max_entries_per_profile:]
                        for entry in entries_to_delete:
                            session.delete(entry)
                            deleted_count += 1
                
                session.commit()
                logger.info(f"Cleaned up {deleted_count} old history entries")
                return deleted_count
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error cleaning up history: {e}")
                raise StorageError(f"Database error: {e}")
    
    # Template Management Methods
    
    def create_template(self, request: TemplateCreateRequest) -> ConfigTemplate:
        """Create a new configuration template."""
        with self._get_session() as session:
            try:
                # Check if template already exists
                existing = session.query(DBConfigTemplate).filter_by(name=request.name).first()
                if existing:
                    raise StorageError(f"Template with name '{request.name}' already exists")
                
                # Create database template
                db_template = DBConfigTemplate(
                    name=request.name,
                    display_name=request.display_name,
                    description=request.description,
                    category=request.category.value,
                    config_data=request.config_data,
                    use_case=request.use_case,
                    estimated_cost=request.estimated_cost,
                    estimated_time=request.estimated_time,
                    is_builtin=False
                )
                
                session.add(db_template)
                session.commit()
                session.refresh(db_template)
                
                return self._db_template_to_model(db_template)
                
            except IntegrityError as e:
                session.rollback()
                raise StorageError(f"Template creation failed: {e}")
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error creating template: {e}")
                raise StorageError(f"Database error: {e}")
    
    def get_template(self, template_name: str) -> Optional[ConfigTemplate]:
        """Get a template by name."""
        with self._get_session() as session:
            try:
                db_template = session.query(DBConfigTemplate).filter_by(name=template_name).first()
                return self._db_template_to_model(db_template) if db_template else None
            except SQLAlchemyError as e:
                logger.error(f"Database error getting template: {e}")
                raise StorageError(f"Database error: {e}")
    
    def list_templates(self, category: Optional[str] = None) -> List[ConfigTemplate]:
        """List templates, optionally filtered by category."""
        with self._get_session() as session:
            try:
                query = session.query(DBConfigTemplate)
                if category:
                    query = query.filter_by(category=category)
                
                db_templates = query.order_by(DBConfigTemplate.display_name).all()
                return [self._db_template_to_model(t) for t in db_templates]
                
            except SQLAlchemyError as e:
                logger.error(f"Database error listing templates: {e}")
                raise StorageError(f"Database error: {e}")
    
    def delete_template(self, template_name: str) -> bool:
        """Delete a template (only custom templates)."""
        with self._get_session() as session:
            try:
                db_template = session.query(DBConfigTemplate).filter_by(name=template_name).first()
                if not db_template:
                    return False
                
                # Don't allow deletion of built-in templates
                if db_template.is_builtin:
                    raise StorageError("Cannot delete built-in template")
                
                session.delete(db_template)
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error deleting template: {e}")
                raise StorageError(f"Database error: {e}")
    
    # Backup and Restore Methods
    
    def create_backup(self, name: str, description: str = None) -> str:
        """Create a complete configuration backup."""
        with self._get_session() as session:
            try:
                # Collect all data for backup
                profiles = session.query(DBConfigProfile).all()
                templates = session.query(DBConfigTemplate).filter_by(is_builtin=False).all()
                settings = session.query(DBConfigSetting).all()
                
                backup_data = {
                    "profiles": [self._db_profile_to_dict(p) for p in profiles],
                    "templates": [self._db_template_to_dict(t) for t in templates],
                    "settings": {s.key: s.value for s in settings},
                    "created_at": datetime.utcnow().isoformat(),
                    "version": "1.0"
                }
                
                # Create backup entry
                db_backup = DBConfigBackup(
                    name=name,
                    description=description,
                    backup_data=backup_data,
                    file_size=len(json.dumps(backup_data))
                )
                
                session.add(db_backup)
                session.commit()
                session.refresh(db_backup)
                
                return db_backup.id
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error creating backup: {e}")
                raise StorageError(f"Database error: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        with self._get_session() as session:
            try:
                db_backups = session.query(DBConfigBackup).order_by(desc(DBConfigBackup.created_at)).all()
                return [
                    {
                        "id": backup.id,
                        "name": backup.name,
                        "description": backup.description,
                        "created_at": backup.created_at,
                        "file_size": backup.file_size
                    }
                    for backup in db_backups
                ]
            except SQLAlchemyError as e:
                logger.error(f"Database error listing backups: {e}")
                raise StorageError(f"Database error: {e}")
    
    def restore_backup(self, backup_id: str) -> bool:
        """Restore configuration from backup."""
        with self._get_session() as session:
            try:
                db_backup = session.query(DBConfigBackup).filter_by(id=backup_id).first()
                if not db_backup:
                    raise StorageError(f"Backup {backup_id} not found")
                
                backup_data = db_backup.backup_data
                
                # Clear existing data (except built-in templates)
                session.query(DBConfigProfile).delete()
                session.query(DBConfigTemplate).filter_by(is_builtin=False).delete()
                
                # Restore profiles
                for profile_data in backup_data.get("profiles", []):
                    db_profile = DBConfigProfile(**profile_data)
                    session.add(db_profile)
                
                # Restore custom templates
                for template_data in backup_data.get("templates", []):
                    db_template = DBConfigTemplate(**template_data)
                    session.add(db_template)
                
                # Restore settings
                for key, value in backup_data.get("settings", {}).items():
                    setting = session.query(DBConfigSetting).filter_by(key=key).first()
                    if setting:
                        setting.value = value
                    else:
                        session.add(DBConfigSetting(key=key, value=value))
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error restoring backup: {e}")
                raise StorageError(f"Database error: {e}")
    
    # Helper Methods
    
    def _add_history_entry(self, session: Session, profile_id: Optional[str], config_data: Dict[str, Any],
                          change_description: str, user_action: UserAction, 
                          changed_fields: List[str] = None, previous_config: Dict[str, Any] = None) -> DBConfigHistory:
        """Internal method to add history entry within a session."""
        history_entry = DBConfigHistory(
            profile_id=profile_id,
            config_data=config_data,
            change_description=change_description,
            changed_fields=changed_fields or [],
            user_action=user_action.value,
            previous_config=previous_config
        )
        session.add(history_entry)
        return history_entry
    
    def _find_config_changes(self, old_config: Dict[str, Any], new_config: Dict[str, Any], 
                           path: str = "") -> List[str]:
        """Find changed fields between two configurations."""
        changes = []
        
        def compare_recursive(old, new, current_path=""):
            if isinstance(old, dict) and isinstance(new, dict):
                all_keys = set(old.keys()) | set(new.keys())
                for key in all_keys:
                    key_path = f"{current_path}.{key}" if current_path else key
                    if key not in old:
                        changes.append(key_path)
                    elif key not in new:
                        changes.append(key_path)
                    else:
                        compare_recursive(old[key], new[key], key_path)
            elif old != new:
                changes.append(current_path)
        
        compare_recursive(old_config, new_config)
        return changes
    
    def _db_profile_to_model(self, db_profile: DBConfigProfile) -> ConfigProfile:
        """Convert database profile to Pydantic model."""
        return ConfigProfile(
            id=db_profile.id,
            name=db_profile.name,
            description=db_profile.description,
            config_data=db_profile.config_data,
            tags=db_profile.tags or [],
            is_default=db_profile.is_default,
            is_template=db_profile.is_template,
            is_active=db_profile.is_active,
            version=db_profile.version,
            created_at=db_profile.created_at,
            updated_at=db_profile.updated_at
        )
    
    def _db_history_to_model(self, db_history: DBConfigHistory) -> ConfigHistory:
        """Convert database history to Pydantic model."""
        return ConfigHistory(
            id=db_history.id,
            profile_id=db_history.profile_id,
            config_data=db_history.config_data,
            change_description=db_history.change_description,
            changed_fields=db_history.changed_fields or [],
            user_action=UserAction(db_history.user_action),
            previous_config=db_history.previous_config,
            timestamp=db_history.timestamp
        )
    
    def _db_template_to_model(self, db_template: DBConfigTemplate) -> ConfigTemplate:
        """Convert database template to Pydantic model."""
        from models.template_models import TemplateCategory, TemplateComplexity
        
        return ConfigTemplate(
            name=db_template.name,
            display_name=db_template.display_name,
            description=db_template.description,
            category=TemplateCategory(db_template.category),
            config_data=db_template.config_data,
            use_case=db_template.use_case,
            estimated_cost=db_template.estimated_cost,
            estimated_time=db_template.estimated_time,
            complexity=TemplateComplexity.BEGINNER,  # Default since not stored in DB yet
            prerequisites=[],  # Default since not stored in DB yet
            tags=[],  # Default since not stored in DB yet
            is_builtin=db_template.is_builtin,
            created_at=db_template.created_at,
            updated_at=db_template.updated_at
        )
    
    def _db_profile_to_dict(self, db_profile: DBConfigProfile) -> Dict[str, Any]:
        """Convert database profile to dictionary for backup."""
        return {
            "id": db_profile.id,
            "name": db_profile.name,
            "description": db_profile.description,
            "config_data": db_profile.config_data,
            "tags": db_profile.tags,
            "is_default": db_profile.is_default,
            "is_template": db_profile.is_template,
            "is_active": db_profile.is_active,
            "version": db_profile.version,
            "created_at": db_profile.created_at.isoformat(),
            "updated_at": db_profile.updated_at.isoformat()
        }
    
    def _db_template_to_dict(self, db_template: DBConfigTemplate) -> Dict[str, Any]:
        """Convert database template to dictionary for backup."""
        return {
            "name": db_template.name,
            "display_name": db_template.display_name,
            "description": db_template.description,
            "category": db_template.category,
            "config_data": db_template.config_data,
            "use_case": db_template.use_case,
            "estimated_cost": db_template.estimated_cost,
            "estimated_time": db_template.estimated_time,
            "is_builtin": db_template.is_builtin,
            "created_at": db_template.created_at.isoformat(),
            "updated_at": db_template.updated_at.isoformat()
        }