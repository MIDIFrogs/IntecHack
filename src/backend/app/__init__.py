"""Flask application factory module.

This module initializes the Flask application and its extensions,
sets up the database, and registers blueprints.
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from config import Config
from app.services.database import db, init_database, verify_database_setup

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def init_app():
    """Initialize and configure the Flask application.
    
    Returns:
        Flask: The configured Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Ensure instance directories exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    # Verify database setup
    verify_database_setup(app.config['SQLALCHEMY_DATABASE_URI'])
    
    # Initialize extensions
    CORS(app)  # Enable CORS for all routes
    init_database(app)  # Initialize database and create tables
    
    # Register blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app