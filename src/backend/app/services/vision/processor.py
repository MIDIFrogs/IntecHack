"""Vision processing service module.

This module provides functionality for:
- Object detection using YOLO
- Text detection using EasyOCR
- Combined image processing
"""

import logging
from pathlib import Path
from typing import List, Optional
from ultralytics import YOLO
import easyocr
from app.models import DetectedText, DetectedObject, DetectionResult
from config import Config

logger = logging.getLogger(__name__)

class VisionProcessor:
    """Service for handling all vision-related processing.
    
    This class provides a unified interface for all computer vision tasks,
    including object detection and text recognition. It uses lazy loading
    for models to optimize memory usage.
    
    Attributes:
        _yolo_model: Cached YOLO model instance
        _ocr_reader: Cached EasyOCR reader instance
    """
    
    def __init__(self) -> None:
        """Initialize vision processor with lazy-loaded models."""
        self._yolo_model: Optional[YOLO] = None
        self._ocr_reader: Optional[easyocr.Reader] = None
    
    @property
    def yolo_model(self) -> YOLO:
        """Get or initialize YOLO model.
        
        Returns:
            YOLO: Initialized YOLO model instance
            
        Raises:
            RuntimeError: If model initialization fails
        """
        if self._yolo_model is None:
            try:
                logger.info("Initializing YOLO model...")
                self._yolo_model = YOLO(Config.VISION_CONFIG['yolo']['model'])
                logger.info("YOLO model initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize YOLO model: {e}")
                raise RuntimeError(f"Failed to initialize YOLO model: {e}")
        return self._yolo_model
    
    @property
    def ocr_reader(self) -> easyocr.Reader:
        """Get or initialize OCR reader.
        
        Returns:
            easyocr.Reader: Initialized EasyOCR reader instance
            
        Raises:
            RuntimeError: If reader initialization fails
        """
        if self._ocr_reader is None:
            try:
                logger.info("Initializing EasyOCR reader...")
                self._ocr_reader = easyocr.Reader(Config.VISION_CONFIG['ocr']['languages'])
                logger.info("EasyOCR reader initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR reader: {e}")
                raise RuntimeError(f"Failed to initialize EasyOCR reader: {e}")
        return self._ocr_reader

    def get_objects(self, image_path: str) -> List[DetectedObject]:
        """Detect objects in image using YOLOv8.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of DetectedObject instances with class names and confidence scores
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            RuntimeError: If object detection fails
        """
        image_path = Path(image_path)
        if not image_path.exists():
            logger.error(f"Image not found: {image_path}")
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            logger.debug(f"Running object detection on {image_path}")
            results = self.yolo_model(str(image_path))
            objects = []
            
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = result.names[class_id]
                    
                    objects.append(DetectedObject(
                        class_name=class_name.lower(),  # Normalize to match Tag model
                        confidence=confidence
                    ))
            
            logger.info(f"Detected {len(objects)} objects in {image_path}")
            return objects
            
        except Exception as e:
            logger.error(f"Object detection failed for {image_path}: {e}")
            raise RuntimeError(f"Object detection failed: {e}")

    def get_text(self, image_path: str) -> List[DetectedText]:
        """Detect text in image using EasyOCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of DetectedText instances with text, confidence, and bounding boxes
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            RuntimeError: If text detection fails
        """
        image_path = Path(image_path)
        if not image_path.exists():
            logger.error(f"Image not found: {image_path}")
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            logger.debug(f"Running text detection on {image_path}")
            ocr_results = self.ocr_reader.readtext(str(image_path))
            texts = []
            
            for bbox, text, conf in ocr_results:
                # Convert bbox to flat list of integers for JSON storage
                flat_bbox = [int(coord) for point in bbox for coord in point]
                texts.append(DetectedText(
                    text=text,
                    confidence=conf,
                    bbox=flat_bbox
                ))
            
            logger.info(f"Detected {len(texts)} text regions in {image_path}")
            return texts
            
        except Exception as e:
            logger.error(f"Text detection failed for {image_path}: {e}")
            raise RuntimeError(f"Text detection failed: {e}")

    def process_image(self, image_path: str) -> DetectionResult:
        """Process image using both object detection and OCR.
        
        This method combines both object and text detection into a single
        operation, providing a complete analysis of the image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            DetectionResult containing lists of detected objects and texts
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            RuntimeError: If processing fails
        """
        image_path = Path(image_path)
        if not image_path.exists():
            logger.error(f"Image not found: {image_path}")
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            logger.info(f"Starting image processing for {image_path}")
            objects = self.get_objects(str(image_path))
            texts = self.get_text(str(image_path))
            
            logger.info(f"Completed processing {image_path}: {len(objects)} objects, {len(texts)} texts")
            return DetectionResult(objects=objects, texts=texts)
            
        except Exception as e:
            logger.error(f"Image processing failed for {image_path}: {e}")
            raise RuntimeError(f"Image processing failed: {e}")

# Create a singleton instance
vision_processor = VisionProcessor() 