"""
Camera Management API
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from pydantic import BaseModel

router = APIRouter()

class CameraConfig(BaseModel):
    id: str
    name: str
    source: str
    location: str

# Simple camera store
cameras_db = {}

@router.get("/list")
async def list_cameras():
    """List all cameras"""
    return {
        "cameras": list(cameras_db.values()),
        "total": len(cameras_db)
    }

@router.post("/add")
async def add_camera(camera: CameraConfig):
    """Add a new camera"""
    cameras_db[camera.id] = camera.dict()
    return {"message": "Camera added", "camera": camera}

@router.delete("/{camera_id}")
async def remove_camera(camera_id: str):
    """Remove a camera"""
    if camera_id in cameras_db:
        del cameras_db[camera_id]
        return {"message": "Camera removed"}
    raise HTTPException(status_code=404, detail="Camera not found")

@router.get("/{camera_id}/status")
async def camera_status(camera_id: str):
    """Get camera status"""
    if camera_id in cameras_db:
        return {"status": "online", "camera": cameras_db[camera_id]}
    raise HTTPException(status_code=404, detail="Camera not found")