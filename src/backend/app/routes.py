"""API routes for the image processing application.

This module defines the REST API endpoints for:
- Image upload and processing
- Image search and retrieval
- Image download
- Search suggestions
- Image text retrieval
"""

from typing import Any, Tuple
from flask import Blueprint, request, jsonify, Response, send_from_directory, send_file
import os
import logging
from werkzeug.utils import secure_filename
from app.services import image_service, image_repository
from config import Config
from pathlib import Path
from threading import Lock
from PIL import Image as PILImage
import io
import cv2
import imutils

logger = logging.getLogger(__name__)
main = Blueprint('main', __name__)

db_lock = Lock()

def error_response(message: str, status_code: int = 500) -> Tuple[Response, int]:
    """Create a JSON error response.
    
    Args:
        message: Error message to return
        status_code: HTTP status code (default: 500)
        
    Returns:
        Tuple of (response, status_code)
    """
    logger.error(f"Error: {message}")
    return jsonify({'error': message}), status_code

def ok_response(response: Any) -> Tuple[Response, int]:
    """Create a JSON success response.
    
    Args:
        response: Success response to return
        
    Returns:
        Tuple of (response, status_code)
    """
    logger.info(f"Success: {response}")
    return jsonify(response), 200

def _ensure_unique_filename(original_filename: str, upload_dir: Path) -> Tuple[str, str]:
    """Generate a unique filename and path for an uploaded file.
    
    This function ensures both the filename in the uploads directory
    and the filename stored in the database are unique.
    
    Args:
        original_filename: Original name of the uploaded file
        upload_dir: Directory where the file will be stored
        
    Returns:
        Tuple[str, str]: (unique_filename, unique_filepath)
        - unique_filename: Name to store in database
        - unique_filepath: Full path where file should be saved
    """
    name, ext = os.path.splitext(original_filename)
    counter = 1
    unique_filename = original_filename
    unique_filepath = upload_dir / unique_filename
    
    while unique_filepath.exists():
        unique_filename = f"{name}_{counter}{ext}"
        unique_filepath = upload_dir / unique_filename
        counter += 1
        
    logger.debug(f"Generated unique filename: {unique_filename} for {original_filename}")
    return unique_filename, str(unique_filepath)

@main.route('/api/upload', methods=['POST'])
def upload_image():
    """Upload and process an image."""
    if 'file' not in request.files:
        return error_response('No file provided', 400)
        
    file = request.files['file']
    if not file or not file.filename:
        return error_response('Invalid file', 400)
    
    try:
        filename, filepath = _ensure_unique_filename(secure_filename(file.filename), Config.UPLOAD_FOLDER)
        
        file.save(filepath)
        processing_result = image_service.process_image_only(filepath)
        
        with db_lock:
            logger.debug("Acquiring lock for database operations")
            image = image_repository.save_image(
                filename=processing_result.filename,
                detected_objects=processing_result.objects,
                texts=processing_result.texts
            )
            logger.debug("Released lock after database operations")
            
        return ok_response({
            "filename": filename,
            "id": image.id
        })
            
    # Remove up the file if there was an error
    except Exception as e:
        logger.error(f"Error during image upload:", e)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as cleanup_error:
            logger.error(f"Failed to clean up file after error: {cleanup_error}")
        return error_response(f"Failed to process image: {str(e)}", 500)

@main.route('/api/images', methods=['GET'])
def search_images():
    """Search images by tags or text."""
    query = request.args.get('q')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 12))
    locale = request.args.get('locale', 'en')
    
    with db_lock:
        images, total = image_repository.search_images(
            query=query, 
            page=page, 
            per_page=per_page,
            locale=locale
        )
    
    return ok_response({
        'images': [img.detection_summary for img in images],
        'total': total,
        'page': page,
        'per_page': per_page
    })

@main.route('/api/images/<int:image_id>', methods=['GET'])
def get_image(image_id: int):
    """Get image details by ID."""
    with db_lock:
        image = image_repository.get_image_by_id(image_id)
        if not image:
            return error_response('Image not found', 404)
        
        return ok_response(image.detection_summary)

@main.route('/api/images/<int:image_id>/file', methods=['GET'])
def get_image_file(image_id: int):
    """Get image file by ID."""
    image = image_repository.get_image_by_id(image_id)
    if not image:
        return error_response('Image not found', 404)
        
    return send_from_directory(Config.UPLOAD_FOLDER, image.filename)

@main.route('/api/images/<int:image_id>/text', methods=['GET'])
def get_image_text(image_id: int):
    """Get detected text for an image."""
    with db_lock:
        texts = image_repository.get_image_text(image_id)
        if texts is None:
            return error_response('Image not found', 404)
        
        return ok_response([text.to_dict() for text in texts])

@main.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Get search suggestions."""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 5))
    locale = request.args.get('locale', 'en')
    
    with db_lock:
        suggestions = image_repository.get_suggestions(
            query=query,
            limit=limit,
            locale=locale
        )
    
    return ok_response(suggestions)

@main.route('/api/tags', methods=['GET'])
def get_available_tags() -> Tuple[Response, int]:
    """Get all available tags with their translations.
    
    Query Parameters:
        locale (str): Language code for tag translations (default: 'en')
        
    Returns:
        JSON array of tag objects with original and translated names
    """
    try:
        locale = request.args.get('locale', 'en')
        
        with db_lock:
            tags = sorted(image_repository.get_all_tags())
            response = [{
                'name': Config.get_tag_translation(tag, locale),
                'original_name': tag
            } for tag in tags]
        
        return ok_response(response)
        
    except Exception as e:
        logger.error(f"Error in get_available_tags:", e)
        return error_response(str(e), 500)

@main.route('/api/images/<int:image_id>/download', methods=['GET'])
def download_image(image_id: int):
    """Download original image file."""
    image = image_repository.get_image_by_id(image_id)
    if not image:
        return error_response('Image not found', 404)
        
    return send_from_directory(
        Config.UPLOAD_FOLDER, 
        image.filename,
        as_attachment=True,
        download_name=image.filename
    )

@main.route('/api/images/<int:image_id>/thumbnail', methods=['GET'])
def get_image_thumbnail(image_id: int):
    """Get image thumbnail."""
    image = image_repository.get_image_by_id(image_id)
    if not image:
        return error_response('Image not found', 404)
        
    try:
        # Read image with OpenCV
        image_path = os.path.join(Config.UPLOAD_FOLDER, image.filename)
        img = cv2.imread(image_path)
        if img is None:
            return error_response('Failed to read image', 500)
            
        # Resize maintaining aspect ratio
        img = imutils.resize(img, width=300)
        
        # Encode to JPEG
        _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        img_bytes = io.BytesIO(buffer)
        
        return send_file(
            img_bytes,
            mimetype='image/jpeg',
            download_name=f"thumb_{image.filename}",
            max_age=86400  # Cache for 24 hours
        )
            
    except Exception as e:
        logger.error(f"Error generating thumbnail: {str(e)}", exc_info=True)
        return error_response('Error generating thumbnail', 500) 
    