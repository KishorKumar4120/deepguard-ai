"""
SQLAlchemy Database Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Detection(Base):
    __tablename__ = 'detections'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    camera_id = Column(String(50))
    camera_name = Column(String(100))
    person_name = Column(String(100))
    confidence = Column(Float)
    is_known = Column(Boolean, default=False)
    is_spoof = Column(Boolean, default=False)
    face_encoding = Column(Text)  # Store as JSON string
    attributes = Column(JSON)
    image_path = Column(String(500))
    
class Alert(Base):
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    alert_id = Column(String(100), unique=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    alert_type = Column(String(50))
    severity = Column(String(20))
    camera_id = Column(String(50))
    camera_name = Column(String(100))
    status = Column(String(20), default='active')
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime)
    resolved_by = Column(String(100))
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    details = Column(JSON)
    
class Camera(Base):
    __tablename__ = 'cameras'
    
    id = Column(Integer, primary_key=True)
    camera_id = Column(String(50), unique=True)
    name = Column(String(100))
    source = Column(String(500))
    location = Column(String(200))
    ptz_enabled = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime)
    
class KnownFace(Base):
    __tablename__ = 'known_faces'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    face_hash = Column(String(64), unique=True)
    face_encoding = Column(Text)
    registered_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)
    image_count = Column(Integer, default=0)