from decimal import Decimal
from datetime import datetime
from app.extensions import db
from app.models import Payment
from app.services.audit import log_audit

class PaymentService:
    @staticmethod
    def record_payment(loan, amount: float, payment_date: datetime.date, method: str, user_id=None):
        if amount <= 0:
            raise ValueError('Payment amount must be greater than zero.')
            
        if amount > loan.outstanding_balance:
            raise ValueError('Payment amount exceeds outstanding balance.')
            
        p = Payment(loan_id=loan.id, amount=amount, payment_date=payment_date, payment_method=method, status='Completed')
        
        loan.outstanding_balance -= Decimal(amount)
        if loan.outstanding_balance <= 0:
            loan.status = 'Closed'
            
        db.session.add(p)
        db.session.commit()
        
        log_audit('Recorded Payment', 'payments', p.id, f"Amount: {amount}, Loan: {loan.id}")
        
        # Try sending whatsapp notification
        try:
            if loan.debtor and loan.debtor.phone_number:
                from app.services.whatsapp import WhatsAppClient
                client = WhatsAppClient()
                msg = f"Hello {loan.debtor.full_name}, we have successfully received your payment of ${amount}. Your remaining balance is ${loan.outstanding_balance}. Thank you!"
                client.send_message(user_id=loan.debtor.user_id or user_id, phone_number=loan.debtor.phone_number, message_text=msg)
        except Exception as e:
            # log warning but don't fail the payment
            import logging
            logging.warning(f"Failed to send whatsapp message for payment {p.id}: {e}")
            
        return p
