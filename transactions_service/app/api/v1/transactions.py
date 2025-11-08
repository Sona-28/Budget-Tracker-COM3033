from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Router Setup ---
router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

# --- JWT Authentication Stub ---
def get_current_user():
    """
    Placeholder JWT dependency.
    Replace with actual JWT validation later.
    """
    # Example: decode and validate JWT here
    # raise HTTPException if invalid
    return {"user_id": 1, "username": "test_user"}  # Mocked user data

# --- Pydantic Schemas ---
class TransactionBase(BaseModel):
    title: str
    amount: float
    category: Optional[str] = None
    date: datetime
    type: str  # 'income' or 'expense'

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    date: Optional[datetime] = None
    type: Optional[str] = None

class Transaction(TransactionBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

# --- CRUD Endpoints ---

@router.post("/", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionCreate,
    current_user: dict = Depends(get_current_user)
):
    return {
        "id": 1,
        "user_id": current_user["user_id"],
        **transaction.dict()
    }

@router.get("/", response_model=List[Transaction])
def get_transactions(current_user: dict = Depends(get_current_user)):
    return [
        {
            "id": 1,
            "title": "Groceries",
            "amount": 50.0,
            "category": "Food",
            "date": datetime.now(),
            "type": "expense",
            "user_id": current_user["user_id"]
        }
    ]

@router.get("/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: int, current_user: dict = Depends(get_current_user)):
    if transaction_id != 1:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return {
        "id": transaction_id,
        "title": "Sample Transaction",
        "amount": 20.5,
        "category": "Transport",
        "date": datetime.now(),
        "type": "expense",
        "user_id": current_user["user_id"]
    }

@router.put("/{transaction_id}", response_model=Transaction)
def update_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    current_user: dict = Depends(get_current_user)
):
    updated_data = transaction.dict(exclude_unset=True)
    return {
        "id": transaction_id,
        "user_id": current_user["user_id"],
        "title": updated_data.get("title", "Updated Transaction"),
        "amount": updated_data.get("amount", 100.0),
        "category": updated_data.get("category", "Misc"),
        "date": updated_data.get("date", datetime.now()),
        "type": updated_data.get("type", "expense")
    }

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, current_user: dict = Depends(get_current_user)):
    if transaction_id != 1:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"detail": f"Transaction {transaction_id} deleted successfully"}
