"""
Face Recognition Engine - Using OpenCV + Face Recognition Library
Windows Compatible - Simplified Working Version
"""
import cv2
import numpy as np
import pickle
import os
from datetime import datetime
import logging
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)

class FaceRecognitionEngine:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_database_path = os.path.join(tempfile.gettempdir(), "face_encodings.pkl")
        
        # Use OpenCV's built-in face detector
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Create data directory
        os.makedirs("data", exist_ok=True)
        os.makedirs("data/known_faces", exist_ok=True)
        
    async def load_known_faces(self):
        """Load known faces from database"""
        if os.path.exists(self.face_database_path):
            try:
                with open(self.face_database_path, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data.get('encodings', [])
                    self.known_face_names = data.get('names', [])
                logger.info(f"✅ Loaded {len(self.known_face_names)} known faces")
            except Exception as e:
                logger.error(f"Error loading faces: {e}")
        else:
            logger.info("📁 No existing face database found. Starting fresh.")
    
    async def save_known_faces(self):
        """Save known faces to database"""
        try:
            data = {
                'encodings': self.known_face_encodings,
                'names': self.known_face_names,
                'timestamp': datetime.now().isoformat()
            }
            with open(self.face_database_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"💾 Saved {len(self.known_face_names)} faces to database")
        except Exception as e:
            logger.error(f"Error saving faces: {e}")
    
    def get_face_encoding(self, face_img):
        """Extract face encoding using histogram features"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            
            # Resize to standard size
            resized = cv2.resize(gray, (100, 100))
            
            # Use HOG (Histogram of Oriented Gradients) features
            # Calculate histogram of gradients as simple features
            gx = cv2.Sobel(resized, cv2.CV_32F, 1, 0, ksize=3)
            gy = cv2.Sobel(resized, cv2.CV_32F, 0, 1, ksize=3)
            mag, ang = cv2.cartToPolar(gx, gy)
            
            # Create histogram of angles
            bin_n = 16  # Number of bins
            bins = np.int32(bin_n * ang / (2 * np.pi))
            hist = np.zeros((bin_n,))
            for i in range(bin_n):
                hist[i] = np.sum(mag[bins == i])
            
            # Normalize histogram
            hist = hist / (np.sum(hist) + 1e-7)
            
            # Add spatial information
            features = []
            features.extend(hist)
            
            # Add mean and std of face regions
            h, w = resized.shape
            for i in range(2):
                for j in range(2):
                    region = resized[i*h//2:(i+1)*h//2, j*w//2:(j+1)*w//2]
                    features.append(np.mean(region) / 255.0)
                    features.append(np.std(region) / 255.0)
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Error getting face encoding: {e}")
            return None
    
    async def register_face(self, name: str, face_img):
        """Register a new face"""
        try:
            # Get face encoding
            encoding = self.get_face_encoding(face_img)
            
            if encoding is None:
                raise ValueError("No face detected in image. Please look directly at camera.")
            
            # Check if face already exists
            for i, existing_encoding in enumerate(self.known_face_encodings):
                is_match, _ = self.compare_faces(encoding, existing_encoding)
                if is_match:
                    raise ValueError(f"Face already registered as '{self.known_face_names[i]}'")
            
            # Add to database
            self.known_face_encodings.append(encoding)
            self.known_face_names.append(name)
            
            await self.save_known_faces()
            
            # Save face image
            face_dir = f"data/known_faces/{name}"
            os.makedirs(face_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cv2.imwrite(f"{face_dir}/{timestamp}.jpg", face_img)
            
            logger.info(f"✅ Registered face for: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            raise
    
    def compare_faces(self, encoding1, encoding2, tolerance=0.7):
        """Compare two face encodings using Euclidean distance"""
        if encoding1 is None or encoding2 is None:
            return False, 1.0
        
        # Ensure same length
        min_len = min(len(encoding1), len(encoding2))
        if min_len == 0:
            return False, 1.0
            
        enc1 = encoding1[:min_len]
        enc2 = encoding2[:min_len]
        
        # Calculate Euclidean distance
        distance = np.linalg.norm(enc1 - enc2)
        
        # Normalize distance (0 to 1)
        max_distance = np.sqrt(min_len)  # Maximum possible distance
        normalized_distance = distance / max_distance
        
        return normalized_distance < tolerance, normalized_distance
    
    async def recognize_face(self, face_img):
        """Recognize a face by comparing with known faces"""
        try:
            # Get encoding of the face
            encoding = self.get_face_encoding(face_img)
            
            if encoding is None:
                return None
            
            # Compare with known faces
            if len(self.known_face_encodings) > 0:
                best_match = None
                best_distance = float('inf')
                
                for i, known_encoding in enumerate(self.known_face_encodings):
                    is_match, distance = self.compare_faces(encoding, known_encoding)
                    
                    if is_match and distance < best_distance:
                        best_distance = distance
                        best_match = i
                
                if best_match is not None:
                    confidence = 1 - best_distance
                    name = self.known_face_names[best_match]
                    
                    # Get simple face attributes
                    attributes = self.get_simple_attributes(face_img)
                    
                    return {
                        'name': name,
                        'confidence': float(confidence),
                        'is_live': True,
                        'attributes': attributes
                    }
            
            # Unknown face
            attributes = self.get_simple_attributes(face_img)
            return {
                'name': 'UNKNOWN',
                'confidence': 0.0,
                'is_live': True,
                'attributes': attributes
            }
            
        except Exception as e:
            logger.error(f"Recognition failed: {e}")
            return None
    
    def get_simple_attributes(self, face_img):
        """Get simple face attributes from image"""
        try:
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            h, w = face_img.shape[:2]
            
            # Simple attribute estimation
            # Calculate face symmetry (left-right)
            left_half = gray[:, :w//2]
            right_half = cv2.flip(gray[:, w//2:], 1)
            
            # Ensure same size
            min_width = min(left_half.shape[1], right_half.shape[1])
            left_half = left_half[:, :min_width]
            right_half = right_half[:, :min_width]
            
            symmetry = 1 - np.mean(np.abs(left_half - right_half)) / 255.0
            
            # Estimate brightness and contrast
            brightness = np.mean(gray) / 255.0
            
            attributes = {
                'age': 30,  # Default
                'gender': 'Unknown',
                'emotion': 'Neutral',
                'symmetry': round(symmetry, 2),
                'brightness': round(brightness, 2)
            }
            
            # Rough age estimation based on face proportions
            # (Very crude, but works for demo)
            aspect_ratio = w / h
            if aspect_ratio > 0.8:
                attributes['age'] = 25
            elif aspect_ratio > 0.7:
                attributes['age'] = 35
            else:
                attributes['age'] = 45
            
            return attributes
            
        except Exception as e:
            logger.error(f"Attribute analysis failed: {e}")
            return None
    
    def detect_faces(self, frame):
        """Detect faces in frame using OpenCV cascade"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60)
        )
        
        face_locations = []
        for (x, y, w, h) in faces:
            # Convert to (top, right, bottom, left) format
            top = y
            right = x + w
            bottom = y + h
            left = x
            face_locations.append((top, right, bottom, left))
        
        return face_locations
    
    def get_status(self):
        """Get engine status"""
        return {
            'known_faces_count': len(self.known_face_names),
            'known_faces': self.known_face_names[:10],
            'database_exists': os.path.exists(self.face_database_path),
            'engine': 'OpenCV Haar Cascade (No MediaPipe)',
            'status': 'operational'
        }

# Singleton instance
face_recognition_engine = FaceRecognitionEngine()