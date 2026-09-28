from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app.auth import bp
from app.models import User
from app.extensions import db, limiter

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'

        user = User.query.filter_by(username=username).first()
        print(f"DEBUG: username={username}, password={password}, user={user}")
        from app.services.audit import log_audit
        
        if user is None or not user.check_password(password):
            if user:
                log_audit('Failed Login - Bad Password', 'users', user.id)
            else:
                # Can't log user_id easily if we don't pass it or context
                pass
            flash(_('Invalid username or password'), 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            log_audit('Failed Login - Deactivated', 'users', user.id)
            flash(_('This account has been deactivated.'), 'warning')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember_me)
        log_audit('Login Successful', 'users', user.id)
        
        # Role-based redirect
        if user.role:
            if user.role.name == 'Super Admin':
                return redirect(url_for('dashboard.admin_dashboard'))
            elif user.role.name == 'Creditor':
                return redirect(url_for('dashboard.creditor_dashboard'))
            elif user.role.name == 'Debtor':
                return redirect(url_for('dashboard.debtor_dashboard'))
            
        return redirect(url_for('main.index'))

    return render_template('auth/login.html', title=_('Sign In'))

@bp.route('/logout')
def logout():
    from app.services.audit import log_audit
    log_audit('Logout Successful', 'users', current_user.id)
    logout_user()
    flash(_('You have been logged out.'), 'info')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role_name = request.form.get('role')
        
        from app.models import Role, Creditor, Debtor
        
        if User.query.filter_by(username=username).first():
            flash(_('Please use a different username.'), 'danger')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash(_('Please use a different email address.'), 'danger')
            return redirect(url_for('auth.register'))
            
        role = Role.query.filter_by(name=role_name).first()
        if not role or role.name == 'Super Admin':
            flash(_('Invalid role selected.'), 'danger')
            return redirect(url_for('auth.register'))
            
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush() # Get user.id
        
        if role.name == 'Creditor':
            creditor = Creditor(user_id=user.id, company_name=f"{username}'s Company")
            db.session.add(creditor)
        elif role.name == 'Debtor':
            # Create a detached debtor profile, needs a creditor later
            debtor = Debtor(user_id=user.id, full_name=username, phone_number="")
            db.session.add(debtor)
            
        db.session.commit()
        from app.services.audit import log_audit
        log_audit('User Registered', 'users', user.id)
        
        flash(_('Congratulations, you are now a registered user!'), 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', title=_('Register'))

@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.get_reset_password_token()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            # Simulate sending email by logging/flashing
            print(f"DEBUG: Password reset link for {email}: {reset_url}")
            flash(_('A password reset link has been generated. Since email is not configured, please check the server logs for the link: %(url)s', url=reset_url), 'info')
        else:
            flash(_('If an account with that email exists, password reset instructions have been sent.'), 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/forgot_password.html', title=_('Forgot Password'))

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    user = User.verify_reset_password_token(token)
    if not user:
        flash(_('The password reset link is invalid or has expired.'), 'danger')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        password = request.form.get('password')
        user.set_password(password)
        db.session.commit()
        
        from app.services.audit import log_audit
        log_audit('Password Reset', 'users', user.id)
        
        flash(_('Your password has been reset.'), 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html', title=_('Reset Password'))
