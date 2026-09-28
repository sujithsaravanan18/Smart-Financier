from flask import render_template
from flask_babel import _
from app.admin import bp
from app.models import User
from app.middleware.auth import roles_required
from flask_login import login_required

@bp.route('/users')
@login_required
@roles_required('Super Admin')
def users():
    users_list = User.query.all()
    return render_template('admin/users.html', title=_('User Management'), users=users_list)
