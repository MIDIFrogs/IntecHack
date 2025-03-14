@echo off
echo Starting development servers...

:: Start backend server
start cmd /k "cd src\backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python run.py"

:: Start frontend server
start cmd /k "cd src\frontend && npm install && npm run dev"

echo Development servers are starting...
echo Backend will be available at http://127.0.0.1:5000
echo Frontend will be available at http://127.0.0.1:5173 