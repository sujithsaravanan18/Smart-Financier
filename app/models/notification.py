from app.extensions import db
from app.models.base import TimestampMixin, generate_uuid

class Notification(db.Model, TimestampMixin):
    __tablename__ = 'notifications'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20)) # WhatsApp, Email, System
    status = db.Column(db.String(20), default='Pending') # Sent, Failed, Pending
    sent_at = db.Column(db.DateTime)
