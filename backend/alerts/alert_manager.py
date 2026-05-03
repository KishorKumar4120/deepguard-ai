"""
Alert Manager
"""
import logging
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self):
        self.alert_history = deque(maxlen=1000)
        self.active_alerts = {}
        
    async def send_unknown_person_alert(self, camera_id: str, camera_name: str, 
                                        frame, face_data: dict):
        """Send alert for unknown person"""
        alert_data = {
            'alert_id': f"alert_{datetime.now().timestamp()}",
            'type': 'unknown',
            'severity': 'HIGH',
            'camera_id': camera_id,
            'camera_name': camera_name,
            'timestamp': datetime.now().isoformat(),
            'status': 'active'
        }
        
        self.active_alerts[alert_data['alert_id']] = alert_data
        self.alert_history.append(alert_data)
        
        logger.warning(f"🚨 UNKNOWN PERSON ALERT from {camera_name}")
        print(f"\n{'='*50}")
        print(f"🚨 ALERT: Unknown person detected at {camera_name}")
        print(f"📸 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        
        return alert_data
    
    async def get_alert_history(self, limit=100, offset=0, filter=None):
        """Get alert history"""
        alerts = list(self.alert_history)
        return alerts[-limit:]
    
    async def get_active_alerts(self):
        """Get active alerts"""
        return [a for a in self.active_alerts.values() if a['status'] == 'active']
    
    async def get_statistics(self, days=7):
        """Get statistics"""
        return {
            'total_alerts': len(self.alert_history),
            'active_alerts': len(self.active_alerts)
        }

# Singleton
alert_manager_instance = AlertManager()