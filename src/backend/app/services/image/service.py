"""Image processing service.

This module provides functionality for:
- Image file handling and validation
- Vision processing integration
- Metadata management using ExifTool
"""

import os
import logging
from typing import List
from werkzeug.utils import secure_filename
from app.services.vision.processor import vision_processor
from config import Config
import json
from PIL import Image
import piexif
from app.models import DetectedObject, DetectedText, DetectionResult

logger = logging.getLogger('app.services.image')

class ProcessingResult:
    """Result of image processing"""
    def __init__(self, filename: str, objects: List[DetectedObject], texts: List[DetectedText]):
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
            logger.fatal(f"Failed to create upload directory {self.upload_folder}: {str(e)}")
            raise RuntimeError(f"Cannot initialize upload directory: {str(e)}")
        logger.info("ImageService initialized successfully.")

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

    def process_image_only(self, filepath: str) -> ProcessingResult:
        """Process image file with vision services without database operations
        
        Args:
            filepath (str): Path to the image file to process
            
        Returns:
            ProcessingResult with the results of the image processing
        """
        logger.info(f"Processing image: {filepath}")
        
        result = vision_processor.process_image(filepath)
        logger.debug(f"Vision processing results - Objects: {len(result.objects)}, Texts: {len(result.texts)}")
        
        self._update_image_metadata(filepath, result)

        filename = os.path.basename(filepath)
        
        return ProcessingResult(
            filename=filename,
            objects=result.objects,
            texts=result.texts
        )

    def _update_image_metadata(self, filepath: str, result: DetectionResult):
        """Update image metadata using PIL images library
        
        Args:
            filepath (str): Path to the image file to update
            result (DetectionResult): Combined detection results
            
        Note:
            This method saves results in metadata depending on file format.
        """
        try:
            objects = [obj.to_dict() for obj in result.objects]
            texts = [text.to_dict() for text in result.texts]
            
            _, ext = os.path.splitext(filepath)
            ext = ext.lower()

            image = Image.open(filepath)

            # Special case for the JPEG images
            if ext in ['.jpg', '.jpeg']:
                # Get current EXIF data
                exif_dict = piexif.load(filepath)
                
                metadata = json.dumps({
                    "objects": objects,
                    "texts": texts
                })

                # Add or update tag ExifComment
                user_comment = metadata.encode('utf-8')
                exif_dict['Exif'][piexif.ExifIFD.UserComment] = user_comment

                # Save EXIF tags into JPEG
                exif_bytes = piexif.dump(exif_dict)
                image.save(filepath, exif=exif_bytes)

            elif ext in ['.png', '.gif', '.webp']:
                image.info['text'] = json.dump(texts)
                image.info['objects'] = json.dump(objects)
                if (ext == '.png'):
                    image.save(filepath, pnginfo=image.info)
                elif (ext == '.gif'):
                    image.save(filepath, save_all=True)
                elif (ext == '.webp'):
                    image.save(filepath, **image.info)

            else:
                raise ValueError("Unsupported file format: {}".format(ext))
            logger.debug(f"Updated metadata for {filepath}")
            
        except Exception as e:
            logger.error(f"Could not update image metadata: {str(e)}", exc_info=True)

image_service = ImageService() 