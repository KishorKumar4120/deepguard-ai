"""
Telegram Bot Integration
"""
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackContext
import asyncio
import logging
import os
from dotenv import load_dotenv
import cv2

load_dotenv()
logger = logging.getLogger(__name__)

class TelegramAlert:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.bot = None
        self.application = None
        
        if self.token:
            self.bot = Bot(token=self.token)
            self.enabled = True
            logger.info("Telegram alerts enabled")
        else:
            self.enabled = False
            logger.warning("Telegram alerts disabled - missing token")
    
    async def send_alert(self, alert_data: dict, frame: np.ndarray):
        """Send Telegram alert with image and inline keyboard"""
        if not self.enabled:
            return False
        
        try:
            # Save frame temporarily
            temp_path = f"temp_telegram_{alert_data.get('timestamp', '')}.jpg"
            cv2.imwrite(temp_path, frame)
            
            # Prepare keyboard
            keyboard = [
                [
                    InlineKeyboardButton("📹 Live Stream", callback_data="live"),
                    InlineKeyboardButton("📍 Location", callback_data="location")
                ],
                [
                    InlineKeyboardButton("🚨 Dispatch Security", callback_data="dispatch"),
                    InlineKeyboardButton("✅ Acknowledge", callback_data="ack")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send photo with caption
            with open(temp_path, 'rb') as photo:
                message = await self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=photo,
                    caption=self._format_caption(alert_data),
                    reply_markup=reply_markup
                )
            
            # Cleanup
            os.remove(temp_path)
            
            logger.info(f"Telegram alert sent: {message.message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Telegram alert failed: {e}")
            return False
    
    def _format_caption(self, alert_data: dict) -> str:
        """Format alert caption"""
        alert_type = alert_data.get('type', 'UNKNOWN')
        severity = alert_data.get('severity', 'MEDIUM')
        
        emoji = "🔴" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🔵"
        
        caption = f"""
{emoji} *DEEPGUARD AI SECURITY ALERT* {emoji}

*Type:* `{alert_type}`
*Severity:* `{severity}`
*Camera:* `{alert_data.get('camera_name', 'Unknown')}`
*Time:* `{alert_data.get('timestamp', 'N/A')}`

*Actions Available:*
• Press buttons below to respond
• View live stream
• Dispatch security team
• Acknowledge alert

---
_ID: {alert_data.get('alert_id', 'N/A')}_
        """
        return caption

# Singleton
telegram_alert = TelegramAlert()