#!/usr/bin/env python3
"""
Local development server for Helpdesk-AI backend.

This script starts the FastAPI server without Docker.
"""

import os
import subprocess
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists, create from template if not."""
    env_file = Path(".env")
    env_example = Path("env.local.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("📋 Creating .env file from template...")
            env_file.write_text(env_example.read_text())
            print("✅ .env file created. Please review and update if needed.")
        else:
            print("⚠️  No .env file found. Creating basic SQLite configuration...")
            env_file.write_text("DATABASE_URL=sqlite:///./helpdesk.db\nDEBUG=True\n")
            print("✅ Basic .env file created with SQLite.")
    else:
        print("✅ .env file already exists.")

def install_dependencies():
    """Install Python dependencies if needed."""
    try:
        import fastapi
        import sqlalchemy
        import uvicorn
        print("✅ Dependencies already installed.")
    except ImportError:
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed.")

def main():
    """Start the development server."""
    print("🚀 Starting Helpdesk-AI local development server...")
    
    # Check environment
    check_env_file()
    install_dependencies()
    
    # Start server
    print("\n🌐 Starting FastAPI server on http://localhost:8000")
    print("📊 Admin interface: http://localhost:8000/admin/tickets")
    print("🔄 API docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server.\n")
    
    # Run uvicorn
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")

if __name__ == "__main__":
    main()
