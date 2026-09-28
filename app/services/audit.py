from app.extensions import db
from app.models import AuditLog, ErrorLog
from flask_login import current_user
import traceback

def log_audit(action, table_name=None, record_id=None, details=None):
    """
    Creates an AuditLog entry.
    """
    user_id = current_user.id if current_user and current_user.is_authenticated else None
    
    log = AuditLog(
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        details=details
    )
    db.session.add(log)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

def log_error(error_message, exc_info=None):
    """
    Creates an ErrorLog entry.
    """
    stack_trace = None
    if exc_info:
        stack_trace = "".join(traceback.format_exception(type(exc_info), exc_info, exc_info.__traceback__))
        
    log = ErrorLog(
        error_message=str(error_message),
        stack_trace=stack_trace
    )
    db.session.add(log)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
