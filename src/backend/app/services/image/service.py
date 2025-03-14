"""Image processing service.

This module provides functionality for:
- Image file handling and validation
- Vision processing integration
- Metadata management using ExifTool
"""

import os
import logging
from typing import Dict, Any, List
from werkzeug.utils import secure_filename
from app.services.vision.processor import vision_processor
from app.services.database.repository import image_repository
from config import Config
import json
#import exiftool
from datetime import datetime
from app.models import DetectedObject, DetectedText, DetectionResult

logger = logging.getLogger('app.services.image')

class ProcessingResult:
    """Result of image processing"""
    def __init__(self, id: int, filename: str, objects: List[DetectedObject], texts: List[DetectedText]):
        self.id = id
        self.filename = filename
        self.objects = objects
        self.texts = texts


class ImageService:
    """Service for handling image processing and metadata"""
    
    def __init__(self):
        self.upload_folder = Config.UPLOAD_FOLDER
        try:
            os.makedirs(self.upload_folder, exist_ok=True)
            logger.info(f"Upload directory initialized: {self.upload_folder}")
        except Exception as e:
            logger.critical(f"Failed to create upload directory {self.upload_folder}: {str(e)}")
            raise RuntimeError(f"Cannot initialize upload directory: {str(e)}")

        #self.et = exiftool.ExifToolHelper()
        logger.info("ImageService initialized with ExifTool")

    def is_allowed_file(self, filename: str) -> bool:
        """Check if file has an allowed extension
        
        Args:
            filename (str): Name of the file to check
            
        Returns:
            bool: True if file extension is in ALLOWED_EXTENSIONS, False otherwise
        """
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

    def save_image_file(self, file) -> str:
        """Save image file to upload directory
        
        Args:
            file: File-like object with 'filename' attribute and 'save' method (typically from Flask's request.files)
            
        Returns:
            str: Absolute path to the saved file
            
        Note:
            The filename will be sanitized using werkzeug.secure_filename
        """
        filename = secure_filename(file.filename)
        filepath = os.path.join(self.upload_folder, filename)
        file.save(filepath)
        logger.info(f"Saved image file: {filepath}")
        return filepath

    def process_image(self, filepath: str) -> ProcessingResult:
        """Process image file with vision services and save results
        
        Args:
            filepath (str): Path to the image file to process
            
        Returns:
            An instance of ProcessingResult with the results of the image processing
        """
        logger.info(f"Processing image: {filepath}")
        
        result = vision_processor.process_image(filepath)
        logger.debug(f"Vision processing results - Objects: {len(result.objects)}, Texts: {len(result.texts)}")
        
        filename = os.path.basename(filepath)
        
        image = image_repository.save_image(filename, result.objects, result.texts)
        logger.debug(f"Saved image to database with ID: {image.id}")
        
        self._update_image_metadata(filepath, result)
        
        return ProcessingResult(
            id=image.id,
            filename=filename,
            objects=result.objects,
            texts=result.texts
        )

    def _get_metadata_dict(self, result: DetectionResult) -> Dict[str, Any]:
        """Convert detection results to a metadata dictionary suitable for ExifTool
        
        Args:
            result (DetectionResult): Combined detection results
            
        Returns:
            Dict[str, Any]: Metadata dictionary containing:
                - XMP tags for structured data storage
                - IPTC tags for searchable keywords
                - EXIF tags for basic compatibility
                - File modification timestamp
        """
        object_tags = [f"{obj.class_name}({obj.confidence:.2f})" for obj in result.objects]
        text_content = [f"{text.text}({text.confidence:.2f})" for text in result.texts]
        
        # Return a dictionary of tags to save in metadata with all the values for the current detection result
        return {
            'XMP:DetectedObjects': json.dumps([obj.to_dict() for obj in result.objects]),
            'XMP:DetectedTexts': json.dumps([text.to_dict() for text in result.texts]),
            
            'IPTC:Keywords': object_tags,
            'IPTC:Caption-Abstract': '; '.join(text_content),
            
            'EXIF:ImageDescription': f"Objects: {', '.join(object_tags)}; Texts: {', '.join(text_content)}",
            'EXIF:UserComment': json.dumps(result.to_dict()),
            
            'FileModifyDate': datetime.now().strftime('%Y:%m:%d %H:%M:%S')
        }

    def _update_image_metadata(self, filepath: str, result: DetectionResult):
        """Update image metadata using ExifTool
        
        Args:
            filepath (str): Path to the image file to update
            result (DetectionResult): Combined detection results
            
        Note:
            This method writes metadata in multiple formats:
            - XMP for structured data
            - IPTC for searchable keywords
            - EXIF for basic compatibility
        """
        try:
            metadata = self._get_metadata_dict(result)
            self.et.set_tags(filepath, metadata)
            logger.debug(f"Updated metadata for {filepath}")
            
        except Exception as e:
            logger.error(f"Could not update image metadata: {str(e)}", exc_info=True)

    def get_image_metadata(self, filepath: str) -> DetectionResult:
        """Read image metadata using ExifTool
        
        Args:
            filepath (str): Path to the image file to read metadata from
            
        Returns:
            DetectionResult: Combined detection results containing detected objects and texts
                
        Note:
            Returns empty DetectionResult if no metadata is found or if metadata cannot be read
        """
        try:
            metadata = self.et.get_metadata(filepath)[0]
            logger.debug(f"Read metadata from {filepath}")
            
            for key in ('XMP:DetectedObjects', 'EXIF:UserComment'):
                if key in metadata:
                    try:
                        data = json.loads(metadata[key])
                        if isinstance(data, dict) and 'objects' in data and 'texts' in data:
                            return DetectionResult.from_dict(data)
                        return DetectionResult(
                            objects=[DetectedObject.from_dict(obj) for obj in data],
                            texts=[DetectedText.from_dict(text) for text in json.loads(metadata.get('XMP:DetectedTexts', '[]'))]
                        )
                    except:
                        continue
            
            logger.warning(f"No metadata found for {filepath}")
            return DetectionResult(objects=[], texts=[])
            
        except Exception as e:
            logger.error(f"Could not read image metadata: {str(e)}", exc_info=True)
            return DetectionResult(objects=[], texts=[])

image_service = ImageService() 