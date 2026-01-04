"""
Launcher script for Windows executable.

This script starts both the backend API and frontend Streamlit interface.
It's designed to be packaged into a Windows executable using PyInstaller.
"""

import sys
import os
import subprocess
import time
import webbrowser
from pathlib import Path
import multiprocessing

# Add current directory to Python path
if getattr(sys, 'frozen', False):
    # Running as executable
    application_path = Path(sys._MEIPASS)
    exe_dir = Path(sys.executable).parent
else:
    # Running as script
    application_path = Path(__file__).parent
    exe_dir = application_path

# Add to path
sys.path.insert(0, str(application_path))

# Set model directory to exe directory
os.environ['APP_T5_MODEL_DIR'] = str(exe_dir / 't5-small-onnx-q')


def start_backend():
    """Start the FastAPI backend server."""
    try:
        from backend.app.main import app
        import uvicorn
        
        print("Starting FastAPI backend on http://localhost:8000")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting backend: {e}")
        input("Press Enter to exit...")
        sys.exit(1)


def start_frontend():
    """Start the Streamlit frontend."""
    try:
        import streamlit.web.cli as stcli
        
        # Wait for backend to start
        time.sleep(3)
        
        print("Starting Streamlit frontend on http://localhost:8501")
        
        # Find frontend app
        if getattr(sys, 'frozen', False):
            frontend_app = str(application_path / 'frontend' / 'app.py')
        else:
            frontend_app = str(application_path / 'frontend' / 'app.py')
        
        # Start Streamlit
        sys.argv = [
            "streamlit",
            "run",
            frontend_app,
            "--server.port=8501",
            "--server.address=127.0.0.1",
            "--browser.gatherUsageStats=false",
        ]
        
        # Open browser after a delay
        def open_browser():
            time.sleep(5)
            webbrowser.open('http://localhost:8501')
        
        import threading
        threading.Thread(target=open_browser, daemon=True).start()
        
        stcli.main()
        
    except Exception as e:
        print(f"Error starting frontend: {e}")
        input("Press Enter to exit...")
        sys.exit(1)


def main():
    """Main entry point."""
    print("=" * 60)
    print("Text Correction Application")
    print("=" * 60)
    print()
    
    # Check if model exists
    model_dir = Path(os.environ['APP_T5_MODEL_DIR'])
    if not model_dir.exists():
        print(f"WARNING: T5 model not found at {model_dir}")
        print("T5 grammar correction will not be available.")
        print("Only SymSpell spell checking will work.")
        print()
        print("To enable T5 correction:")
        print("1. Export and quantize the model (see README_T5_ONNX.md)")
        print("2. Place 't5-small-onnx-q/' directory next to the .exe")
        print()
        response = input("Continue without T5? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
        print()
    
    print("Starting application components...")
    print()
    
    # Start backend in separate process
    backend_process = multiprocessing.Process(target=start_backend, daemon=True)
    backend_process.start()
    
    # Start frontend in main process (so it controls termination)
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        backend_process.terminate()
        backend_process.join(timeout=5)
        if backend_process.is_alive():
            backend_process.kill()
    
    print("Application stopped.")


if __name__ == "__main__":
    # Windows multiprocessing fix
    multiprocessing.freeze_support()
    main()
