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
    _tag_cache: Set[str] = set()
    _is_tag_cache_initialized: bool = False
    
    def __init__(self):
        """Initialize repository with database session."""
        self.session: Session = SessionLocal()
        self.session.commit() # To ensure that we save the database file. 
        logger.info("ImageRepository initialized with database session")
    
    def _refresh_tag_cache(self) -> None:
        """Refresh the internal tag cache from the database."""
        try:
            self._tag_cache = {
                name for name in self.session.scalars(select(Tag.name)).all()
            }
            logger.debug(f"Tag cache refreshed with {len(self._tag_cache)} tags")
        except SQLAlchemyError as e:
            logger.error("Failed to refresh tag cache", exc_info=True)
            self._tag_cache = set()
    
    def _find_internal_tag(self, query: str, locale: str) -> str:
        """Find internal tag name from localized query.
        
        Args:
            query: Localized tag query
            locale: Language code
            
        Returns:
            Internal tag name or original query if no match found
        """
        if (not self._is_tag_cache_initialized):
            self._refresh_tag_cache()
            self._is_tag_cache_initialized = True
        return next(
            (tag for tag in self._tag_cache if Config.get_tag_translation(tag, locale).lower() == query.lower()),
            query.lower()
        )
    
    def save_image(self, filename: str, detected_objects: List[DetectedObject], texts: List[DetectedText]) -> Image:
        """Save image with its associated tags and detected texts.
        
        Args:
            filename: Name of the image file
            detected_objects: List of detected objects with their confidence scores
            texts: List of detected texts with their confidence scores and bounding boxes
            
        Returns:
            Image: Saved image instance with all relationships
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            image = Image(filename=filename)
            
            # Handle tags (convert detected objects to tags)
            unique_tags: Set[str] = {obj.class_name.lower() for obj in detected_objects}
            for tag_name in unique_tags:
                if tag_name not in self._tag_cache:
                    tag = Tag(name=tag_name)
                    self.session.add(tag)
                    self._tag_cache.add(tag_name)
                    logger.debug(f"Created new tag: {tag_name}")
                else:
                    tag = self.session.query(Tag).filter(Tag.name == tag_name).first()
                image.tags.append(tag)
            
            # Add texts
            image.texts = texts
            
            self.session.add(image)
            self.session.commit()
            
            logger.info(f"Saved image {filename} with {len(unique_tags)} tags and {len(texts)} text detections")
            return image
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to save image {filename}: {str(e)}", exc_info=True)
            raise

    def get_image_by_id(self, image_id: int) -> Optional[Image]:
        """Get image by ID with its tags and texts"""
        return self.session.get(Image, image_id)

    def search_images(self, query: str = None, page: int = 1, per_page: int = 12, locale: str = 'en') -> Tuple[List[Image], int]:
        """Search images by tags and text with optimized queries.
        
        Args:
            query: Search string (optional)
            page: Page number for pagination (default: 1)
            per_page: Number of items per page (default: 12)
            locale: Language code for tag search (default: 'en')
            
        Returns:
            Tuple[List[Image], int]: List of matching images and total count
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            if not query:
                # If no query, just return paginated images
                stmt = select(Image)
                total = self.session.scalar(select(func.count(Image.id)))
                images = self.session.scalars(
                    stmt.offset((page - 1) * per_page).limit(per_page)
                ).all()
                
                logger.debug(f"Retrieved {len(images)} images (page {page}, no query)")
                return images, total

            # Check if query is a tag search (starts with #)
            if query.startswith('#'):
                localized_query = query[1:].lower()
                internal_tag = self._find_internal_tag(localized_query, locale)
                
                stmt = (
                    select(Image)
                    .join(Image.tags)
                    .where(Tag.name == internal_tag)
                )
                logger.debug(f"Searching for tag: {internal_tag}")
            else:
                # Try tag match first
                internal_tag = self._find_internal_tag(query, locale)
                
                tag_stmt = (
                    select(Image)
                    .join(Image.tags)
                    .where(Tag.name == internal_tag)
                )
                
                # Then look for text matches
                text_stmt = (
                    select(Image)
                    .join(Image.texts)
                    .where(DetectedText.text.ilike(f'%{query}%'))
                )
                
                # Combine both queries
                stmt = tag_stmt.union(text_stmt)
                logger.debug(f"Searching for query: {query}")

            # Get total count
            total = self.session.scalar(
                select(func.count()).select_from(stmt.subquery())
            )

            # Apply pagination
            images = self.session.scalars(
                stmt.offset((page - 1) * per_page).limit(per_page)
            ).all()

            logger.debug(f"Found {total} images, returning page {page} ({len(images)} items)")
            return images, total
            
        except SQLAlchemyError as e:
            logger.error(f"Search failed for query '{query}': {str(e)}", exc_info=True)
            raise

    def get_suggestions(self, query: str, limit: int = 5, locale: str = 'en') -> List[str]:
        """Get optimized search suggestions.
        
        Args:
            query: Partial search query
            limit: Maximum number of suggestions to return (default: 5)
            locale: Language code for tag suggestions (default: 'en')
            
        Returns:
            List[str]: List of suggested search terms
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            if not query:
                return []

            if query.startswith('#'):
                # Only search tags for # queries
                query = query[1:].lower()
                # Filter cached tags that match the query
                matching_tags = [tag for tag in self._tag_cache 
                               if tag.startswith(query)][:limit]
                # Convert to localized versions
                suggestions = [f"#{Config.get_tag_translation(name, locale)}" 
                             for name in matching_tags]
                logger.debug(f"Found {len(suggestions)} tag suggestions for #{query}")
                return suggestions
            
            # Get tag suggestions from cache
            matching_tags = [tag for tag in self._tag_cache 
                           if tag.startswith(query.lower())][:limit]
            
            # Get text suggestions (only from start of words for better performance)
            text_stmt = (
                select(DetectedText.text)
                .where(DetectedText.text.ilike(f'% {query}%'))
                .distinct()
                .limit(limit)
            )
            
            suggestions = set()
            # Convert tags to localized versions
            suggestions.update(Config.get_tag_translation(name, locale) 
                            for name in matching_tags)
            suggestions.update(self.session.scalars(text_stmt).all())
            
            result = list(suggestions)[:limit]
            logger.debug(f"Found {len(result)} suggestions for query: {query}")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get suggestions for '{query}': {str(e)}", exc_info=True)
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