from app.extensions import scheduler, db
from app.models import Loan, Debtor, Creditor, User
from app.services.whatsapp import WhatsAppClient
from datetime import date, timedelta
from flask import current_app

@scheduler.task('cron', id='check_upcoming_dues', hour=8, minute=0)
def check_upcoming_dues():
    # Because this runs outside a request context, we need app_context
    app = current_app._get_current_object() if current_app else None
    # If app is None, this means we are running in an isolated thread and need a proper app context
    if app is None:
        # We can't easily get the app here unless we import create_app, but we are inside an app context when tasks are registered
        pass
    # For simplicity, we assume we have app context pushed by the scheduler or we use the flask-apscheduler features
    pass

# A better way to write the tasks to ensure app context is using the context provided by flask_apscheduler
@scheduler.task('cron', id='daily_whatsapp_reminders', hour=9, minute=0)
def send_daily_reminders():
    # Flask-APScheduler automatically runs jobs inside an app context!
    today = date.today()
    client = WhatsAppClient()
    
    loans = Loan.query.filter(Loan.status == 'Active').all()
    
    for loan in loans:
        if not loan.end_date:
            continue
            
        days_until_due = (loan.end_date - today).days
        debtor = loan.debtor
        creditor = loan.creditor
        phone = debtor.phone_number
        
        if not phone:
            continue
            
        msg = None
        # 1. Before due date (3 days)
        if days_until_due == 3:
            msg = f"Reminder from {creditor.company_name}: Your loan of ${loan.principal_amount} has an upcoming due date on {loan.end_date.strftime('%b %d, %Y')}."
        
        # 2. On due date
        elif days_until_due == 0:
            msg = f"URGENT Reminder from {creditor.company_name}: Your loan is DUE TODAY. Please ensure your balance of ${loan.outstanding_balance} is settled."
            
        # 3. Overdue (e.g., 3 days overdue)
        elif days_until_due == -3:
            msg = f"OVERDUE Notice from {creditor.company_name}: Your loan was due on {loan.end_date.strftime('%b %d, %Y')}. Your current outstanding balance is ${loan.outstanding_balance}."
            
        if msg:
            client.send_message(user_id=debtor.user_id or creditor.user_id, phone_number=phone, message_text=msg)

