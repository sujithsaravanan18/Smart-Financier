from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def roles_required(*roles):
    """
    Decorator to ensure that the current user has one of the specified roles.
    Assumes current_user.is_authenticated has already been checked or is handled by @login_required.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if not current_user.role or current_user.role.name not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
