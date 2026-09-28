from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from flask_babel import _
from app.creditor import bp
from app.models import Beneficiary, Debtor
from app.extensions import db
from app.middleware.auth import roles_required

@bp.route('/beneficiaries', methods=['GET', 'POST'])
@login_required
@roles_required('Creditor')
def beneficiaries():
    creditor_id = current_user.creditor_profile.id
    if request.method == 'POST':
        name = request.form.get('name')
        account = request.form.get('bank_account_number')
        bank = request.form.get('bank_name')
        ifsc = request.form.get('ifsc_code')
        
        b = Beneficiary(creditor_id=creditor_id, name=name, bank_account_number=account, bank_name=bank, ifsc_code=ifsc)
        db.session.add(b)
        db.session.commit()
        from app.services.audit import log_audit
        log_audit('Created Beneficiary', 'beneficiaries', b.id, f"Beneficiary name: {name}")
        flash(_('Beneficiary added successfully.'), 'success')
        return redirect(url_for('creditor.beneficiaries'))
        
    b_list = Beneficiary.query.filter_by(creditor_id=creditor_id, deleted_at=None).all()
    return render_template('creditor/beneficiaries.html', title=_('Beneficiaries'), beneficiaries=b_list)

@bp.route('/debtors', methods=['GET', 'POST'])
@login_required
@roles_required('Creditor')
def debtors():
    creditor_id = current_user.creditor_profile.id
    if request.method == 'POST':
        name = request.form.get('full_name')
        phone = request.form.get('phone_number')
        address = request.form.get('address')
        
        d = Debtor(creditor_id=creditor_id, full_name=name, phone_number=phone, address=address)
        db.session.add(d)
        db.session.commit()
        from app.services.audit import log_audit
        log_audit('Created Debtor', 'debtors', d.id, f"Debtor name: {name}")
        flash(_('Debtor added successfully.'), 'success')
        return redirect(url_for('creditor.debtors'))
        
    d_list = Debtor.query.filter_by(creditor_id=creditor_id, deleted_at=None).all()
    return render_template('creditor/debtors.html', title=_('Debtors'), debtors=d_list)
