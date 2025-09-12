#!/usr/bin/env python3
"""
Startup script for IT Planning Workflow System
This script helps you run both the FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import streamlit
        import fastapi
        import uvicorn
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def run_api():
    """Run the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    try:
        # Run the API in the background
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
        print("✅ FastAPI backend started on http://localhost:8000")
        return process
    except Exception as e:
        print(f"❌ Failed to start FastAPI: {e}")
        return None

def run_streamlit():
    """Run the Streamlit frontend"""
    print("🚀 Starting Streamlit frontend...")
    try:
        # Run Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")

def main():
    """Main function to orchestrate the startup"""
    print("=" * 60)
    print("🚀 IT Planning Workflow System Startup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py") or not os.path.exists("streamlit_app.py"):
        print("❌ Please run this script from the project root directory")
        print("   (where main.py and streamlit_app.py are located)")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("\n📋 Available options:")
    print("1. Run Streamlit UI only (assumes API is already running)")
    print("2. Run both API and Streamlit UI")
    print("3. Run API only")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🌐 Starting Streamlit UI only...")
        print("   Make sure the API is running on http://localhost:8000")
        run_streamlit()
    
    elif choice == "2":
        print("\n🌐 Starting both API and Streamlit UI...")
        api_process = run_api()
        
        if api_process:
            print("\n⏳ Waiting for API to start...")
            time.sleep(3)  # Give API time to start
            
            print("\n🌐 Starting Streamlit UI...")
            print("   API: http://localhost:8000")
            print("   UI:  http://localhost:8501")
            print("\n   Press Ctrl+C to stop both services")
            
            try:
                run_streamlit()
            except KeyboardInterrupt:
                print("\n🛑 Stopping services...")
                api_process.terminate()
                print("✅ Services stopped")
    
    elif choice == "3":
        print("\n🌐 Starting API only...")
        run_api()
        print("\n   API running on http://localhost:8000")
        print("   Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n✅ API stopped")
    
    else:
        print("❌ Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()
