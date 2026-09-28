import uuid
import datetime
from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
import enum

class LoanStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAID = "PAID"
    OVERDUE = "OVERDUE"

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    loans = relationship("Loan", back_populates="customer", cascade="all, delete-orphan")

class Loan(Base):
    __tablename__ = "loans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    principal_amount = Column(Numeric(10, 2), nullable=False)
    total_amount_due = Column(Numeric(10, 2), nullable=False)
    balance_remaining = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLEnum(LoanStatus), default=LoanStatus.ACTIVE, nullable=False)
    issue_date = Column(Date, default=lambda: datetime.date.today())
    due_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    customer = relationship("Customer", back_populates="loans")
    payments = relationship("Payment", back_populates="loan", cascade="all, delete-orphan")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    loan_id = Column(String, ForeignKey("loans.id", ondelete="CASCADE"), nullable=False)
    amount_paid = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(Date, default=lambda: datetime.date.today())
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    loan = relationship("Loan", back_populates="payments")
