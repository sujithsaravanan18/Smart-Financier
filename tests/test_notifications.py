from app.services.whatsapp import WhatsAppClient
from app.models import Notification, User
from app.extensions import db

def test_whatsapp_logging(app, init_database):
    with app.app_context():
        user = User(username='notif_user', email='notif@test.com')
        user.set_password('pass')
        db.session.add(user)
        db.session.commit()
        
        client = WhatsAppClient()
        client.mock_mode = True
        
        result = client.send_message(user_id=user.id, phone_number='1234567890', message_text='Test Message')
        assert result is True
        
        notification = Notification.query.first()
        assert notification is not None
        assert notification.message == 'Test Message'
        assert notification.status == 'Sent'
        assert notification.type == 'WhatsApp'
