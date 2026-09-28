from datetime import datetime, timezone
from app.extensions import db
from app.models.base import generate_uuid

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(128))
    table_name = db.Column(db.String(64))
    record_id = db.Column(db.String(36))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class ErrorLog(db.Model):
    __tablename__ = 'error_logs'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    error_message = db.Column(db.Text, nullable=False)
    stack_trace = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
