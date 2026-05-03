"""
Alert Management API
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from datetime import datetime

from backend.api.auth import get_current_active_user
from backend.alerts.alert_manager import alert_manager_instance

router = APIRouter()

def send_email_background():
    """Background task to send email"""
    try:
        from backend.alerts.email_alert import EmailAlert
        import cv2
        import numpy as np
        
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(test_frame, "DEEPGUARD AI ALERT", (100, 240), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(test_frame, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), (200, 300), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        email = EmailAlert()
        result = email.send_alert(test_frame, "Test Alert", "DeepGuard System")
        print(f"Email sending result: {result}")
        return result
    except Exception as e:
        print(f"Background email error: {e}")
        return False

@router.post("/test")
async def send_test_alert(background_tasks: BackgroundTasks):
    """Send a test alert with email in background"""
    from backend.alerts.alert_manager import alert_manager_instance
    from backend.alerts.email_alert import EmailAlert
    
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
    
    # Try to send email directly (not background) to see result
    email = EmailAlert()
    email_sent = False
    
    try:
        import cv2
        import numpy as np
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(test_frame, "DEEPGUARD AI TEST", (150, 240), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        email_sent = email.send_alert(test_frame, "Test Alert", "DeepGuard System")
    except Exception as e:
        print(f"Email error: {e}")
    
    return {
        "message": "Test alert created", 
        "alert": test_alert,
        "email_sent": email_sent
    }

@router.get("/history")
async def get_alert_history(limit: int = 100):
    alerts = list(alert_manager_instance.alert_history)[-limit:]
    return {"alerts": alerts, "total": len(alerts)}

@router.get("/statistics")
async def get_alert_statistics():
    stats = await alert_manager_instance.get_statistics()
    return stats

@router.get("/active")
async def get_active_alerts():
    alerts = await alert_manager_instance.get_active_alerts()
    return {"alerts": alerts, "count": len(alerts)}
