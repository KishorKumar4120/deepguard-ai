"""
Alert Management API
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from datetime import datetime
import os

from backend.api.auth import get_current_active_user
from backend.alerts.alert_manager import alert_manager_instance

router = APIRouter()

@router.post("/test")
async def send_test_alert():
    """Send a test alert and return email status"""
    from backend.alerts.alert_manager import alert_manager_instance
    from backend.alerts.email_alert import EmailAlert
    import cv2
    import numpy as np
    
    # Create test alert record
    test_alert = {
        'alert_id': f"test_{datetime.now().timestamp()}",
        'type': 'TEST_ALERT',
        'severity': 'LOW',
        'camera_name': 'Test Camera',
        'timestamp': datetime.now().isoformat(),
        'status': 'active',
        'details': {'message': 'This is a test alert from DeepGuard AI'}
    }
    
    alert_manager_instance.alert_history.append(test_alert)
    alert_manager_instance.active_alerts[test_alert['alert_id']] = test_alert
    
    # Create a test image for email
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(test_frame, "DEEPGUARD AI TEST ALERT", (100, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(test_frame, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), (200, 300), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Try to send email
    email_sent = False
    email_error = None
    
    try:
        email = EmailAlert()
        email_sent = email.send_alert(test_frame, "Test Alert", "DeepGuard System")
        print(f"Email sending result: {email_sent}")
    except Exception as e:
        email_error = str(e)
        print(f"Email error: {email_error}")
    
    return {
        "message": "Test alert created",
        "alert": test_alert,
        "email_sent": email_sent,
        "email_error": email_error
    }

@router.get("/history")
async def get_alert_history(limit: int = 100):
    from backend.alerts.alert_manager import alert_manager_instance
    alerts = list(alert_manager_instance.alert_history)[-limit:]
    return {"alerts": alerts, "total": len(alerts)}

@router.get("/statistics")
async def get_alert_statistics():
    from backend.alerts.alert_manager import alert_manager_instance
    stats = await alert_manager_instance.get_statistics()
    return stats

@router.get("/active")
async def get_active_alerts():
    from backend.alerts.alert_manager import alert_manager_instance
    alerts = await alert_manager_instance.get_active_alerts()
    return {"alerts": alerts, "count": len(alerts)}
