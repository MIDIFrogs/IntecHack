from app import db
from datetime import datetime

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.relationship('Tag', backref='image', lazy=True)
    detected_text = db.relationship('DetectedText', backref='image', lazy=True)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False)

class DetectedText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    bbox = db.Column(db.String(255), nullable=False)  # Stored as JSON string
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False) 