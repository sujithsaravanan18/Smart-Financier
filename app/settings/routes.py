from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from flask_babel import _
from app.settings import bp
from app.models import Setting
from app.extensions import db
from app.middleware.auth import roles_required

@bp.route('/')
@login_required
def index():
    if current_user.role.name == 'Super Admin':
        return redirect(url_for('settings.admin_settings'))
    elif current_user.role.name == 'Creditor':
        return redirect(url_for('settings.creditor_settings'))
    elif current_user.role.name == 'Debtor':
        return redirect(url_for('settings.debtor_settings'))
    return redirect(url_for('main.index'))

@bp.route('/admin', methods=['GET', 'POST'])
@login_required
@roles_required('Super Admin')
def admin_settings():
    if request.method == 'POST':
        default_lang = request.form.get('default_language')
        lang_setting = Setting.query.filter_by(setting_key='DEFAULT_LANGUAGE').first()
        if not lang_setting:
            lang_setting = Setting(setting_key='DEFAULT_LANGUAGE')
            db.session.add(lang_setting)
        lang_setting.setting_value = default_lang
        db.session.commit()
        from app.services.audit import log_audit
        log_audit('Updated Global Settings', 'settings', lang_setting.id, f"Default Language: {default_lang}")
        flash(_('Settings updated successfully.'), 'success')
        return redirect(url_for('settings.admin_settings'))
        
    current_lang = Setting.query.filter_by(setting_key='DEFAULT_LANGUAGE').first()
    lang_val = current_lang.setting_value if current_lang else 'en'
    return render_template('admin/settings.html', title=_('Global Settings'), current_lang=lang_val)

@bp.route('/creditor', methods=['GET', 'POST'])
@login_required
@roles_required('Creditor')
def creditor_settings():
    creditor = current_user.creditor_profile
    if request.method == 'POST':
        company_name = request.form.get('company_name')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')
        
        creditor.company_name = company_name
        creditor.phone_number = phone_number
        creditor.address = address
        db.session.commit()
        from app.services.audit import log_audit
        log_audit('Updated Settings', 'creditors', creditor.id)
        flash(_('Creditor profile updated.'), 'success')
        return redirect(url_for('settings.creditor_settings'))
        
    return render_template('creditor/settings.html', title=_('Settings'), creditor=creditor)

@bp.route('/debtor', methods=['GET', 'POST'])
@login_required
@roles_required('Debtor')
def debtor_settings():
    debtor = current_user.debtor_profile
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')
        
        debtor.full_name = full_name
        debtor.phone_number = phone_number
        debtor.address = address
        db.session.commit()
        from app.services.audit import log_audit
        log_audit('Updated Settings', 'debtors', debtor.id)
        flash(_('Debtor profile updated.'), 'success')
        return redirect(url_for('settings.debtor_settings'))
        
    return render_template('debtor/settings.html', title=_('Settings'), debtor=debtor)
