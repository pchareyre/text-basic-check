#!/bin/bash
# Start script for Text Correction Application
# Starts both the FastAPI backend and Streamlit frontend

echo "======================================"
echo "Starting Text Correction Application"
echo "======================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null
then
    echo "ERROR: Python not found"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD=$(command -v python3 || command -v python)

# Check if required packages are installed
echo "Checking dependencies..."
$PYTHON_CMD -c "import fastapi, streamlit, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Missing dependencies"
    echo "Please install: pip install -r requirements.txt -r requirements_api.txt"
    exit 1
fi

echo "✓ Dependencies OK"
echo ""

# Start FastAPI backend in background
echo "Starting FastAPI backend on http://localhost:8000"
$PYTHON_CMD -m backend.run &
API_PID=$!
echo "API PID: $API_PID"

# Wait for API to start
sleep 3

# Check if API is running
if ps -p $API_PID > /dev/null 2>&1; then
    echo "✓ API started successfully"
else
    echo "ERROR: API failed to start"
    exit 1
fi

echo ""
echo "Starting Streamlit frontend..."
echo "Web interface will open in your browser"
echo ""

# Start Streamlit frontend
streamlit run frontend/app.py

# Cleanup: Kill API when Streamlit exits
echo ""
echo "Shutting down..."
kill $API_PID 2>/dev/null
echo "✓ Application stopped"
