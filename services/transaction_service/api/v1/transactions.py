from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from services.transaction_service.dependencies.auth import get_current_user
from services.transaction_service.database.connection import get_db
from services.transaction_service.models.transaction import (
    Transaction as TransactionModel,
    TransactionType)


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

# ---------- Schemas ----------

class TransactionBase(BaseModel):
    title: str
    amount: float
    category: Optional[str] = None
    description: Optional[str] = None
    date: datetime
    type: str  # income | expense


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    type: Optional[str] = None


class TransactionRead(TransactionBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)

# ---------- Endpoints ----------

@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_tx = TransactionModel(
        user_id=current_user["user_id"],
        title=transaction.title,
        amount=transaction.amount,
        category=transaction.category,
        description=transaction.description,
        date=transaction.date,
        type=TransactionType(transaction.type),
    )

    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx


@router.get("", response_model=List[TransactionRead])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return (
        db.query(TransactionModel)
        .filter(TransactionModel.user_id == current_user["user_id"])
        .all()
    )


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    tx = db.query(TransactionModel).filter(
        TransactionModel.id == transaction_id,
        TransactionModel.user_id == current_user["user_id"]
    ).first()

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return tx


@router.put("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    tx = db.query(TransactionModel).filter(
        TransactionModel.id == transaction_id,
        TransactionModel.user_id == current_user["user_id"]
    ).first()

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    for field, value in transaction.model_dump(exclude_unset=True).items():
        if field == "type":
            value = TransactionType(value)
        setattr(tx, field, value)

    db.commit()
    db.refresh(tx)
    return tx


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    tx = db.query(TransactionModel).filter(
        TransactionModel.id == transaction_id,
        TransactionModel.user_id == current_user["user_id"]
    ).first()

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(tx)
    db.commit()


@router.get("/health", tags=["Health"])
def health():
    return {
        "service": "transactions",
        "version": "v1",
        "status": "ok"
    }
