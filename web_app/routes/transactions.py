import os
import requests
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    session,
    url_for
)
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


def _auth_headers():
    """Internal helper to build auth headers"""
    return {
        "X-User-Id": str(session.get("user_id"))
    }


@transaction_blueprint.route("/transaction", methods=["GET", "POST"])
def transaction():
    guard = require_login()
    if guard:
        return guard

    headers = _auth_headers()

    # ---------- POST: Create transaction ----------
    if request.method == "POST":
        payload = {
            "title": request.form["title"],
            "amount": float(request.form["amount"]),
            "category": request.form.get("category") or None,
            "description": request.form.get("description") or None,
            "date": request.form["date"],
            "type": request.form["type"],
        }

        try:
            resp = requests.post(
                f"{TRANSACTION_SERVICE_URL}/api/v1/transactions",
                json=payload,
                headers=headers,
                timeout=5,
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
        resp = requests.get(
            f"{TRANSACTION_SERVICE_URL}/api/v1/transactions",
            headers=headers,
            timeout=5,
        )
        transactions = resp.json() if resp.status_code == 200 else []
    except requests.RequestException:
        transactions = []

    return render_template(
        "transaction/transaction.html",
        transactions=transactions,
    )


@transaction_blueprint.route(
    "/transaction/<int:transaction_id>/delete",
    methods=["POST"]
)
def delete_transaction(transaction_id):
    guard = require_login()
    if guard:
        return guard

    try:
        requests.delete(
            f"{TRANSACTION_SERVICE_URL}/api/v1/transactions/{transaction_id}",
            headers=_auth_headers(),
            timeout=5,
        )
        flash("Transaction deleted", "success")
    except requests.RequestException:
        flash("Transaction service unavailable", "danger")

    return redirect(url_for("transaction.transaction"))


@transaction_blueprint.route(
    "/transaction/<int:transaction_id>/edit",
    methods=["GET", "POST"]
)
def edit_transaction(transaction_id):
    guard = require_login()
    if guard:
        return guard

    headers = _auth_headers()

    # ---------- GET: Fetch transaction ----------
    if request.method == "GET":
        resp = requests.get(
            f"{TRANSACTION_SERVICE_URL}/api/v1/transactions/{transaction_id}",
            headers=headers,
            timeout=5,
        )

        if resp.status_code != 200:
            flash("Transaction not found", "danger")
            return redirect(url_for("transaction.transaction"))

        return render_template(
            "transaction/edit.html",
            tx=resp.json(),
        )

    # ---------- POST: Update transaction ----------
    payload = {
        "title": request.form["title"],
        "amount": float(request.form["amount"]),
        "category": request.form.get("category") or None,
        "description": request.form.get("description") or None,
        "date": request.form["date"],
        "type": request.form["type"],
    }

    try:
        resp = requests.put(
            f"{TRANSACTION_SERVICE_URL}/api/v1/transactions/{transaction_id}",
            json=payload,
            headers=headers,
            timeout=5,
        )
    except requests.RequestException:
        flash("Transaction service unavailable", "danger")
        return redirect(url_for("transaction.transaction"))

    if resp.status_code == 200:
        flash("Transaction updated", "success")
    else:
        flash("Failed to update transaction", "danger")

    return redirect(url_for("transaction.transaction"))
