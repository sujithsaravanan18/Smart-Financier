import os
import requests
from app.extensions import db
from app.models import Notification
from datetime import datetime, timezone

class WhatsAppClient:
    def __init__(self):
        self.token = os.environ.get('WHATSAPP_TOKEN')
        self.phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
        self.base_url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
        self.mock_mode = not (self.token and self.phone_number_id)

    def send_message(self, user_id, phone_number, message_text):
        """
        Sends a WhatsApp message. If credentials are not set, falls back to mock mode.
        Logs the notification to the database.
        """
        status = 'Pending'
        
        if self.mock_mode:
            print(f"[MOCK WHATSAPP] To: {phone_number} | Message: {message_text}")
            status = 'Sent'
        else:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {"body": message_text}
            }
            try:
                response = requests.post(self.base_url, headers=headers, json=payload, timeout=5)
                if response.status_code in [200, 201]:
                    status = 'Sent'
                else:
                    status = 'Failed'
                    print(f"WhatsApp API Error: {response.text}")
            except Exception as e:
                status = 'Failed'
                print(f"WhatsApp Request Exception: {str(e)}")

        # Log to database
        notification = Notification(
            user_id=user_id,
            message=message_text,
            type='WhatsApp',
            status=status,
            sent_at=datetime.now(timezone.utc) if status == 'Sent' else None
        )
        db.session.add(notification)
        db.session.commit()
        
        try:
            from app.services.audit import log_audit
            log_audit(f'WhatsApp Notification {status}', 'notifications', notification.id)
        except Exception:
            pass
        return status == 'Sent' or self.mock_mode
