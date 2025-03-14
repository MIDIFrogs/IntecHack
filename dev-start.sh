#!/bin/bash

echo "Starting development servers..."

# Start backend server
(cd src/backend && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt && \
python run.py) &

# Start frontend server
(cd src/frontend && \
npm install && \
npm run dev) &

echo "Development servers are starting..."
echo "Backend will be available at http://127.0.0.1:5000"
echo "Frontend will be available at http://127.0.0.1:5173"

# Wait for both processes
wait 