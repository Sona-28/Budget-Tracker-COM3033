# services/transaction_service/api/v1/analytics.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import requests
import os

from services.transaction_service.database.connection import get_db
from services.transaction_service.dependencies.auth import get_current_user
from services.transaction_service.models.transaction import Transaction, TransactionType

router = APIRouter(
    prefix="/transactions/analytics",
    tags=["Analytics"],
)

CATEGORY_SERVICE_URL = os.getenv(
    "CATEGORY_SERVICE_URL",
    "http://localhost:5003"
)

# -------------------- Helper: fetch category mapping --------------------
def fetch_category_map(user_id: int):
    """Return dict {category_id: category_name}"""
    try:
        resp = requests.get(f"{CATEGORY_SERVICE_URL}/category", params={"user_id": user_id}, timeout=5)
        resp.raise_for_status()
        categories = resp.json()
        return {c["id"]: c["name"] for c in categories}
    except Exception:
        return {}  # fallback: unknown categories


# -------------------------------------------------
# Expenses by Category
# -------------------------------------------------
@router.get("/by-category")
def transactions_by_category(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    category_map = fetch_category_map(user_id)

    results = (
        db.query(
            Transaction.category_id,
            func.sum(Transaction.amount).label("total"),
        )
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.expense,
        )
        .group_by(Transaction.category_id)
        .all()
    )

    return [
        {
            "category": category_map.get(cat_id, "Uncategorised"),
            "total": float(total),
        }
        for cat_id, total in results
    ]


# -------------------------------------------------
# Raw Export
# -------------------------------------------------
@router.get("/export")
def export_transactions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    category_map = fetch_category_map(user_id)

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
            "category": category_map.get(tx.category_id, "Uncategorised"),
            "type": tx.type.value,
            "date": tx.date.isoformat(),
            "description": tx.description,
        }
        for tx in transactions
    ]


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

    return {
        "total_income": float(income),
        "total_expense": float(expense),
        "net_balance": float(income - expense),
    }


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
        {
            "month": month,
            "total": float(total),
        }
        for month, total in results
    ]
