#!/usr/bin/env python3
"""
Standalone server launcher for Novel Translation Refiner
This file imports everything correctly and starts the server
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Now import the FastAPI app
from main import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Novel Translation Refiner Backend Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 