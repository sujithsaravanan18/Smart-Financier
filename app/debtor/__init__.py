from flask import Blueprint, request, redirect, url_for, flash
from flask_login import current_user

bp = Blueprint('debtor', __name__)

@bp.before_request
def require_debtor():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.url))
    if not current_user.role or current_user.role.name != 'Debtor':
        flash('You do not have permission to access the debtor portal.', 'danger')
        return redirect(url_for('main.index'))
    
    # Ensure they have a linked Debtor profile
    if not current_user.debtor_profile:
        flash('No active debtor profile assigned. Please contact your creditor to link your account.', 'warning')
        return redirect(url_for('auth.logout'))

from app.debtor import routes
