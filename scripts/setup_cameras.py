"""
Camera Setup Script
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def setup_cameras():
    """Configure cameras interactively"""
    print("\n=== DeepGuard AI Camera Setup ===\n")
    
    cameras = []
    
    while True:
        print("\nAdd a new camera:")
        name = input("Camera name (or 'done' to finish): ")
        
        if name.lower() == 'done':
            break
        
        source = input("Camera source (0 for webcam, or RTSP URL): ")
        location = input("Camera location (e.g., Front Door): ")
        ptz = input("PTZ capable? (y/n): ").lower() == 'y'
        
        cameras.append({
            'id': f"cam_{len(cameras) + 1}",
            'name': name,
            'source': source,
            'location': location,
            'ptz_enabled': ptz,
            'enabled': True
        })
        
        print(f"✅ Camera '{name}' added!")
    
    # Save configuration
    import json
    with open('config/cameras.json', 'w') as f:
        json.dump(cameras, f, indent=2)
    
    print(f"\n✅ Saved {len(cameras)} cameras to config/cameras.json")
    return cameras

if __name__ == "__main__":
    asyncio.run(setup_cameras())