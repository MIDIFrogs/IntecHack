"""Database repository for image metadata.

This module provides database operations for:
- Storing and retrieving images
- Managing tags and detected texts
- Searching and suggestions
"""

import logging
from typing import List, Optional, Tuple, Set, Dict
from sqlalchemy import select, func, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import Image, DetectedText, Tag, DetectedObject
from config import Config

logger = logging.getLogger('app.services.database')

# Setup DB engine and session
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class ImageRepository:
    """Repository for handling all database operations related to images.
    
    This class provides an interface for all database operations,
    including image storage, retrieval, and search functionality.
    """
    
    def __init__(self):
        """Initialize repository with database session."""
        self.session: Session = SessionLocal()
        self.session.commit() # To ensure that we save the database file. 
        logger.info("ImageRepository initialized with database session")
    
    def _find_internal_tag(self, query: str, locale: str) -> str:
        """Find internal tag name from localized query.
        
        Args:
            query: Localized tag query
            locale: Language code
            
        Returns:
            Internal tag name or original query if no match found
        """
        # Get all tags that match when translated
        tag_statement = select(Tag.name)
        all_tags = self.session.scalars(tag_statement).all()
        
        # Find first tag that matches when translated
        return next(
            (tag for tag in all_tags 
             if Config.get_tag_translation(tag, locale).lower() == query.lower()),
            query.lower()
        )
    
    def save_image(self, filename: str, detected_objects: List[DetectedObject], texts: List[DetectedText]) -> Image:
        """Save image with its detections."""
        try:
            image = Image(filename=filename)
            image.objects = detected_objects
            image.add_tags_from_objects(detected_objects, self.session)
            image.texts = texts
            
            self.session.add(image)
            self.session.commit()
            
            logger.info(f"Saved image {filename} with {len(image.tags)} tags")
            return image
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to save image {filename}", exc_info=True)
            raise

    def get_image_by_id(self, image_id: int) -> Optional[Image]:
        """Get image by ID."""
        return self.session.get(Image, image_id)

    def search_images(self, query: str = None, page: int = 1, per_page: int = 12, locale: str = 'en') -> Tuple[List[Image], int]:
        """Search images by tags and text."""
        try:
            if not query:
                # Return paginated images
                images = select(Image)
                total = self.session.scalar(select(func.count(Image.id)))
                images = self.session.scalars(
                    images.offset((page - 1) * per_page).limit(per_page)
                ).all()
                return images, total

            if query.startswith('#'):
                # Tag search
                internal_tag = self._find_internal_tag(query[1:].lower(), locale)
                images = (
                    select(Image)
                    .join(Image.tags)
                    .where(Tag.name == internal_tag)
                )
            else:
                # Combined tag and text search
                internal_tag = self._find_internal_tag(query, locale)
                tag_query = (
                    select(Image)
                    .join(Image.tags)
                    .where(Tag.name == internal_tag)
                )
                text_query = (
                    select(Image)
                    .join(Image.texts)
                    .where(DetectedText.text.ilike(f'%{query}%'))
                )
                images = tag_query.union(text_query)

            total = self.session.scalar(
                select(func.count()).select_from(images.subquery())
            )
            images = self.session.scalars(
                images.offset((page - 1) * per_page).limit(per_page)
            ).all()

            return images, total
            
        except SQLAlchemyError as e:
            logger.error(f"Search failed: {query}", exc_info=True)
            raise

    def get_suggestions(self, query: str, limit: int = 5, locale: str = 'en') -> List[str]:
        """Get search suggestions."""
        try:
            if not query:
                return []

            suggestions = set()
            
            if query.startswith('#'):
                # Tag suggestions
                query = query[1:].lower()
                tags = select(Tag.name).where(Tag.name.ilike(f'{query}%')).limit(limit)
                matching_tags = self.session.scalars(tags).all()
                suggestions.update(
                    f"#{Config.get_tag_translation(name, locale)}" 
                    for name in matching_tags
                )
            else:
                # Combined tag and text suggestions
                tags = select(Tag.name).where(Tag.name.ilike(f'{query.lower()}%')).limit(limit)
                texts = (
                    select(DetectedText.text)
                    .where(DetectedText.text.ilike(f'% {query}%'))
                    .distinct()
                    .limit(limit)
                )
                
                matching_tags = self.session.scalars(tags).all()
                suggestions.update(
                    Config.get_tag_translation(name, locale) 
                    for name in matching_tags
                )
                suggestions.update(self.session.scalars(texts).all())
            
            return list(suggestions)[:limit]
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get suggestions", exc_info=True)
            raise

    def get_image_text(self, image_id: int) -> Optional[List[DetectedText]]:
        """Get all text detections for an image.
        
        Args:
            image_id: ID of the image to get text for
            
        Returns:
            Optional[List[DetectedText]]: List of detected texts sorted by confidence,
            or None if image not found
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            image = self.session.get(Image, image_id)
            if not image:
                logger.debug(f"Image {image_id} not found")
                return None
                
            # Sort texts by confidence for better UX
            sorted_texts = sorted(image.texts, key=lambda t: t.confidence, reverse=True)
            logger.debug(f"Retrieved {len(sorted_texts)} texts for image {image_id}")
            return sorted_texts
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get texts for image {image_id}: {str(e)}", exc_info=True)
            raise

# Create a singleton instance
image_repository = ImageRepository() 