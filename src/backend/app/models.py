"""Database models for the application.

This module defines SQLAlchemy models for:
- Images
- Tags
- Detected objects
- Detected text
"""

from typing import Dict, Any, List, Set
from datetime import datetime
from app.services.database import db
from dataclasses import dataclass

# Association table for tags (many-to-many)
image_tags = db.Table(
    'image_tags',
    db.Column('image_id', db.Integer, db.ForeignKey('images.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Index('idx_image_tags_tag', 'tag_id'),  # Index for faster tag lookups
    db.Index('idx_image_tags_image', 'image_id')  # Index for faster image lookups
)

class Tag(db.Model):
    """Tag model for categorizing images."""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    images = db.relationship("Image", secondary=image_tags, back_populates="tags")

    def __init__(self, name: str) -> None:
        """Initialize a tag with a normalized name."""
        self.name = name.lower()

    def __repr__(self) -> str:
        return f'<Tag {self.name}>'

    @classmethod
    def get_or_create(cls, name: str, session) -> 'Tag':
        """Get an existing tag or create a new one.
        
        Args:
            name: The tag name to look up or create
            session: SQLAlchemy session to use
            
        Returns:
            An existing or new Tag instance
        """
        name = name.lower()
        tag = session.query(cls).filter_by(name=name).first()
        if tag is None:
            tag = cls(name=name)
            session.add(tag)
        return tag

    @classmethod
    def get_or_create_many(cls, names: List[str], session) -> List['Tag']:
        """Get or create multiple tags at once.
        
        Args:
            names: List of tag names to look up or create
            session: SQLAlchemy session to use
            
        Returns:
            List of Tag instances
        """
        tags = []
        for name in names:
            tags.append(cls.get_or_create(name, session))
        session.commit()
        return tags

class DetectedObject(db.Model):
    """Object detected by YOLO model"""
    __tablename__ = 'detected_objects'

    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False)
    image = db.relationship("Image", back_populates="objects")

    def __init__(self, class_name: str, confidence: float):
        self.class_name = class_name
        self.confidence = confidence
    
    def to_dict(self) -> dict:
        """Convert DetectedObject to a dictionary"""
        return {
            'class_name': self.class_name,
            'confidence': self.confidence
        }

class DetectedText(db.Model):
    """Text detected by OCR."""
    __tablename__ = 'detected_texts'
    __table_args__ = (
        db.Index('idx_texts_text', 'text'),  # Index for full text search
        db.Index('idx_texts_image', 'image_id')  # Index for image relationship
    )

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    bbox = db.Column(db.JSON, nullable=False)  # Stored as JSON array
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False)
    image = db.relationship("Image", back_populates="texts")

    def __init__(self, text: str, confidence: float, bbox: List[int]) -> None:
        """Initialize detected text with its properties."""
        self.text = text
        self.confidence = confidence
        self.bbox = bbox

    def to_dict(self) -> Dict[str, Any]:
        """Convert DetectedText to a dictionary for API responses."""
        return {
            'text': self.text,
            'confidence': self.confidence,
            'bbox': self.bbox
        }

@dataclass
class DetectionResult:
    """Combined result of image detection."""
    objects: List[DetectedObject]
    texts: List[DetectedText]

class Image(db.Model):
    """Processed image with its detection results."""
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    tags = db.relationship(
        "Tag", 
        secondary=image_tags, 
        back_populates="images"
    )
    objects = db.relationship(
        "DetectedObject", 
        back_populates="image", 
        cascade="all, delete-orphan"
    )
    texts = db.relationship(
        "DetectedText", 
        back_populates="image", 
        cascade="all, delete-orphan"
    )

    def __init__(self, filename: str) -> None:
        """Initialize an image.
        
        Args:
            filename: The filename to use (must be unique)
        """
        self.filename = filename

    def add_tags_from_objects(self, detected_objects: List[DetectedObject], session) -> None:
        """Add tags to the image based on detected objects.
        
        This method automatically creates tags from detected object classes
        and handles tag deduplication.
        
        Args:
            detected_objects: List of detected objects to create tags from
            session: SQLAlchemy session to use
        """
        # Get unique class names from objects
        unique_tags: Set[str] = {obj.class_name.lower() for obj in detected_objects}
        
        # Get or create tags and add them to the image
        for tag_name in unique_tags:
            tag = Tag.get_or_create(tag_name, session)
            if tag not in self.tags:  # Avoid duplicate tags
                self.tags.append(tag)
    
    @property
    def detection_summary(self) -> Dict[str, Any]:
        """Get a summary of detections for API responses."""
        return {
            'id': self.id,
            'filename': self.filename,
            'created_at': self.created_at.isoformat(),
            'tags': [{'name': tag.name, 'confidence': 1.0} for tag in self.tags],
            'objects': [obj.to_dict() for obj in self.objects],
            'texts': [text.to_dict() for text in self.texts]
        }