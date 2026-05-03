"""
DeepGuard AI - Main Application Entry Point
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Now import using full paths
from backend.api import auth, cameras, alerts
from backend.core.face_recognition import face_recognition_engine
from backend.alerts.alert_manager import alert_manager_instance

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting DeepGuard AI Enterprise Suite...")
    
    # Load AI models
    await face_recognition_engine.load_known_faces()
    
    logger.info("✅ DeepGuard AI is ready!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down DeepGuard AI...")

# Create FastAPI app
app = FastAPI(
    title="DeepGuard AI Security Suite",
    version="1.0.0",
    description="Enterprise-grade AI Security System",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(cameras.router, prefix="/api/cameras", tags=["Cameras"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])

@app.get("/")
async def root():
    """Health check"""
    return {
        "name": "DeepGuard AI Security Suite",
        "version": "1.0.0",
        "status": "operational",
        "features": {
            "face_recognition": True,
            "anti_spoofing": True,
            "real_time_alerts": True
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "face_engine": face_recognition_engine.get_status()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
    
@app.get("/favicon.ico")
async def favicon():
    return {"message": "No favicon"}