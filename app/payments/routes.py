from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from flask_babel import _
from app.payments import bp
from app.models import Payment, Loan
from app.extensions import db
from datetime import datetime
from decimal import Decimal
from app.middleware.auth import roles_required

@bp.route('/<loan_id>', methods=['GET', 'POST'])
@login_required
@roles_required('Creditor')
def manage(loan_id):
    creditor_id = current_user.creditor_profile.id
    loan = Loan.query.filter_by(id=loan_id, creditor_id=creditor_id).first_or_404()
    
    if request.method == 'POST':
        from app.services.payment_service import PaymentService
        try:
            amount = float(request.form.get('amount', 0))
            date_str = request.form.get('payment_date')
            method = request.form.get('payment_method')
            payment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            PaymentService.record_payment(
                loan=loan,
                amount=amount,
                payment_date=payment_date,
                method=method,
                user_id=current_user.id
            )
            flash(_('Payment recorded successfully.'), 'success')
        except ValueError as ve:
            flash(_(str(ve)), 'danger')
        except Exception as e:
            flash(_('An error occurred while recording the payment.'), 'danger')
            
        return redirect(url_for('payments.manage', loan_id=loan.id))
        
    p_list = Payment.query.filter_by(loan_id=loan.id, deleted_at=None).all()
    return render_template('creditor/payments.html', title=_('Payments'), payments=p_list, loan=loan)

@bp.route('/<payment_id>/receipt')
@login_required
def receipt(payment_id):
    if current_user.role.name == 'Creditor':
        creditor_id = current_user.creditor_profile.id
        payment = Payment.query.join(Loan).filter(Payment.id==payment_id, Loan.creditor_id==creditor_id).first_or_404()
    elif current_user.role.name == 'Debtor':
        debtor_id = current_user.debtor_profile.id
        payment = Payment.query.join(Loan).filter(Payment.id==payment_id, Loan.debtor_id==debtor_id).first_or_404()
    else:
        from flask import abort
        abort(403)
        
    return render_template('shared/receipt.html', title=_('Receipt'), payment=payment)
