#!/usr/bin/env python3
"""
Startup script for Railway deployment
Handles PORT environment variable properly
"""

import os
import uvicorn
from main import app

if __name__ == "__main__":
    # Get port from environment variable, default to 8000
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting server on port {port}")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
