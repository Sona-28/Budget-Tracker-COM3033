# scripts/seed_data.py
from app.database.connection import SessionLocal, engine, Base
from app.models.transaction import Transaction, TransactionType
from datetime import datetime

Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    db.query(Transaction).delete()
    db.add(Transaction(user_id="550e8400-e29b-41d4-a716-446655440000", category="Groceries", amount=12.5, type=TransactionType.expense, description="Milk"))
    db.add(Transaction(user_id="550e8400-e29b-41d4-a716-446655440000", category="Salary", amount=1200.0, type=TransactionType.income, description="Monthly salary"))
    db.commit()
    db.close()
    print("Seeded data")

if __name__ == "__main__":
    seed()
