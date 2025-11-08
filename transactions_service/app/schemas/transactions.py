# app/schemas/transaction.py
from pydantic import BaseModel, Field, condecimal
from typing import Optional
from uuid import UUID
from datetime import date, datetime

class TransactionBase(BaseModel):
    category_id: Optional[UUID] = None
    amount: condecimal(max_digits=12, decimal_places=2)
    type: str = Field(..., regex="^(income|expense)$")
    description: Optional[str] = None
    date: date

class TransactionCreate(TransactionBase):
    # user_id should be inferred from JWT; include optional client_id for idempotency
    client_id: Optional[str] = None

class TransactionUpdate(BaseModel):
    category_id: Optional[UUID] = None
    amount: Optional[condecimal(max_digits=12, decimal_places=2)] = None
    description: Optional[str] = None
    date: Optional[date] = None

class TransactionRead(TransactionBase):
    transaction_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
