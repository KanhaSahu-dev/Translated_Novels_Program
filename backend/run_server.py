#!/usr/bin/env python3
"""
Simple launcher script for the Novel Translation Refiner backend server
Run this from the backend directory: python run_server.py
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main app
from app.main import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Novel Translation Refiner Backend Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 