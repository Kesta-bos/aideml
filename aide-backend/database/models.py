"""
SQLAlchemy database models for AIDE ML configuration profiles.
"""

from sqlalchemy import Column, String, JSON, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()


def generate_uuid():
    """Generate a UUID string."""
    return str(uuid.uuid4())


class ConfigProfile(Base):
    """Configuration profile model."""
    __tablename__ = "config_profiles"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    config_data = Column(JSON, nullable=False)
    tags = Column(JSON, default=list)  # Stored as JSON array
    is_default = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship to history
    history_entries = relationship("ConfigHistory", back_populates="profile", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ConfigProfile(id='{self.id}', name='{self.name}', is_default={self.is_default})>"


class ConfigHistory(Base):
    """Configuration change history model."""
    __tablename__ = "config_history"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    profile_id = Column(String, ForeignKey("config_profiles.id"), nullable=True)  # Can be null for system-wide changes
    config_data = Column(JSON, nullable=False)
    change_description = Column(Text, nullable=False)
    changed_fields = Column(JSON, default=list)  # List of changed field paths
    user_action = Column(String(100), nullable=False)  # "manual_edit", "template_apply", "import", etc.
    previous_config = Column(JSON)  # Store previous config for rollback
    timestamp = Column(DateTime, default=func.now())
    
    # Relationship to profile
    profile = relationship("ConfigProfile", back_populates="history_entries")
    
    def __repr__(self):
        return f"<ConfigHistory(id='{self.id}', action='{self.user_action}', timestamp='{self.timestamp}')>"


class ConfigTemplate(Base):
    """Configuration template model."""
    __tablename__ = "config_templates"
    
    name = Column(String(100), primary_key=True)  # Template identifier
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)  # "quick_experiment", "cost_optimized", etc.
    config_data = Column(JSON, nullable=False)
    use_case = Column(Text)
    estimated_cost = Column(String(50))  # e.g., "$1-5", "Low", etc.
    estimated_time = Column(String(50))  # e.g., "5-10 minutes", "Fast", etc.
    is_builtin = Column(Boolean, default=False)  # Whether it's a built-in template
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ConfigTemplate(name='{self.name}', category='{self.category}')>"


class ConfigBackup(Base):
    """Configuration backup model."""
    __tablename__ = "config_backups"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    backup_data = Column(JSON, nullable=False)  # Contains all profiles and current config
    created_at = Column(DateTime, default=func.now())
    file_path = Column(String(500))  # Optional file system path for large backups
    file_size = Column(Integer)  # Size in bytes
    
    def __repr__(self):
        return f"<ConfigBackup(id='{self.id}', name='{self.name}', created_at='{self.created_at}')>"


class ConfigSetting(Base):
    """Global configuration settings model."""
    __tablename__ = "config_settings"
    
    key = Column(String(100), primary_key=True)
    value = Column(JSON)
    description = Column(Text)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ConfigSetting(key='{self.key}', value='{self.value}')>"