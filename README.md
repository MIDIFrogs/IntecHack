# Image Processing and Search Web Application

This application allows users to upload images, automatically detect text and objects using YOLOv8 and EasyOCR, and search through the processed images.

## Project Structure

```
.
├── backend/                 # Flask backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py       # Database models
│   │   ├── routes.py       # API routes
│   │   └── utils.py        # Helper functions
│   ├── config.py           # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   └── run.py             # Application entry point
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/    # Vue components
│   │   ├── views/         # Vue views
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Flask server:
```bash
python run.py
```

### Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm run dev
```

## Features

- Image upload with automatic text and object detection
- Image search based on detected text and objects
- Autocomplete suggestions for search
- Image grid view with download functionality
- SQLite database for storing image metadata

## API Endpoints

- POST /api/upload - Upload image and process it
- GET /api/images - Get list of images with optional search parameters
- GET /api/images/<id> - Download specific image
- GET /api/suggestions - Get search suggestions

## Technologies Used

- Backend: Flask, YOLOv8, EasyOCR, SQLite
- Frontend: Vue.js, Vite
