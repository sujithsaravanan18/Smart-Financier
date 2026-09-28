from flask import render_template
from flask_login import login_required
from flask_babel import _
from app.logs import bp
from app.models import AuditLog, ErrorLog
from app.middleware.auth import roles_required

@bp.route('/')
@login_required
@roles_required('Super Admin')
def index():
    audit_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(50).all()
    error_logs = ErrorLog.query.order_by(ErrorLog.created_at.desc()).limit(50).all()
    return render_template('admin/logs.html', title=_('System Logs'), audit_logs=audit_logs, error_logs=error_logs)
