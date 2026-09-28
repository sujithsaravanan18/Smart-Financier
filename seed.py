from app import create_app
from app.extensions import db
from app.models import User, Role

app = create_app()

with app.app_context():
    # 1. Create Roles
    roles = ['Super Admin', 'Creditor', 'Debtor']
    for r_name in roles:
        if not Role.query.filter_by(name=r_name).first():
            role = Role(name=r_name)
            db.session.add(role)
    db.session.commit()

    # 2. Create Users
    users_data = [
        ('admin', 'admin@example.com', 'admin123', 'Super Admin'),
        ('creditor1', 'creditor1@example.com', 'cred123', 'Creditor'),
        ('debtor1', 'debtor1@example.com', 'deb123', 'Debtor')
    ]

    for username, email, password, role_name in users_data:
        if not User.query.filter_by(username=username).first():
            role = Role.query.filter_by(name=role_name).first()
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
    db.session.commit()

    # 3. Create Sample Creditor Data
    from app.models import Creditor, Debtor, Loan, Payment
    from datetime import date, timedelta
    creditor_user = User.query.filter_by(username='creditor1').first()
    if creditor_user and not creditor_user.creditor_profile:
        creditor = Creditor(user_id=creditor_user.id, company_name="Creditor One Finance")
        db.session.add(creditor)
        db.session.commit()
        
        # Add a Debtor and link to user
        debtor_user = User.query.filter_by(username='debtor1').first()
        debtor = Debtor(creditor_id=creditor.id, user_id=debtor_user.id if debtor_user else None, full_name="John Doe", phone_number="1234567890", address="123 Main St")
        db.session.add(debtor)
        db.session.commit()
        
        # Add a Loan
        loan = Loan(creditor_id=creditor.id, debtor_id=debtor.id, principal_amount=5000.00, outstanding_balance=4500.00, interest_rate=12.5, start_date=date.today() - timedelta(days=30), end_date=date.today() + timedelta(days=30))
        db.session.add(loan)
        db.session.commit()
        
        # Add a Payment
        payment = Payment(loan_id=loan.id, amount=500.00, payment_date=date.today() - timedelta(days=5), payment_method="Bank Transfer")
        db.session.add(payment)
        db.session.commit()
    print("Seed data successfully created!")
    print("Test Accounts:")
    print("- Admin: admin / admin123")
    print("- Creditor: creditor1 / cred123")
    print("- Debtor: debtor1 / deb123")
