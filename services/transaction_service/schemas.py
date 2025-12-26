# services/transaction_service/app/schemas.py
from pydantic import BaseModel
from datetime import date

class TransactionBase(BaseModel):
    title: str
    amount: float
    category: str
    description: str
    date: date
    type: str  # 'expense' or 'income'

class TransactionCreate(TransactionBase):
    user_id: int  # required for frontend/auth integration

class TransactionResponse(TransactionBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
