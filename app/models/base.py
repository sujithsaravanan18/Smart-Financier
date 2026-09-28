import uuid
from datetime import datetime, timezone
from app.extensions import db

def generate_uuid():
    return str(uuid.uuid4())

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class SoftDeleteMixin:
    deleted_at = db.Column(db.DateTime, nullable=True)
