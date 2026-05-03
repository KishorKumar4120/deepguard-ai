"""
Test face recognition
"""
import asyncio
import cv2
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.core.face_recognition import face_recognition_engine

async def test():
    print("Testing Face Recognition...")
    await face_recognition_engine.load_known_faces()
    
    # Open camera
    cap = cv2.VideoCapture(0)
    
    print("\n📸 Press 'r' to register a face")
    print("📸 Press 'q' to quit")
    print("-" * 40)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect faces
        face_locations = face_recognition_engine.detect_faces(frame)
        
        for (top, right, bottom, left) in face_locations:
            # Extract face ROI
            face_roi = frame[top:bottom, left:right]
            
            if face_roi.size > 0:
                # Recognize face
                result = await face_recognition_engine.recognize_face(face_roi)
                
                if result:
                    name = result['name']
                    confidence = result['confidence']
                    
                    # Draw rectangle and label
                    color = (0, 0, 255) if name == 'UNKNOWN' else (0, 255, 0)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    
                    label = f"{name} ({confidence:.2f})" if confidence > 0 else name
                    cv2.putText(frame, label, (left, top-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        cv2.imshow('Face Recognition Test', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            # Register a face
            name = input("\nEnter name: ")
            if name and face_locations:
                face_roi = frame[face_locations[0][0]:face_locations[0][2], 
                                face_locations[0][3]:face_locations[0][1]]
                await face_recognition_engine.register_face(name, face_roi)
                print(f"✅ Registered {name}!")
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    asyncio.run(test())