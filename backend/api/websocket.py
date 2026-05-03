"""
WebSocket for real-time streaming
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import base64
import cv2
import asyncio

from backend.api.auth import get_current_user

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, camera_id: str, user_id: str):
        await websocket.accept()
        if camera_id not in self.active_connections:
            self.active_connections[camera_id] = set()
        self.active_connections[camera_id].add(websocket)
        self.user_connections[user_id] = websocket
    
    def disconnect(self, websocket: WebSocket, camera_id: str, user_id: str):
        if camera_id in self.active_connections:
            self.active_connections[camera_id].discard(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]
    
    async def broadcast_frame(self, camera_id: str, frame_data: dict):
        if camera_id in self.active_connections:
            message = json.dumps(frame_data)
            for connection in self.active_connections[camera_id]:
                try:
                    await connection.send_text(message)
                except:
                    pass
    
    async def send_personal_alert(self, user_id: str, alert_data: dict):
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_json(alert_data)
            except:
                pass

manager = ConnectionManager()

@router.websocket("/stream/{camera_id}")
async def websocket_stream(websocket: WebSocket, camera_id: str):
    # Get user from token (implement proper auth)
    user_id = "temp_user"  # Extract from query params
    
    await manager.connect(websocket, camera_id, user_id)
    
    try:
        while True:
            # Receive commands from client
            data = await websocket.receive_text()
            command = json.loads(data)
            
            if command.get("type") == "ptz_command":
                # Handle PTZ command
                from backend.core.camera_manager import camera_manager_instance
                await camera_manager_instance.ptz_move(
                    camera_id,
                    command.get("direction"),
                    command.get("speed", 0.5)
                )
            elif command.get("type") == "request_frame":
                # Request current frame
                await manager.broadcast_frame(camera_id, {
                    "type": "frame_requested",
                    "camera": camera_id
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, camera_id, user_id)