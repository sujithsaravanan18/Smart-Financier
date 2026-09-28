from flask import Blueprint, request, abort, redirect, url_for, flash
from flask_login import current_user
from app.middleware.auth import roles_required

bp = Blueprint('admin', __name__)

@bp.before_request
def require_admin():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.url))
    if not current_user.role or current_user.role.name != 'Super Admin':
        flash('You do not have permission to access the admin portal.', 'danger')
        return redirect(url_for('main.index'))

from app.admin import routes
