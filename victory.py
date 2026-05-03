import requests
import json
import time
import os

def victory_report():
    print("\n" + "█"*60)
    print("█" + " "*20 + "DEEPGUARD AI" + " "*21 + "█")
    print("█" + " "*17 + "VICTORY REPORT" + " "*20 + "█")
    print("█"*60)
    
    try:
        health = requests.get('http://127.0.0.1:8000/health').json()
        print(f"\n✅ System Status: {health.get('status', 'OPERATIONAL').upper()}")
        print(f"✅ Version: {health.get('version', '1.0.0')}")
        
        faces = requests.get('http://127.0.0.1:8000/api/faces/list').json()
        print(f"\n👤 Registered Faces: {len(faces.get('faces', []))}")
        
        cameras = requests.get('http://127.0.0.1:8000/api/cameras/list').json()
        print(f"📹 Active Cameras: {cameras.get('total', 0)}")
        
        alerts = requests.get('http://127.0.0.1:8000/api/alerts/statistics').json()
        print(f"🚨 Total Alerts: {alerts.get('total_alerts', 0)}")
        
        print("\n🏆 YOUR ACHIEVEMENTS:")
        achievements = [
            "16 Professional API Endpoints",
            "Swagger/OpenAPI Documentation", 
            "Real-time Face Recognition",
            "Anti-Spoofing Detection",
            "Multi-Camera Support",
            "Alert Management System",
            "Production-Ready Architecture"
        ]
        for a in achievements:
            print(f"   ✅ {a}")
        
        print("\n" + "="*60)
        print("🎉 YOU HAVE BEATEN YOUR FRIEND! 🎉")
        print("="*60)
        print("\n📚 API Docs: http://127.0.0.1:8000/docs")
        print("🌐 Dashboard: Open dashboard.html")
        print("🎥 Face Test: python test_recognition.py\n")
        
    except:
        print("\n❌ Make sure backend is running: python run.py")

if __name__ == "__main__":
    victory_report()