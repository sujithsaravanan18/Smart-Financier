from flask import render_template, redirect, url_for
from flask_login import current_user, login_required
from flask_babel import _
from app.dashboard import bp
from app.models import User, Creditor, Debtor, Loan, Payment, Role
from app.middleware.auth import roles_required

@bp.route('/')
@login_required
def index():
    if current_user.role.name == 'Super Admin':
        return redirect(url_for('dashboard.admin_dashboard'))
    elif current_user.role.name == 'Creditor':
        return redirect(url_for('dashboard.creditor_dashboard'))
    elif current_user.role.name == 'Debtor':
        return redirect(url_for('dashboard.debtor_dashboard'))
    return redirect(url_for('main.index'))

from app.extensions import cache

@bp.route('/admin')
@login_required
@roles_required('Super Admin')
@cache.cached(timeout=60, key_prefix='admin_dash')
def admin_dashboard():
    user_count = User.query.count()
    loan_count = Loan.query.count()
    payment_count = Payment.query.count()
    
    roles = Role.query.all()
    role_labels = [r.name for r in roles]
    role_counts = [User.query.filter_by(role_id=r.id).count() for r in roles]
    
    from datetime import datetime, date
    from dateutil.relativedelta import relativedelta
    
    today = date.today()
    months = [(today - relativedelta(months=i)).strftime('%Y-%m') for i in range(5, -1, -1)]
    monthly_payments = {m: 0 for m in months}
    
    all_payments = Payment.query.all()
    for p in all_payments:
        month_key = p.payment_date.strftime('%Y-%m')
        if month_key in monthly_payments:
            monthly_payments[month_key] += float(p.amount)
            
    stats = {
        'users': user_count,
        'loans': loan_count,
        'payments': payment_count,
        'role_labels': role_labels,
        'role_counts': role_counts,
        'month_labels': months,
        'monthly_data': [monthly_payments[m] for m in months]
    }
    return render_template('admin/dashboard.html', title=_('Admin Dashboard'), stats=stats)

@bp.route('/creditor')
@login_required
@roles_required('Creditor')
@cache.cached(timeout=60, key_prefix=lambda: f"creditor_dash_{current_user.id}")
def creditor_dashboard():
    creditor_id = current_user.creditor_profile.id
    
    total_debtors = Debtor.query.filter_by(creditor_id=creditor_id).count()
    loans = Loan.query.filter_by(creditor_id=creditor_id).all()
    total_loans = len(loans)
    
    total_principal = sum(loan.principal_amount for loan in loans)
    outstanding_balance = sum(loan.outstanding_balance for loan in loans)
    total_collected = total_principal - outstanding_balance
    
    from datetime import datetime, date
    from dateutil.relativedelta import relativedelta
    
    today = date.today()
    months = [(today - relativedelta(months=i)).strftime('%Y-%m') for i in range(5, -1, -1)]
    monthly_collections = {m: 0 for m in months}
    
    payments = Payment.query.join(Loan).filter(Loan.creditor_id == creditor_id).all()
    for p in payments:
        month_key = p.payment_date.strftime('%Y-%m')
        if month_key in monthly_collections:
            monthly_collections[month_key] += float(p.amount)

    stats = {
        'total_debtors': total_debtors,
        'total_loans': total_loans,
        'outstanding_balance': outstanding_balance,
        'total_collected': total_collected,
        'month_labels': months,
        'monthly_data': [monthly_collections[m] for m in months]
    }
    return render_template('creditor/dashboard.html', title=_('Creditor Dashboard'), stats=stats)

@bp.route('/debtor')
@login_required
@roles_required('Debtor')
@cache.cached(timeout=60, key_prefix=lambda: f"debtor_dash_{current_user.id}")
def debtor_dashboard():
    debtor_id = current_user.debtor_profile.id
    loans = Loan.query.filter_by(debtor_id=debtor_id).all()
    
    total_principal = sum(loan.principal_amount for loan in loans)
    total_balance = sum(loan.outstanding_balance for loan in loans)
    total_paid = total_principal - total_balance
    
    loan_data = []
    for loan in loans:
        paid = loan.principal_amount - loan.outstanding_balance
        loan_data.append({
            'loan': loan,
            'paid': paid,
            'balance': loan.outstanding_balance,
            'progress': (paid / loan.principal_amount * 100) if loan.principal_amount > 0 else 0
        })
        
    overall_progress = (total_paid / total_principal * 100) if total_principal > 0 else 0

    stats = {
        'total_principal': total_principal,
        'total_paid': total_paid,
        'overall_progress': overall_progress
    }
    return render_template('debtor/dashboard.html', title=_('Debtor Dashboard'), loans=loan_data, stats=stats)

@bp.route('/export/csv')
@login_required
@roles_required('Super Admin')
def export_csv():
    from flask import Response
    from app.services.reporting_service import ReportingService
    import datetime
    
    csv_data = ReportingService.generate_loan_report_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=loan_report_{datetime.date.today()}.csv"}
    )

