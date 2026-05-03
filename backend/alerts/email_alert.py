import smtplib
import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmailAlert:
    def __init__(self):
        # Email configuration - will be loaded from environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.sender_email = os.getenv("SMTP_SENDER")
        self.sender_password = os.getenv("SMTP_PASSWORD")  # Use App Password!
        self.receiver_email = os.getenv("ALERT_RECEIVER")
        
    def send_alert(self, frame, person_name="Unknown Person", camera_name="Unknown Camera"):
        """Send email alert with attached photo"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save the frame as a temporary image
            import cv2
            temp_path = f"temp_alert_{timestamp}.jpg"
            cv2.imwrite(temp_path, frame)
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.receiver_email
            msg['Subject'] = f"🚨 SECURITY ALERT - {person_name} detected at {timestamp}"
            
            # Email body
            body = f"""
            <html>
            <body>
            <h2>⚠️ Security Alert!</h2>
            <p><b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><b>Location:</b> {camera_name}</p>
            <p><b>Person:</b> {person_name}</p>
            <p><b>Action Required:</b> Unknown person detected. Please check the attached photo.</p>
            <hr>
            <p><i>This is an automated alert from your DeepGuard AI Security System.</i></p>
            </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html'))
            
            # Attach the photo
            with open(temp_path, 'rb') as f:
                img_data = f.read()
                image = MIMEImage(img_data, name=f"security_alert_{timestamp}.jpg")
                msg.attach(image)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            # Clean up temp file
            os.remove(temp_path)
            
            logger.info(f"Alert email sent to {self.receiver_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
