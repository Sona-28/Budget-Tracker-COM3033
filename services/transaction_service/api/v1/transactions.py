from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import requests
import os

from services.transaction_service.dependencies.auth import get_current_user
from services.transaction_service.database.connection import get_db
from services.transaction_service.models.transaction import (
    Transaction as TransactionModel,
    TransactionType
)

router = APIRouter(
    prefix="",
    tags=["Transactions"]
)

CATEGORY_SERVICE_URL = os.getenv(
    "CATEGORY_SERVICE_URL",
    "http://localhost:5003"  # fallback
)

# ---------- Schemas ----------

class TransactionBase(BaseModel):
    title: str
    amount: float
    category_id: Optional[int] = None
    description: Optional[str] = None
    date: datetime
    type: TransactionType

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    type: Optional[TransactionType] = None

class TransactionRead(TransactionBase):
    id: int
    user_id: int
    category: Optional[dict] = None  # {"id": 1, "name": "Food"}
    model_config = ConfigDict(from_attributes=True)

# ---------- Helper: fetch categories ----------

def fetch_categories(user_id: int):
    try:
        resp = requests.get(f"{CATEGORY_SERVICE_URL}/category", params={"user_id": user_id}, timeout=5)
        resp.raise_for_status()
        return {c["id"]: c["name"] for c in resp.json()}
    except requests.RequestException:
        return {}

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
        category_id=transaction.category_id,
        description=transaction.description,
        date=transaction.date,
        type=transaction.type
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
    user_id = current_user["user_id"]
    transactions = (
        db.query(TransactionModel)
        .filter(TransactionModel.user_id == user_id)
        .all()
    )

    categories = fetch_categories(user_id)

    result = []
    for tx in transactions:
        tx_dict = TransactionRead.from_orm(tx).model_dump()
        tx_dict["category"] = {"id": tx.category_id, "name": categories.get(tx.category_id, "Uncategorised")} if tx.category_id else None
        result.append(tx_dict)

    return result

@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    tx = db.query(TransactionModel).filter(
        TransactionModel.id == transaction_id,
        TransactionModel.user_id == user_id
    ).first()

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    categories = fetch_categories(user_id)
    tx_dict = TransactionRead.from_orm(tx).model_dump()
    tx_dict["category"] = {"id": tx.category_id, "name": categories.get(tx.category_id, "Uncategorised")} if tx.category_id else None

    return tx_dict

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
        setattr(tx, field, value)

    db.commit()
    db.refresh(tx)

    categories = fetch_categories(current_user["user_id"])
    tx_dict = TransactionRead.from_orm(tx).model_dump()
    tx_dict["category"] = {"id": tx.category_id, "name": categories.get(tx.category_id, "Uncategorised")} if tx.category_id else None

    return tx_dict

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
