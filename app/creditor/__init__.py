from flask import Blueprint, request, redirect, url_for, flash
from flask_login import current_user
from app.middleware.auth import roles_required

bp = Blueprint('creditor', __name__)

@bp.before_request
def require_creditor():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.url))
    if not current_user.role or current_user.role.name != 'Creditor':
        flash('You do not have permission to access the creditor portal.', 'danger')
        return redirect(url_for('main.index'))
    
    # Ensure they have a Creditor profile
    if not current_user.creditor_profile:
        from app.models import Creditor
        from app.extensions import db
        # Auto-create profile if missing (can also be done in user registration)
        profile = Creditor(user_id=current_user.id, company_name=current_user.username + " Finance")
        db.session.add(profile)
        db.session.commit()

from app.creditor import routes
