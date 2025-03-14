from ultralytics import YOLO
import easyocr
from PIL import Image
import os
from config import Config

# Initialize YOLO model
yolo_model = YOLO('yolov8n.pt')

# Initialize EasyOCR
reader = easyocr.Reader(['en'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def process_image(image_path):
    """
    Process image using YOLOv8 and EasyOCR
    Returns tuple of (tags, detected_text)
    """
    # Run YOLOv8 detection
    results = yolo_model(image_path)
    
    # Extract tags from YOLO results
    tags = []
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = result.names[class_id]
            tags.append((class_name, confidence))
    
    # Run EasyOCR
    ocr_results = reader.readtext(image_path)
    
    # Extract text from OCR results
    detected_text = []
    for (bbox, text, conf) in ocr_results:
        detected_text.append((text, conf, bbox))
    
    return tags, detected_text 