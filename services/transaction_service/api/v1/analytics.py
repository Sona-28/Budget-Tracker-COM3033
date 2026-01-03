# services/transaction_service/api/v1/analytics.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from services.transaction_service.database.connection import get_db
from services.transaction_service.dependencies.auth import get_current_user
from services.transaction_service.models.transaction import (
    Transaction,
    TransactionType,
)

router = APIRouter(
    prefix="/transactions/analytics",
    tags=["Analytics"],
)

# -------------------------------------------------
# Summary
# -------------------------------------------------
@router.get("/summary")
def transaction_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    income = (
        db.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.income,
        )
        .scalar()
        or 0
    )

    expense = (
        db.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.expense,
        )
        .scalar()
        or 0
    )

    count = (
        db.query(func.count(Transaction.id))
        .filter(Transaction.user_id == user_id)
        .scalar()
    )

    return {
        "total_income": float(income),
        "total_expense": float(expense),
        "net_balance": float(income - expense),
        "transaction_count": count,
    }


# -------------------------------------------------
# Expenses by Category
# -------------------------------------------------
@router.get("/by-category")
def transactions_by_category(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    results = (
        db.query(
            Transaction.category,
            func.sum(Transaction.amount).label("total"),
        )
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.expense,
        )
        .group_by(Transaction.category)
        .all()
    )

    return [
        {
            "category": category or "Uncategorised",
            "total": float(total),
        }
        for category, total in results
    ]


# -------------------------------------------------
# Expenses by Month (MySQL compatible)
# -------------------------------------------------
@router.get("/by-month")
def transactions_by_month(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    results = (
        db.query(
            func.date_format(Transaction.date, "%Y-%m").label("month"),
            func.sum(Transaction.amount).label("total"),
        )
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.expense,
        )
        .group_by("month")
        .order_by("month")
        .all()
    )

    return [
        {"month": month, "total": float(total)}
        for month, total in results
    ]


# -------------------------------------------------
# Raw Export (for Analytics / Rewards services)
# -------------------------------------------------
@router.get("/export")
def export_transactions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.date.desc())
        .all()
    )

    return [
        {
            "id": tx.id,
            "title": tx.title,
            "amount": float(tx.amount),
            "category": tx.category,
            "type": tx.type.value,  # enum → string
            "date": tx.date.isoformat(),
            "description": tx.description,
        }
        for tx in transactions
    ]
