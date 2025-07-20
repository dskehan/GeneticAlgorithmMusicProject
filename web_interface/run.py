#!/usr/bin/env python3
"""
Simple startup script for the Genetic Algorithm Music Evolution Web Interface
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Start the FastAPI web server."""
    
    # Add the parent directory to Python path for imports
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))
    
    # Set default configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")
    
    print("🎵 Starting Genetic Algorithm Music Evolution Web Interface")
    print(f"🌐 Server will be available at: http://{host}:{port}")
    print(f"📖 API Documentation: http://{host}:{port}/api/docs")
    print(f"🔄 Auto-reload: {reload}")
    print()
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True
    )

if __name__ == "__main__":
    main()