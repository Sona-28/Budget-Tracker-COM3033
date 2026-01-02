from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
import enum

from services.transaction_service.database.connection import Base


class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    # Comes from Auth Service
    user_id = Column(Integer, index=True, nullable=False)

    title = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)

    category_id = Column(Integer, nullable=False)

    description = Column(String(255), nullable=True)

    date = Column(DateTime, nullable=False)

    type = Column(Enum(TransactionType), nullable=False)

    created_at = Column(DateTime, server_default=func.now())
