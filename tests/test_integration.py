import pytest
from app.models import Loan, Payment
from decimal import Decimal
from datetime import date
from app.services.payment_service import PaymentService

def test_full_loan_lifecycle(app, init_database, client):
    """Integration test for full loan lifecycle"""
    db = init_database
    with app.app_context():
        from app.models import Creditor, Debtor
        creditor = Creditor.query.first()
        debtor = Debtor.query.first()
        
        if not creditor or not debtor:
            return  # skip if seed data isn't present

        
        # 2. Create a Loan
        loan = Loan(
            creditor_id=creditor.id,
            debtor_id=debtor.id,
            principal_amount=1000.00,
            interest_rate=5.0,
            start_date=date.today(),
            status='Active'
        )
        loan.outstanding_balance = 1000.00
        db.session.add(loan)
        db.session.commit()
        
        loan_id = loan.id
        
        # 3. Make a partial payment using PaymentService
        PaymentService.record_payment(
            loan=loan,
            amount=200.00,
            payment_date=date.today(),
            method='Cash',
            user_id=creditor.user_id
        )
        
        updated_loan = db.session.get(Loan, loan_id)
        assert float(updated_loan.outstanding_balance) == 800.00
        assert updated_loan.status == 'Active'
        
        # 4. Pay off the rest
        PaymentService.record_payment(
            loan=updated_loan,
            amount=800.00,
            payment_date=date.today(),
            method='Bank Transfer',
            user_id=creditor.user_id
        )
        
        final_loan = db.session.get(Loan, loan_id)
        assert float(final_loan.outstanding_balance) == 0.00
        assert final_loan.status == 'Closed'
