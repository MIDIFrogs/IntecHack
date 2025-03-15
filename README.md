ImageHound - Image Processing and Search Application

A modern web application for uploading, organizing, and searching images with automatic tag generation using AI-powered object detection and text recognition.

Project Overview
--------------
ImageHound is a full-stack web application that allows users to:
- Upload and organize images
- Automatically detect objects and text in images
- Search images by tags
- Browse images in a responsive grid layout
- Download images
- View images by albums/categories
- Switch between light and dark themes

Project Structure
---------------

.
├── src/
│   ├── backend/           # Flask backend
│   │   ├── server.py     # Main Flask application
│   │   └── requirements.txt
│   ├── frontend/         # Vue.js frontend
│   │   ├── src/
│   │   │   ├── App.vue  # Main Vue application
│   │   │   └── main.js
│   │   └── package.json
│   └── run.py           # Unified launcher script

Technical Requirements
--------------------
- Python 3.x
- Node.js and npm
- Flask
- Vue.js 3
- SQLite

Dependencies
-----------
Backend (Python):
- flask==3.0.2
- flask-cors==4.0.0
- flask-sqlalchemy==3.1.1
- ultralytics==8.1.27 (YOLOv8)
- easyocr==1.7.1
- Pillow==11.1.0
- python-dotenv==1.0.1
- SQLAlchemy==2.0.27
- Werkzeug==3.0.1
- PyYAML==6.0.1
- piexif==1.1.3
- imutils==0.5.4

Frontend:
- Vue.js 3
- Tailwind CSS
- Axios for API calls
- Inter font family

Features
--------
1. Image Management:
   - Drag-and-drop image upload
   - Multi-file upload support
   - Upload progress tracking
   - Image preview before upload

2. Search and Organization:
   - Tag-based image search
   - Auto-complete suggestions
   - Album view by tags
   - Horizontal scrollable album navigation

3. User Interface:
   - Responsive grid layout
   - Light/Dark theme toggle
   - Infinite scroll for image loading
   - Modern and clean design
   - "Back to Top" button
   - Loading indicators

4. Image Processing:
   - Automatic object detection using YOLOv8
   - Text recognition using EasyOCR
   - Automatic tag generation
   - Image metadata extraction

Setup Instructions
----------------

1. Clone the repository:
   git clone [repository-url]
   cd [project-directory]

2. Backend Setup:
   cd src/backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt

3. Frontend Setup:
   cd src/frontend
   npm install

4. Running the Application:
   - Use the unified launcher:
     python src/run.py
   
   OR run services separately:
   - Backend: python src/backend/server.py
   - Frontend: cd src/frontend && npm run dev

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

API Endpoints
------------
- POST /api/upload - Upload and process images
- GET /api/images - Get images list with optional search/tag filters
- GET /api/images/{id} - Download specific image
- GET /api/albums/tags - Get available tags and their thumbnails

Browser Support
-------------
- Chrome (recommended)
- Firefox
- Safari
- Edge

Note: For optimal performance, use modern browsers with JavaScript enabled.

Contributing
-----------
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request 