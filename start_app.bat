@echo off
REM Start script for Text Correction Application
REM Starts both the FastAPI backend and Streamlit frontend

echo ======================================
echo Starting Text Correction Application
echo ======================================
echo.

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import fastapi, streamlit, uvicorn" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Missing dependencies
    echo Please install: pip install -r requirements.txt -r requirements_api.txt
    pause
    exit /b 1
)

echo Done! Dependencies OK
echo.

REM Start FastAPI backend in separate window
echo Starting FastAPI backend on http://localhost:8000
start "Text Correction API" python -m backend.run

REM Wait for API to start
timeout /t 3 /nobreak >nul

echo Done! API started
echo.
echo Starting Streamlit frontend...
echo Web interface will open in your browser
echo.

REM Start Streamlit frontend
streamlit run frontend/app.py

echo.
echo Application stopped
pause
