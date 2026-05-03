"""
Object Detection with YOLOv8 for Weapons and Suspicious Items
"""
import cv2
import numpy as np
from ultralytics import YOLO
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from typing import List, Dict, Tuple
import os

logger = logging.getLogger(__name__)

class ObjectDetector:
    """Detect weapons, tools, and suspicious objects"""
    
    def __init__(self):
        self.model = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.suspicious_classes = [
            'knife', 'gun', 'pistol', 'rifle', 'shotgun',
            'weapon', 'scissors', 'hammer', 'crowbar'
        ]
        
    async def load_model(self):
        """Load YOLO model"""
        try:
            # Download model if not exists
            model_path = "ai_models/yolov8n.pt"
            if not os.path.exists(model_path):
                os.makedirs("ai_models", exist_ok=True)
                logger.info("Downloading YOLO model...")
            
            self.model = YOLO(model_path)
            logger.info("YOLO model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            return False
    
    async def detect_objects(self, frame: np.ndarray) -> List[Dict]:
        """Detect objects in frame"""
        if self.model is None:
            return []
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            self.executor,
            self.model,
            frame
        )
        
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    confidence = float(box.conf[0])
                    
                    if confidence > 0.5:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        detections.append({
                            'class': class_name,
                            'confidence': confidence,
                            'bbox': [x1, y1, x2, y2],
                            'is_suspicious': class_name.lower() in self.suspicious_classes
                        })
        
        return detections
    
    def annotate_frame(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """Draw detection boxes on frame"""
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            color = (0, 0, 255) if det['is_suspicious'] else (0, 255, 0)
            
            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{det['class']}: {det['confidence']:.2f}"
            if det['is_suspicious']:
                label = f"⚠️ {label}"
            
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 10),
                         (x1 + label_size[0], y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return frame

# Singleton
object_detector = ObjectDetector()