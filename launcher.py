import subprocess
import time
import signal
import sys
import os

def signal_handler(signum, frame):
    print("\nShutting down services...")
    # Kill all child processes
    try:
        backend_process.terminate()
        frontend_process.terminate()
    except:
        pass
    sys.exit(0)

# Register signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

try:
    print("Starting FastAPI backend...")
    # Start backend process
    backend_process = subprocess.Popen([
        "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"
    ])
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    print("Starting Streamlit frontend...")
    # Start frontend process
    frontend_process = subprocess.Popen([
        "streamlit", "run", "streamlit_app.py"
    ])
    
    # Wait for processes to complete
    frontend_process.wait()
    
except KeyboardInterrupt:
    print("\nShutting down services...")
finally:
    # Clean up processes
    try:
        backend_process.terminate()
        frontend_process.terminate()
    except:
        pass