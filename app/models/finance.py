from app.extensions import db
from app.models.base import TimestampMixin, SoftDeleteMixin, generate_uuid

class Creditor(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = 'creditors'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    company_name = db.Column(db.String(128))
    phone_number = db.Column(db.String(20))
    address = db.Column(db.Text)

    debtors = db.relationship('Debtor', backref='creditor', lazy=True)
    beneficiaries = db.relationship('Beneficiary', backref='creditor', lazy=True)
    loans = db.relationship('Loan', backref='creditor', lazy=True)

class Debtor(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = 'debtors'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    creditor_id = db.Column(db.String(36), db.ForeignKey('creditors.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True, unique=True)
    full_name = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.Text)

    loans = db.relationship('Loan', backref='debtor', lazy=True)

class Beneficiary(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = 'beneficiaries'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    creditor_id = db.Column(db.String(36), db.ForeignKey('creditors.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    bank_account_number = db.Column(db.String(64))
    bank_name = db.Column(db.String(128))
    ifsc_code = db.Column(db.String(20))

class Loan(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = 'loans'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    creditor_id = db.Column(db.String(36), db.ForeignKey('creditors.id'), nullable=False, index=True)
    debtor_id = db.Column(db.String(36), db.ForeignKey('debtors.id'), nullable=False, index=True)
    principal_amount = db.Column(db.Numeric(10, 2), nullable=False)
    outstanding_balance = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, server_default='0.00')
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Active', index=True) # Active, Closed, Defaulted

    payments = db.relationship('Payment', backref='loan', lazy=True)

class Payment(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = 'payments'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    loan_id = db.Column(db.String(36), db.ForeignKey('loans.id'), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False, index=True)
    payment_method = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Completed', index=True) # Completed, Pending, Failed
