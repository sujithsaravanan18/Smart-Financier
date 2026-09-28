from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from decimal import Decimal
import datetime
from models import LoanStatus

class CustomerBase(BaseModel):
    name: str
    phone_number: str
    email: Optional[EmailStr] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class LoanBase(BaseModel):
    customer_id: str
    principal_amount: Decimal = Field(..., max_digits=10, decimal_places=2)
    total_amount_due: Decimal = Field(..., max_digits=10, decimal_places=2)
    due_date: datetime.date

class LoanCreate(LoanBase):
    issue_date: Optional[datetime.date] = None

class LoanResponse(LoanBase):
    id: str
    balance_remaining: Decimal
    status: LoanStatus
    issue_date: datetime.date
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class PaymentBase(BaseModel):
    loan_id: str
    amount_paid: Decimal = Field(..., max_digits=10, decimal_places=2)
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    payment_date: Optional[datetime.date] = None

class PaymentResponse(PaymentBase):
    id: str
    payment_date: datetime.date
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class CustomerDetailResponse(CustomerResponse):
    loans: List[LoanResponse] = []

    class Config:
        orm_mode = True
