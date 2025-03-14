from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from app import db
from app.models import Image, Tag, DetectedText
from app.utils import process_image, allowed_file
import os
from config import Config

main = Blueprint('main', __name__)

@main.route('/api/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Process image with YOLOv8 and EasyOCR
        tags, detected_text = process_image(filepath)
        
        # Save to database
        image = Image(filename=filename)
        db.session.add(image)
        db.session.flush()  # Get image ID
        
        for tag_name, confidence in tags:
            tag = Tag(name=tag_name, confidence=confidence, image_id=image.id)
            db.session.add(tag)
        
        for text, conf, bbox in detected_text:
            detected = DetectedText(
                text=text,
                confidence=conf,
                bbox=str(bbox),
                image_id=image.id
            )
            db.session.add(detected)
        
        db.session.commit()
        return jsonify({'message': 'Image processed successfully', 'id': image.id})
    
    return jsonify({'error': 'Invalid file type'}), 400

@main.route('/api/images', methods=['GET'])
def get_images():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    # Build query based on search parameters
    images_query = Image.query
    
    if query:
        # Search in tags and detected text
        images_query = images_query.join(Tag).join(DetectedText).filter(
            (Tag.name.ilike(f'%{query}%')) |
            (DetectedText.text.ilike(f'%{query}%'))
        )
    
    # Get paginated results
    pagination = images_query.paginate(page=page, per_page=per_page)
    images = pagination.items
    
    return jsonify({
        'images': [{
            'id': img.id,
            'filename': img.filename,
            'tags': [{'name': tag.name, 'confidence': tag.confidence} for tag in img.tags],
            'detected_text': [{'text': dt.text, 'confidence': dt.confidence} for dt in img.detected_text]
        } for img in images],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@main.route('/api/images/<int:image_id>', methods=['GET'])
def download_image(image_id):
    image = Image.query.get_or_404(image_id)
    return send_file(
        os.path.join(Config.UPLOAD_FOLDER, image.filename),
        as_attachment=True
    )

@main.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    # Get suggestions from tags and detected text
    tag_suggestions = Tag.query.filter(
        Tag.name.ilike(f'%{query}%')
    ).distinct(Tag.name).limit(5).all()
    
    text_suggestions = DetectedText.query.filter(
        DetectedText.text.ilike(f'%{query}%')
    ).distinct(DetectedText.text).limit(5).all()
    
    suggestions = (
        [tag.name for tag in tag_suggestions] +
        [dt.text for dt in text_suggestions]
    )
    
    return jsonify(list(set(suggestions)))  # Remove duplicates 