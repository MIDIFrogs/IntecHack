"""API routes for the image processing application.

This module defines the REST API endpoints for:
- Image upload and processing
- Image search and retrieval
- Image download
- Search suggestions
- Image text retrieval
"""

from typing import Dict, Any, Tuple, List, Iterable
from flask import Blueprint, request, jsonify, send_file, Response
import os
import logging
from werkzeug.utils import secure_filename
from app.services import image_service, image_repository
from app.models import Image
from config import Config

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
    return jsonify({'error': message}), status_code

def ok_response(response: Any) -> Tuple[Response, int]:
    """Create a JSON success response.
    
    Args:
        response: Success response to return
        
    Returns:
        Tuple of (response, status_code)
    """
    return jsonify(response), 200

def _format_image(img: Image, locale: str = 'en') -> Dict[str, Any]:
    """Format an image model for JSON response.
    
    Args:
        img: Image model instance
        locale: Language code for tag translations (default: 'en')
        
    Returns:
        Dictionary with formatted image data
    """
    summary = img.detection_summary()
    # Add translations to tags in the summary
    summary['tags'] = [{
        'name': Config.get_tag_translation(tag['name'], locale),
        'original_name': tag['name'],
        'confidence': tag['confidence']
    } for tag in summary['tags']]
    return summary

@main.route('/api/upload', methods=['POST'])
def upload_image() -> Tuple[Response, int]:
    """Handle image upload and processing.
    
    Expects a file in the request with key 'file'.
    Processes the image for object detection and text recognition.
    
    Returns:
        JSON response with:
        - On success: message and image ID
        - On failure: error message and appropriate status code
    """
    try:
        logger.info("Received image upload request")
        
        if 'file' not in request.files:
            logger.warning("No file found in request")
            return error_response('No file part', 400)
        
        file = request.files['file']
        if file.filename == '':
            logger.warning("Empty filename received")
            return error_response('No selected file', 400)
        
        if file and image_service.is_allowed_file(file.filename):
            # Ensure filename is secure
            filename = secure_filename(file.filename)
            logger.info(f"Processing file: {filename}")
            
            # Save the file
            filepath = image_service.save_image_file(file)
            logger.info(f"File saved to: {filepath}")
            
            # Process the image
            logger.info("Starting image processing with YOLO and OCR")
            result = image_service.process_image(filepath)
            
            response_data = {
                'message': 'Image processed successfully',
                'id': result.id
            }
            logger.info(f"Successfully processed image {filename} (ID: {result.id})")
            logger.debug(f"Processing result: {response_data}")
            
            return ok_response(response_data)
        else:
            logger.warning(f"Invalid file type: {file.filename}")
            return error_response('Invalid file type', 400)
            
    except Exception as e:
        logger.error(f"Error in upload_image: {str(e)}", exc_info=True)
        return error_response(str(e), 500)

@main.route('/api/images', methods=['GET'])
def get_images() -> Tuple[Response, int]:
    """Search and retrieve processed images.
    
    Query Parameters:
        q (str): Search query for filtering images
        page (int): Page number for pagination (default: 1)
        per_page (int): Items per page (default: 12)
        locale (str): Language code for tag translations (default: 'en')
    
    Returns:
        JSON response with:
        - List of images with their metadata
        - Pagination information
    """
    try:
        query = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        locale = request.args.get('locale', 'en')
        
        logger.info(f"Searching images with query='{query}', page={page}, per_page={per_page}, locale='{locale}'")
        images, total = image_repository.search_images(query, page, per_page, locale)
        logger.info(f"Found {total} images, returning page {page} ({len(images)} items)")
        
        response = {
            'images': [_format_image(img, locale) for img in images],
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'current_page': page
        }
        logger.debug(f"Search response: {response}")
        return ok_response(response)
        
    except Exception as e:
        logger.error(f"Error in get_images: {str(e)}", exc_info=True)
        return error_response(str(e), 500)

@main.route('/api/images/<int:image_id>', methods=['GET'])
def download_image(image_id: int) -> Tuple[Response, int]:
    """Download a processed image by ID.
    
    Args:
        image_id: ID of the image to download
        
    Returns:
        File download response or error if image not found
    """
    try:
        logger.info(f"Downloading image with ID: {image_id}")
        
        image = image_repository.get_image_by_id(image_id)
        if not image:
            logger.warning(f"Image not found: ID {image_id}")
            return error_response('Image not found', 404)
            
        filepath = os.path.join(image_service.upload_dir, image.filename)
        logger.debug(f"Image file path: {filepath}")
        
        if not os.path.exists(filepath):
            logger.error(f"File not found for image {image_id}: {filepath}")
            return error_response('Image file not found', 404)
            
        logger.info(f"Sending file: {image.filename}")
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error in download_image: {str(e)}", exc_info=True)
        return error_response(str(e), 500)

@main.route('/api/suggestions', methods=['GET'])
def get_suggestions() -> Tuple[Response, int]:
    """Get search suggestions based on query.
    
    Query Parameters:
        q (str): Partial search query
        locale (str): Language code for tag translations (default: 'en')
        
    Returns:
        JSON array of suggestion strings
    """
    try:
        query = request.args.get('q', '')
        locale = request.args.get('locale', 'en')
        
        logger.info(f"Getting suggestions for query='{query}', locale='{locale}'")
        suggestions = image_repository.get_suggestions(query, locale=locale)
        logger.info(f"Found {len(suggestions)} suggestions")
        logger.debug(f"Suggestions: {suggestions}")
        
        return ok_response(suggestions)
        
    except Exception as e:
        logger.error(f"Error in get_suggestions: {str(e)}", exc_info=True)
        return error_response(str(e), 500)

@main.route('/api/images/<int:image_id>/text', methods=['GET'])
def get_image_text(image_id: int) -> Tuple[Response, int]:
    """Get all detected text for an image.
    
    Args:
        image_id: ID of the image to get text for
        
    Returns:
        JSON response with:
        - On success: List of detected texts with their data
        - On failure: error message and appropriate status code
    """
    try:
        logger.info(f"Getting text for image ID: {image_id}")
        
        texts = image_repository.get_image_text(image_id)
        if texts is None:
            logger.warning(f"Image not found: ID {image_id}")
            return error_response('Image not found', 404)
            
        text_data = [text.to_dict() for text in texts]
        logger.info(f"Found {len(text_data)} text regions")
        logger.debug(f"Text data: {text_data}")
        
        return ok_response(text_data)
        
    except Exception as e:
        logger.error(f"Error in get_image_text: {str(e)}", exc_info=True)
        return error_response(str(e), 500)

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
    