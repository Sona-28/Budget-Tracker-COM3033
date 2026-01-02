import os
import requests
from flask import Blueprint, render_template, request, redirect, flash, session, url_for
from web_app.routes.utils import require_login

transaction_blueprint = Blueprint(
    "transaction",
    __name__,
    template_folder="../templates"
)

TRANSACTION_SERVICE_URL = os.getenv(
    "TRANSACTION_SERVICE_URL",
    "http://localhost:5002"
)

CATEGORY_SERVICE_URL = os.getenv(
    "CATEGORY_SERVICE_URL",
    "http://localhost:5003"
)


# ---------- Helper: fetch categories ----------
def fetch_categories(user_id):
    resp = requests.get(
        f"{CATEGORY_SERVICE_URL}/category",
        params={"user_id": user_id},
        timeout=5
    )
    resp.raise_for_status()
    return resp.json()


# ---------- Helper: map category_id -> category_name ----------
def attach_category_name(transactions, categories):
    cat_map = {c["id"]: c["name"] for c in categories}
    for tx in transactions:
        cat_id = tx.get("category_id")
        tx["category"] = {"id": cat_id, "name": cat_map.get(cat_id, "Uncategorised")}
    return transactions


# ---------- List + Create Transactions ----------
@transaction_blueprint.route("/transaction", methods=["GET", "POST"])
def transaction():
    guard = require_login()
    if guard:
        return guard

    user_id = session.get("user_id")
    headers = {"X-User-Id": str(user_id)}

    # ---------- POST: Create transaction ----------
    if request.method == "POST":
        payload = {
            "title": request.form["title"],
            "amount": float(request.form["amount"]),
            "category_id": int(request.form["category_id"]),
            "description": request.form.get("description") or None,
            "date": request.form["date"],
            "type": request.form["type"]
        }

        try:
            resp = requests.post(
                f"{TRANSACTION_SERVICE_URL}/api/v1/transactions",
                json=payload,
                headers=headers,
                timeout=5
            )
        except requests.RequestException:
            flash("Transaction service unavailable", "danger")
            return redirect(url_for("transaction.transaction"))

        if resp.status_code == 201:
            flash("Transaction added successfully", "success")
        else:
            flash("Failed to add transaction", "danger")

        return redirect(url_for("transaction.transaction"))

    # ---------- GET: Fetch transactions ----------
    try:
        tx_resp = requests.get(
            f"{TRANSACTION_SERVICE_URL}/api/v1/transactions",
            headers=headers,
            timeout=5
        )
        transactions = tx_resp.json() if tx_resp.status_code == 200 else []
    except requests.RequestException:
        transactions = []

    # ---------- Fetch categories for dropdown ----------
    try:
        categories = fetch_categories(user_id)
    except requests.RequestException:
        categories = []
        flash("Category service unavailable", "warning")

    # ---------- Attach category names ----------
    transactions = attach_category_name(transactions, categories)

    return render_template(
        "transaction/transaction.html",
        transactions=transactions,
        categories=categories
    )


# ---------- Delete transaction ----------
@transaction_blueprint.route("/transaction/<int:transaction_id>/delete", methods=["POST"])
def delete_transaction(transaction_id):
    guard = require_login()
    if guard:
        return guard

    headers = {"X-User-Id": str(session.get("user_id"))}

    try:
        requests.delete(
            f"{TRANSACTION_SERVICE_URL}/api/v1/transactions/{transaction_id}",
            headers=headers,
            timeout=5
        )
        flash("Transaction deleted", "success")
    except requests.RequestException:
        flash("Transaction service unavailable", "danger")

    return redirect(url_for("transaction.transaction"))


# ---------- Edit transaction ----------
@transaction_blueprint.route("/transaction/<int:transaction_id>/edit", methods=["GET", "POST"])
def edit_transaction(transaction_id):
    guard = require_login()
    if guard:
        return guard

    user_id = session.get("user_id")
    headers = {"X-User-Id": str(user_id)}

    # ---------- GET: Load edit form ----------
    if request.method == "GET":
        try:
            tx_resp = requests.get(
                f"{TRANSACTION_SERVICE_URL}/api/v1/transactions/{transaction_id}",
                headers=headers,
                timeout=5
            )
            categories = fetch_categories(user_id)
        except requests.RequestException:
            flash("Service unavailable", "danger")
            return redirect(url_for("transaction.transaction"))

        if tx_resp.status_code != 200:
            flash("Transaction not found", "danger")
            return redirect(url_for("transaction.transaction"))

        tx = tx_resp.json()
        # attach category object
        tx["category"] = next((c for c in categories if c["id"] == tx.get("category_id")), {"id": None, "name": "Uncategorised"})

        return render_template(
            "transaction/edit.html",
            tx=tx,
            categories=categories
        )

    # ---------- POST: Update transaction ----------
    payload = {
        "title": request.form["title"],
        "amount": float(request.form["amount"]),
        "category_id": int(request.form["category_id"]),
        "description": request.form.get("description"),
        "date": request.form["date"],
        "type": request.form["type"]
    }

    try:
        resp = requests.put(
            f"{TRANSACTION_SERVICE_URL}/api/v1/transactions/{transaction_id}",
            json=payload,
            headers=headers,
            timeout=5
        )
    except requests.RequestException:
        flash("Transaction service unavailable", "danger")
        return redirect(url_for("transaction.transaction"))

    if resp.status_code == 200:
        flash("Transaction updated", "success")
    else:
        flash("Failed to update transaction", "danger")

    return redirect(url_for("transaction.transaction"))
