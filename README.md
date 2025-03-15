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

Technical Requirements
--------------------
- Python 3.x
- Node.js and npm
- Flask
- Vue.js 3
- SQLite

- Application uses Flask for backend app and Vue.JS for frontend.
- Images search is based on SQLite DB run with SQLAlchemy.
- Detection and text reading are performed with YOLOv8 and EasyOCR

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
   ```
   git clone https://https://github.com/MIDIFrogs/IntecHack.git
   cd IntecHack
   ```

2. Running the Application:
   - Use the unified launcher:
     `python src/run.py`
   
   OR run services separately:
   - Backend: `python src/backend/server.py`
   - Frontend: `cd src/frontend && npm run dev`

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

API Endpoints
------------
- POST /api/upload - Upload and process images
- GET /api/images - Get images list with optional search/tag filters
- GET /api/images/{id} - Get info about specific image
- GET /api/images/{id}/download - Download an image
- GET /api/albums/tags - Get available tags and their thumbnails

Contributing
-----------
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request 
