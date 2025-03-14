"""Database initialization and management module.

This module handles:
- Database setup and verification
- Model registration
- Table creation
"""

import logging
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

logger = logging.getLogger(__name__)

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def init_database(app) -> None:
    """Initialize database with the application.
    
    This function:
    1. Initializes SQLAlchemy with the app
    2. Imports all models
    3. Creates database tables
    
    Args:
        app: Flask application instance
    """
    logger.info("Initializing database...")
    
    # Initialize SQLAlchemy with app
    db.init_app(app)
    
    # Import all models to register them with SQLAlchemy
    logger.debug("Importing database models...")
    from app.models import Image, Tag, DetectedObject, DetectedText
    
    # Create database tables
    with app.app_context():
        logger.info("Creating database tables...")
        try:
            db.create_all()
            # Log created tables
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"Created tables: {tables}")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}", exc_info=True)
            raise

def verify_database_setup(db_uri: str) -> None:
    """Verify database setup and permissions.
    
    Args:
        db_uri: Database URI from configuration
    """
    logger.info("Verifying database setup...")
    
    # Handle SQLite database
    if db_uri.startswith('sqlite:///'):
        db_file = db_uri.replace('sqlite:///', '')
        db_path = Path(db_file)
        
        # Ensure database directory exists
        db_dir = db_path.parent
        if not db_dir.exists():
            logger.info(f"Creating database directory: {db_dir}")
            db_dir.mkdir(parents=True, exist_ok=True)
        
        # Verify directory permissions
        try:
            test_file = db_dir / '.test_write'
            test_file.touch()
            test_file.unlink()
            logger.debug("Database directory is writable")
        except Exception as e:
            logger.error(f"Database directory is not writable: {e}")
            raise
        
        # Create empty database file if needed
        if not db_path.exists():
            logger.info(f"Creating empty database file: {db_path}")
            try:
                db_path.touch()
                logger.debug("Database file created successfully")
            except Exception as e:
                logger.error(f"Failed to create database file: {e}")
                raise
    
    logger.info("Database setup verified successfully") 