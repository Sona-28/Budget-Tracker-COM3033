# tests/test_transactions.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import Base, engine, SessionLocal

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown - drop tables
    Base.metadata.drop_all(bind=engine)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_create_and_get_transaction():
    payload = {
	"title": "Test transaction",
        "category": "Test",
        "amount": 15.00,
        "type": "expense",
        "description": "unit test",
        "date": "2025-01-01T00:00:00"
    }
    r = client.post("/api/v1/transactions", json=payload)
    assert r.status_code == 201

    data = r.json()
    assert data["title"] == payload["title"]
    assert data["amount"] == payload["amount"]
    assert data["type"] == payload["type"]

    r = client.get("/api/v1/transactions")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
