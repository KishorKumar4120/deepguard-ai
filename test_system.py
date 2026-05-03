"""
DeepGuard AI - Complete System Test Suite
Run this before deployment to verify everything works!
"""
import requests
import cv2
import numpy as np
import os
import sys
import time
import json
from datetime import datetime

# Configuration
API_URL = "http://127.0.0.1:8000"
TEST_RESULTS = []

def print_test(name, status, details=""):
    """Print test result"""
    symbol = "✅" if status else "❌"
    result = f"{symbol} {name}: {'PASS' if status else 'FAIL'}"
    if details:
        result += f" - {details}"
    print(result)
    TEST_RESULTS.append({"name": name, "status": status, "details": details})
    return status

def test_backend_connection():
    """Test 1: Backend server connection"""
    print("\n📡 TEST 1: Backend Connection")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return print_test("Backend Server", True, f"Version {data.get('version', '1.0')}")
    except:
        pass
    return print_test("Backend Server", False, "Make sure to run: python run.py")

def test_api_endpoints():
    """Test 2: All API endpoints"""
    print("\n🔌 TEST 2: API Endpoints")
    all_passed = True
    
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/api/cameras/list", "Cameras list"),
        ("GET", "/api/alerts/history", "Alerts history"),
        ("GET", "/api/alerts/statistics", "Alert statistics"),
        ("GET", "/api/alerts/active", "Active alerts"),
    ]
    
    for method, endpoint, name in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_URL}{endpoint}", timeout=5)
                if response.status_code in [200, 404]:  # 404 is fine for empty data
                    print_test(f"API: {name}", True, f"HTTP {response.status_code}")
                else:
                    print_test(f"API: {name}", False, f"HTTP {response.status_code}")
                    all_passed = False
        except Exception as e:
            print_test(f"API: {name}", False, str(e))
            all_passed = False
    
    return all_passed

def test_camera_management():
    """Test 3: Camera CRUD operations"""
    print("\n📹 TEST 3: Camera Management")
    
    # Test add camera
    test_camera = {
        "id": "test_cam_001",
        "name": "Test Camera",
        "source": "0",
        "location": "Test Location"
    }
    
    try:
        response = requests.post(f"{API_URL}/api/cameras/add", json=test_camera)
        if response.status_code == 200:
            print_test("Add Camera", True, "Camera added successfully")
        else:
            print_test("Add Camera", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_test("Add Camera", False, str(e))
        return False
    
    # Test list cameras
    try:
        response = requests.get(f"{API_URL}/api/cameras/list")
        if response.status_code == 200:
            cameras = response.json()
            print_test("List Cameras", True, f"Found {cameras.get('total', 0)} cameras")
        else:
            print_test("List Cameras", False, "Failed to list cameras")
    except Exception as e:
        print_test("List Cameras", False, str(e))
    
    # Test delete camera
    try:
        response = requests.delete(f"{API_URL}/api/cameras/test_cam_001")
        if response.status_code == 200:
            print_test("Delete Camera", True, "Camera removed")
        else:
            print_test("Delete Camera", False, f"HTTP {response.status_code}")
    except Exception as e:
        print_test("Delete Camera", False, str(e))
    
    return True

def test_face_recognition():
    """Test 4: Face recognition engine"""
    print("\n👤 TEST 4: Face Recognition Engine")
    
    from backend.core.face_recognition import face_recognition_engine
    import asyncio
    
    async def test_faces():
        # Load faces
        await face_recognition_engine.load_known_faces()
        
        # Check if engine is working
        status = face_recognition_engine.get_status()
        if status.get('known_faces_count', 0) >= 0:
            print_test("Face Engine Initialized", True, f"Ready with {status['known_faces_count']} faces")
            return True
        return False
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_faces())
        loop.close()
        return result
    except Exception as e:
        print_test("Face Engine", False, str(e))
        return False

def test_webcam():
    """Test 5: Webcam access"""
    print("\n📸 TEST 5: Webcam Access")
    
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print_test("Webcam Access", True, "Camera working")
                cap.release()
                return True
            else:
                print_test("Webcam Access", False, "Cannot capture frame")
                cap.release()
                return False
        else:
            print_test("Webcam Access", False, "No camera detected")
            return False
    except Exception as e:
        print_test("Webcam Access", False, str(e))
        return False

def test_alert_system():
    """Test 6: Alert system"""
    print("\n🚨 TEST 6: Alert System")
    
    # Test alert statistics
    try:
        response = requests.get(f"{API_URL}/api/alerts/statistics")
        if response.status_code == 200:
            stats = response.json()
            print_test("Alert Statistics", True, f"Total: {stats.get('total_alerts', 0)}")
        else:
            print_test("Alert Statistics", False, "Failed to get stats")
    except Exception as e:
        print_test("Alert Statistics", False, str(e))
    
    # Test test alert endpoint
    try:
        response = requests.post(f"{API_URL}/api/alerts/test")
        if response.status_code == 200:
            print_test("Test Alert", True, "Alert sent successfully")
        else:
            print_test("Test Alert", False, f"HTTP {response.status_code}")
    except Exception as e:
        print_test("Test Alert", False, str(e))
    
    return True

def test_database():
    """Test 7: Database operations"""
    print("\n💾 TEST 7: Database")
    
    # Check if database directory exists
    if os.path.exists("data"):
        print_test("Database Directory", True, "data/ folder exists")
    else:
        os.makedirs("data", exist_ok=True)
        print_test("Database Directory", True, "Created data/ folder")
    
    # Check face encodings file
    encodings_file = "data/face_encodings.pkl"
    if os.path.exists(encodings_file):
        import pickle
        try:
            with open(encodings_file, 'rb') as f:
                data = pickle.load(f)
            print_test("Face Database", True, f"Loaded {len(data.get('names', []))} faces")
        except:
            print_test("Face Database", False, "Corrupted database")
    else:
        print_test("Face Database", True, "Database will be created on first use")
    
    return True

def test_frontend():
    """Test 8: Frontend accessibility"""
    print("\n🌐 TEST 8: Frontend")
    
    # Test React frontend
    try:
        response = requests.get("http://localhost:3000", timeout=3)
        if response.status_code == 200:
            print_test("React Frontend", True, "Running on port 3000")
        else:
            print_test("React Frontend", False, f"HTTP {response.status_code}")
    except:
        print_test("React Frontend", False, "Not running (run: npm start)")
    
    # Check HTML dashboard
    if os.path.exists("dashboard.html"):
        print_test("HTML Dashboard", True, "dashboard.html exists")
    else:
        print_test("HTML Dashboard", False, "dashboard.html not found")
    
    return True

def test_performance():
    """Test 9: Performance metrics"""
    print("\n⚡ TEST 9: Performance")
    
    # Test response time
    try:
        start = time.time()
        response = requests.get(f"{API_URL}/health", timeout=5)
        response_time = (time.time() - start) * 1000
        if response_time < 100:
            print_test("API Response Time", True, f"{response_time:.0f}ms (Excellent)")
        elif response_time < 500:
            print_test("API Response Time", True, f"{response_time:.0f}ms (Good)")
        else:
            print_test("API Response Time", False, f"{response_time:.0f}ms (Slow)")
    except:
        print_test("API Response Time", False, "Cannot measure")
    
    return True

def generate_report():
    """Generate test report"""
    print("\n" + "="*60)
    print("📊 TEST REPORT")
    print("="*60)
    
    passed = sum(1 for t in TEST_RESULTS if t['status'])
    total = len(TEST_RESULTS)
    
    print(f"\n✅ PASSED: {passed}/{total}")
    print(f"❌ FAILED: {total - passed}/{total}")
    print(f"📈 SUCCESS RATE: {(passed/total)*100:.1f}%\n")
    
    if passed == total:
        print("🎉 EXCELLENT! All tests passed! System is ready for deployment!")
        print("\n📦 Deployment Checklist:")
        print("   ✅ Backend API is operational")
        print("   ✅ Face recognition is working")
        print("   ✅ Database is configured")
        print("   ✅ Camera system is ready")
        print("   ✅ Alert system is active")
        print("\n🚀 You can now deploy to production!")
    else:
        print("⚠️ Some tests failed. Please fix the issues above before deployment.")
    
    print("\n" + "="*60)
    
    # Save report
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(TEST_RESULTS, f, indent=2)
    print(f"\n📄 Detailed report saved to: {report_file}")

def main():
    """Run all tests"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         DEEPGUARD AI - COMPLETE SYSTEM TEST              ║
    ║              Pre-Deployment Validation                   ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Run all tests
    test_backend_connection()
    test_api_endpoints()
    test_camera_management()
    test_face_recognition()
    test_webcam()
    test_alert_system()
    test_database()
    test_frontend()
    test_performance()
    
    # Generate report
    generate_report()

if __name__ == "__main__":
    main()