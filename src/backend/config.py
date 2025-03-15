"""Application configuration module.

This module contains all configuration settings for the application, including:
- Directory structures
- Flask settings
- Database settings
- File upload settings
- Vision processing settings
- Tag localization
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Set, Dict

logger = logging.getLogger(__name__)

class Config:
    """Application configuration class.
    
    All configuration settings are class attributes and can be accessed directly
    through the class without instantiation.
    """
    
    # Base paths
    BASE_DIR: Path = Path(__file__).parent
    RUNTIME_DIR: Path = BASE_DIR / 'runtime'
    
    # Runtime directory structure
    UPLOAD_FOLDER: Path = RUNTIME_DIR / 'uploads'
    LOG_DIR: Path = RUNTIME_DIR / 'logs'
    DB_DIR: Path = RUNTIME_DIR / 'db'
    
    # Flask configuration
    SECRET_KEY: str = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    DEBUG: bool = True
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI: str = os.environ.get('DATABASE_URL') or f'sqlite:///{DB_DIR}/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    
    # File upload configuration
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS: Set[str] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Vision configuration
    VISION_CONFIG: dict = {
        'yolo': {
            'model': 'yolov8n.pt',
            'confidence': 0.25
        },
        'ocr': {
            'languages': ['en', 'ru'],
            'confidence': 0.5
        }
    }
    
    # Spell checking configuration
    ENABLE_SPELL_CHECK=False

    # Tag translations
    TAG_TRANSLATIONS_FILE: Path = BASE_DIR / 'tag_translations.json'
    _tag_translations: Dict[str, Dict[str, str]] = {}
    
    @classmethod
    def init_runtime_dirs(cls) -> None:
        """Initialize all runtime directories.
        
        Creates the following directory structure if it doesn't exist:
        runtime/
        ├── db/       # Database files
        ├── logs/     # Application logs
        └── uploads/  # User uploaded files
        """
        dirs: List[Path] = [
            cls.RUNTIME_DIR,
            cls.UPLOAD_FOLDER,
            cls.LOG_DIR,
            cls.DB_DIR
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {dir_path}")
    
    @classmethod
    def cleanup_runtime_dirs(cls) -> None:
        """Clean up runtime directories.
        
        Removes all files from uploads directory and logs directory.
        Note: Database directory is not cleaned up to preserve data.
        """
        # Clean uploads
        for file in cls.UPLOAD_FOLDER.glob('*'):
            file.unlink()
            logger.debug(f"Removed upload file: {file}")
                
        # Clean logs
        for file in cls.LOG_DIR.glob('*.log'):
            file.unlink()
            logger.debug(f"Removed log file: {file}")
    
    @classmethod
    def load_tag_translations(cls) -> None:
        """Load tag translations from JSON file.
        
        The JSON file should have the format:
        {
            "person": {
                "en": "person",
                "ru": "человек",
                "jp": "人"
            },
            // ... more tags
        }
        """
        try:
            if cls.TAG_TRANSLATIONS_FILE.exists():
                with open(cls.TAG_TRANSLATIONS_FILE, 'r', encoding='utf-8') as f:
                    cls._tag_translations = json.load(f)
                    logger.debug(f"Loaded {len(cls._tag_translations)} tag translations")
        except Exception as e:
            logger.error(f"Could not load tag translations: {e}")
            cls._tag_translations = {}
    
    @classmethod
    def get_tag_translation(cls, tag: str, locale: str) -> str:
        """Get localized version of a tag.
        
        Args:
            tag: Original tag name (in English, from YOLO)
            locale: Target locale code (e.g., 'en', 'ru')
            
        Returns:
            Localized tag name or original tag if translation not found
        """
        if not cls._tag_translations:
            cls.load_tag_translations()
        
        tag = tag.lower()
        translations = cls._tag_translations.get(tag, {})
        return translations.get(locale, tag)