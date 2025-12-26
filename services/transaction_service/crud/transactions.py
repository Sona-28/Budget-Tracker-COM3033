from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate
from datetime import datetime
from uuid import uuid4

def create_transaction(db: Session, user_id, tx_in: TransactionCreate):
    new = Transaction(
        transaction_id=uuid4(),
        user_id=user_id,
        category_id=tx_in.category_id,
        amount=float(tx_in.amount),
        type=tx_in.type,
        description=tx_in.description,
        date=tx_in.date,
        created_at=datetime.utcnow()
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

def get_transaction(db: Session, tx_id):
    return db.query(Transaction).filter(Transaction.transaction_id == tx_id).first()

def list_transactions(db: Session, user_id, skip=0, limit=25, **filters):
    q = db.query(Transaction).filter(Transaction.user_id == user_id)
    # apply filters (dates, category)
    if filters.get("start_date"):
        q = q.filter(Transaction.date >= filters["start_date"])
    if filters.get("end_date"):
        q = q.filter(Transaction.date <= filters["end_date"])
    if filters.get("category_id"):
        q = q.filter(Transaction.category_id == filters["category_id"])
    return q.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()
