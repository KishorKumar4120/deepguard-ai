#!/usr/bin/env python
"""
DeepGuard AI - Launcher Script
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         DEEPGUARD AI - ENTERPRISE SECURITY SUITE         ║
    ║                    Starting Server...                     ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )