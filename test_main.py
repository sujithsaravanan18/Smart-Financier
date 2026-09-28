import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

from database import Base, get_db
from main import app
import models

# Use an in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_smart_financier.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_customer():
    response = client.post(
        "/api/customers/",
        json={"name": "Alice Smith", "phone_number": "+1234567890", "email": "alice@example.com"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice Smith"
    assert data["phone_number"] == "+1234567890"
    assert "id" in data

    # Test duplicate phone number
    response = client.post(
        "/api/customers/",
        json={"name": "Bob Jones", "phone_number": "+1234567890"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Phone number already registered"

def test_create_loan():
    # 1. Create Customer first
    cust_resp = client.post(
        "/api/customers/",
        json={"name": "Bob Jones", "phone_number": "+1987654321"},
    )
    cust_id = cust_resp.json()["id"]

    # 2. Create Loan
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    loan_resp = client.post(
        "/api/loans/",
        json={
            "customer_id": cust_id,
            "principal_amount": "1000.00",
            "total_amount_due": "1100.00",
            "due_date": tomorrow
        }
    )
    assert loan_resp.status_code == 201
    loan_data = loan_resp.json()
    assert loan_data["balance_remaining"] == "1100.00"
    assert loan_data["status"] == "ACTIVE"

def test_payment_updates_loan():
    # Setup customer & loan
    cust_resp = client.post(
        "/api/customers/",
        json={"name": "Charlie Brown", "phone_number": "+1555555555"},
    )
    cust_id = cust_resp.json()["id"]

    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    loan_resp = client.post(
        "/api/loans/",
        json={
            "customer_id": cust_id,
            "principal_amount": "500.00",
            "total_amount_due": "550.00",
            "due_date": tomorrow
        }
    )
    loan_id = loan_resp.json()["id"]

    # Log partial payment of 200
    pay_resp = client.post(
        "/api/payments/",
        json={"loan_id": loan_id, "amount_paid": "200.00", "notes": "First installment"}
    )
    assert pay_resp.status_code == 201
    
    # Verify loan remaining balance
    loan_check = client.get(f"/api/loans/{loan_id}")
    assert loan_check.json()["balance_remaining"] == "350.00"
    assert loan_check.json()["status"] == "ACTIVE"

    # Log overpayment check
    pay_over = client.post(
        "/api/payments/",
        json={"loan_id": loan_id, "amount_paid": "400.00"}
    )
    assert pay_over.status_code == 400
    assert "exceeds the remaining balance" in pay_over.json()["detail"]

    # Log final payment of 350
    pay_final = client.post(
        "/api/payments/",
        json={"loan_id": loan_id, "amount_paid": "350.00"}
    )
    assert pay_final.status_code == 201

    # Verify loan status updated to PAID
    loan_check_final = client.get(f"/api/loans/{loan_id}")
    assert loan_check_final.json()["balance_remaining"] == "0.00"
    assert loan_check_final.json()["status"] == "PAID"

def test_reminders_trigger():
    # Setup customer & loan due tomorrow
    cust_resp = client.post(
        "/api/customers/",
        json={"name": "David Miller", "phone_number": "+1444444444"},
    )
    cust_id = cust_resp.json()["id"]

    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    client.post(
        "/api/loans/",
        json={
            "customer_id": cust_id,
            "principal_amount": "300.00",
            "total_amount_due": "330.00",
            "due_date": tomorrow
        }
    )

    # Trigger reminder check
    reminder_resp = client.post("/api/reminders/trigger-check/")
    assert reminder_resp.status_code == 200
    data = reminder_resp.json()
    assert data["total_reminders_triggered"] == 1
    assert data["reminders"][0]["customer_name"] == "David Miller"
    assert "+144444444" in data["reminders"][0]["phone_number"]
