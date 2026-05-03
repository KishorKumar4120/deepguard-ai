from backend.alerts.email_alert import EmailAlert

class AlertManager:
    def __init__(self):
        # ... existing code ...
        self.email_alert = EmailAlert()
    
    async def send_unknown_person_alert(self, camera_id, camera_name, frame, face_data):
        # ... existing code ...
        
        # Send email alert
        self.email_alert.send_alert(
            frame=frame,
            person_name="Unknown Person",
            camera_name=camera_name
        )
