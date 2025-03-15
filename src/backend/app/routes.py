"""API routes for the image processing application.

This module defines the REST API endpoints for:
- Image upload and processing
- Image search and retrieval
- Image download
- Search suggestions
- Image text retrieval
"""

from typing import Dict, Any, Tuple, List, Iterable
from flask import Blueprint, request, jsonify, send_file, Response, send_from_directory
import os
import logging
from werkzeug.utils import secure_filename
from app.services import image_service, image_repository
from app.models import Image
from config import Config
from pathlib import Path

logger = logging.getLogger(__name__)
main = Blueprint('main', __name__)

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
        
    # Ensure safe and unique filename
    filename, filepath = _ensure_unique_filename(
        secure_filename(file.filename), 
        Config.UPLOAD_FOLDER
    )
    
    file.save(filepath)
    result = image_service.process_image(filepath)
    
    return ok_response({
        "filename": filename,
        "id": result.id
    })

@main.route('/api/images', methods=['GET'])
def search_images():
    """Search images by tags or text."""
    query = request.args.get('q')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 12))
    locale = request.args.get('locale', 'en')
    
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
        logger.info(f"Getting available tags for locale: {locale}")
        
        tags = sorted(image_repository._tag_cache)
        response = [{
            'name': Config.get_tag_translation(tag, locale),
            'original_name': tag
        } for tag in tags]
        
        logger.info(f"Returning {len(tags)} tags")
        logger.debug(f"Tags response: {response}")
        
        return ok_response(response)
        
    except Exception as e:
        logger.error(f"Error in get_available_tags: {str(e)}", exc_info=True)
        return error_response(str(e), 500) 
    