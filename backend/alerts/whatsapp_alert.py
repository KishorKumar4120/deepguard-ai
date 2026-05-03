"""
WhatsApp Business API Integration
"""
from twilio.rest import Client
import base64
import cv2
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class WhatsAppAlert:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        self.to_number = os.getenv("SECURITY_TEAM_NUMBER")
        self.client = None
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            self.enabled = True
            logger.info("WhatsApp alerts enabled")
        else:
            self.enabled = False
            logger.warning("WhatsApp alerts disabled - missing credentials")
    
    async def send_alert(self, alert_data: dict, frame: np.ndarray):
        """Send WhatsApp alert with image"""
        if not self.enabled or not self.client:
            return False
        
        try:
            # Save frame temporarily
            temp_path = f"temp_alert_{datetime.now().timestamp()}.jpg"
            cv2.imwrite(temp_path, frame)
            
            # Create message
            message_body = self._format_message(alert_data)
            
            # Send WhatsApp message with media
            message = self.client.messages.create(
                from_=self.from_number,
                to=self.to_number,
                body=message_body,
                media_url=[self._upload_media(temp_path)]
            )
            
            # Cleanup
            os.remove(temp_path)
            
            logger.info(f"WhatsApp alert sent: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"WhatsApp alert failed: {e}")
            return False
    
    def _format_message(self, alert_data: dict) -> str:
        """Format alert message"""
        alert_type = alert_data.get('type', 'UNKNOWN')
        severity = alert_data.get('severity', 'MEDIUM')
        camera = alert_data.get('camera_name', 'Unknown')
        
        emoji = "🚨" if severity == "HIGH" else "⚠️" if severity == "MEDIUM" else "ℹ️"
        
        message = f"""
{emoji} *DEEPGUARD AI ALERT* {emoji}

*Type:* {alert_type}
*Severity:* {severity}
*Camera:* {camera}
*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

*Details:*
{self._get_alert_details(alert_data)}

*Actions:*
1️⃣ Check attached image
2️⃣ Review live feed
3️⃣ Dispatch security if needed

_This is an automated security alert._
        """
        return message
    
    def _get_alert_details(self, alert_data: dict) -> str:
        """Get alert specific details"""
        if alert_data.get('type') == 'UNKNOWN_PERSON':
            face_data = alert_data.get('face_data', {})
            attrs = face_data.get('attributes', {})
            return f"""
• Unknown person detected
• Confidence: {face_data.get('confidence', 0):.2%}
• Age estimate: {attrs.get('age', 'Unknown')}
• Emotion: {attrs.get('dominant_emotion', 'Unknown')}
            """
        elif alert_data.get('type') == 'WEAPON_DETECTED':
            return f"""
• Weapon detected: {alert_data.get('weapon_type', 'Unknown')}
• Confidence: {alert_data.get('confidence', 0):.2%}
• Immediate action required!
            """
        elif alert_data.get('type') == 'SPOOF_ATTEMPT':
            return f"""
• Spoofing attempt detected
• Method: {alert_data.get('spoof_method', 'Unknown')}
• Security breach attempted
            """
        return "• Check live feed for details"
    
    def _upload_media(self, file_path: str) -> str:
        """Upload media to Twilio (simplified - use your own storage)"""
        # In production, upload to cloud storage and return URL
        # For demo, use local file (Twilio requires public URL)
        return "https://your-storage.com/path/to/image.jpg"