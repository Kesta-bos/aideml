"""
Database initialization and migration utilities.
"""

import os
import logging
from pathlib import Path
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from database.models import Base, ConfigTemplate, ConfigSetting

logger = logging.getLogger("aide")


class DatabaseManager:
    """Database manager for AIDE ML configuration system."""
    
    def __init__(self, database_url: str = None):
        """Initialize database manager."""
        if database_url is None:
            # Default to SQLite in the backend directory
            db_path = Path(__file__).parent.parent / "data" / "aide_config.db"
            db_path.parent.mkdir(exist_ok=True)
            database_url = f"sqlite:///{db_path}"
        
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error creating database tables: {e}")
            return False
    
    def check_tables_exist(self) -> bool:
        """Check if all required tables exist."""
        try:
            inspector = inspect(self.engine)
            existing_tables = set(inspector.get_table_names())
            required_tables = {
                "config_profiles",
                "config_history", 
                "config_templates",
                "config_backups",
                "config_settings"
            }
            return required_tables.issubset(existing_tables)
        except SQLAlchemyError as e:
            logger.error(f"Error checking tables: {e}")
            return False
    
    def initialize_database(self):
        """Initialize database with tables and default data."""
        try:
            # Create tables if they don't exist
            if not self.check_tables_exist():
                self.create_tables()
            
            # Initialize default data
            self._initialize_default_data()
            
            logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return False
    
    def _initialize_default_data(self):
        """Initialize default templates and settings."""
        with self.SessionLocal() as session:
            try:
                # Check if templates already exist
                existing_templates = session.query(ConfigTemplate).filter_by(is_builtin=True).count()
                if existing_templates == 0:
                    # Load built-in templates with delayed import to avoid circular dependency
                    from services.template_service import TemplateService
                    template_service = TemplateService()
                    builtin_templates = template_service.get_builtin_templates()
                    
                    for template_data in builtin_templates:
                        template = ConfigTemplate(
                            name=template_data["name"],
                            display_name=template_data["display_name"],
                            description=template_data["description"],
                            category=template_data["category"],
                            config_data=template_data["config_data"],
                            use_case=template_data.get("use_case", ""),
                            estimated_cost=template_data.get("estimated_cost"),
                            estimated_time=template_data.get("estimated_time"),
                            is_builtin=True
                        )
                        session.add(template)
                    
                    logger.info(f"Added {len(builtin_templates)} built-in templates")
                
                # Initialize default settings
                default_settings = [
                    {
                        "key": "auto_save_history",
                        "value": True,
                        "description": "Automatically save configuration changes to history"
                    },
                    {
                        "key": "max_history_entries",
                        "value": 100,
                        "description": "Maximum number of history entries to keep per profile"
                    },
                    {
                        "key": "default_profile_name",
                        "value": "default",
                        "description": "Name of the default configuration profile"
                    },
                    {
                        "key": "backup_retention_days",
                        "value": 30,
                        "description": "Number of days to retain automatic backups"
                    }
                ]
                
                for setting_data in default_settings:
                    existing_setting = session.query(ConfigSetting).filter_by(key=setting_data["key"]).first()
                    if not existing_setting:
                        setting = ConfigSetting(**setting_data)
                        session.add(setting)
                
                session.commit()
                logger.info("Default settings initialized")
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Error initializing default data: {e}")
                raise
    
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection."""
        self.engine.dispose()


# Global database manager instance
db_manager = None


def get_database_manager() -> DatabaseManager:
    """Get or create global database manager instance."""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
        db_manager.initialize_database()
    return db_manager


def get_db_session():
    """Dependency to get database session for FastAPI."""
    db = get_database_manager()
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()