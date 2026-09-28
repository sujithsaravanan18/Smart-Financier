from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from flask_babel import _
from app.loans import bp
from app.models import Loan, Debtor
from app.extensions import db
from datetime import datetime
from app.middleware.auth import roles_required

@bp.route('/admin')
@login_required
@roles_required('Super Admin')
def admin_overview():
    loans_list = Loan.query.all()
    return render_template('admin/loans.html', title=_('Loans Overview'), loans=loans_list)

@bp.route('/creditor', methods=['GET', 'POST'])
@login_required
@roles_required('Creditor')
def creditor_manage():
    creditor_id = current_user.creditor_profile.id
    if request.method == 'POST':
        debtor_id = request.form.get('debtor_id')
        principal = request.form.get('principal_amount')
        interest = request.form.get('interest_rate')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        if debtor_id and principal and interest and start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            l = Loan(
                creditor_id=creditor_id, 
                debtor_id=debtor_id, 
                principal_amount=principal, 
                outstanding_balance=principal,
                interest_rate=interest, 
                start_date=start_date,
                end_date=end_date
            )
            db.session.add(l)
            db.session.commit()
            
            debtor = Debtor.query.get(debtor_id)
            if debtor.phone_number:
                from app.services.whatsapp import WhatsAppClient
                client = WhatsAppClient()
                msg = f"Hello {debtor.full_name}, a new loan of ${principal} has been assigned to you by {current_user.creditor_profile.company_name}. Due Date: {end_date.strftime('%b %d, %Y')}."
                client.send_message(user_id=debtor.user_id or current_user.id, phone_number=debtor.phone_number, message_text=msg)
                
            flash(_('Loan created successfully.'), 'success')
        else:
            flash(_('All fields are required.'), 'danger')
        return redirect(url_for('loans.creditor_manage'))
        
    l_list = Loan.query.filter_by(creditor_id=creditor_id, deleted_at=None).all()
    d_list = Debtor.query.filter_by(creditor_id=creditor_id, deleted_at=None).all()
    return render_template('creditor/loans.html', title=_('Loans'), loans=l_list, debtors=d_list)

@bp.route('/<loan_id>')
@login_required
@roles_required('Debtor')
def debtor_details(loan_id):
    debtor_id = current_user.debtor_profile.id
    loan = Loan.query.filter_by(id=loan_id, debtor_id=debtor_id).first_or_404()
    
    paid = loan.principal_amount - loan.outstanding_balance
    
    return render_template('debtor/loan_details.html', title=_('Loan Details'), loan=loan, paid=paid, balance=loan.outstanding_balance)
