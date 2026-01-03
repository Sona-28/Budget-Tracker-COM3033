import os
import requests
import concurrent.futures
from flask import Blueprint, jsonify, request

analytics_api = Blueprint("analytics_api", __name__)

TRANSACTION_SERVICE_URL = (
    os.getenv("TRANSACTION_SERVICE_URL") or "http://localhost:5002"
).rstrip("/")


def _default_summary():
    return {
        "total_income": 0,
        "total_expense": 0,
        "net_balance": 0,
        "transaction_count": 0,
    }


def _fetch_json(path, headers, default, timeout_seconds):
    url = f"{TRANSACTION_SERVICE_URL}{path}"
    try:
        resp = requests.get(url, headers=headers, timeout=timeout_seconds)
    except requests.RequestException:
        return default, f"Request failed for {path}"

    if resp.status_code != 200:
        return default, f"Request failed for {path}: {resp.status_code}"

    try:
        return resp.json(), None
    except ValueError:
        return default, f"Invalid JSON from {path}"


@analytics_api.get("/health")
def health():
    return jsonify(service="analytics", status="ok")


@analytics_api.get("/analytics/overview")
def analytics_overview():
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        return jsonify(error="Missing X-User-Id"), 401

    headers = {"X-User-Id": user_id}
    errors = []
    timeout_seconds = float(os.getenv("ANALYTICS_REQUEST_TIMEOUT", "4"))

    summary = _default_summary()
    per_category = []
    by_month = []
    transactions = []

    endpoints = {
        "summary": (
            "/api/v1/transactions/analytics/summary",
            _default_summary(),
        ),
        "per_category": (
            "/api/v1/transactions/analytics/by-category",
            [],
        ),
        "by_month": (
            "/api/v1/transactions/analytics/by-month",
            [],
        ),
        "transactions": (
            "/api/v1/transactions/analytics/export",
            [],
        ),
    }

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(endpoints)
    ) as executor:
        future_map = {
            executor.submit(
                _fetch_json, path, headers, default, timeout_seconds
            ): key
            for key, (path, default) in endpoints.items()
        }
        for future in concurrent.futures.as_completed(future_map):
            key = future_map[future]
            data, err = future.result()
            if err:
                errors.append(err)
            if key == "summary":
                summary = data
            elif key == "per_category":
                per_category = data
            elif key == "by_month":
                by_month = data
            elif key == "transactions":
                transactions = data

    if not isinstance(per_category, list):
        per_category = []

    if not isinstance(by_month, list):
        by_month = []

    if not isinstance(transactions, list):
        transactions = []

    normalized_transactions = []
    for tx in transactions:
        category = tx.get("category") or "Uncategorised"
        normalized_transactions.append(
            {
                **tx,
                "category": category,
            }
        )

    total_income = summary.get("total_income", 0)
    total_expense = summary.get("total_expense", 0)
    net_balance = summary.get("net_balance", 0)
    transaction_count = summary.get("transaction_count", 0)

    return jsonify(
        per_category=per_category,
        overall=per_category,
        income_vs_expense={
            "income": total_income,
            "expense": total_expense,
        },
        totals={
            "savings": net_balance,
            "total_income": total_income,
            "total_expense": total_expense,
            "transaction_count": transaction_count,
        },
        summary=summary,
        transactions=normalized_transactions,
        by_month=by_month,
        errors=errors,
    )
