import csv
import io
from app.models import Loan, Payment, User

class ReportingService:
    @staticmethod
    def generate_loan_report_csv():
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Loan ID', 'Creditor', 'Debtor', 'Principal', 'Outstanding Balance', 'Status', 'Issue Date', 'Due Date'])
        
        loans = Loan.query.all()
        for loan in loans:
            writer.writerow([
                loan.id,
                loan.creditor.user.username if loan.creditor and loan.creditor.user else 'N/A',
                loan.debtor.user.username if loan.debtor and loan.debtor.user else 'N/A',
                loan.principal_amount,
                loan.outstanding_balance,
                loan.status.value,
                loan.issue_date.strftime('%Y-%m-%d') if loan.issue_date else 'N/A',
                loan.due_date.strftime('%Y-%m-%d') if loan.due_date else 'N/A'
            ])
            
        return output.getvalue()
