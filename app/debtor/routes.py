from flask import redirect, url_for
from app.debtor import bp

@bp.route('/')
def index():
    return redirect(url_for('dashboard.debtor_dashboard'))
