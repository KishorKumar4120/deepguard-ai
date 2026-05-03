@router.post("/test")
async def send_test_alert():
    """Send a test alert"""
    from backend.alerts.alert_manager import alert_manager_instance
    from backend.alerts.email_alert import EmailAlert
    
    # Create test alert
    test_alert = {
        'alert_id': f"test_{datetime.now().timestamp()}",
        'type': 'TEST_ALERT',
        'severity': 'LOW',
        'camera_name': 'Test Camera',
        'timestamp': datetime.now().isoformat(),
        'status': 'active',
        'details': {'message': 'This is a test alert from DeepGuard AI'}
    }
    
    # Add to alert history
    alert_manager_instance.alert_history.append(test_alert)
    alert_manager_instance.active_alerts[test_alert['alert_id']] = test_alert
    
    # Try to send email
    email = EmailAlert()
    # Create a blank image for test
    import numpy as np
    import cv2
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(test_frame, "TEST ALERT", (200, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
    
    email_sent = email.send_alert(test_frame, "Test Person", "Test Camera")
    
    return {
        "message": "Test alert sent", 
        "alert": test_alert,
        "email_sent": email_sent
    }
