import os
import requests
from flask import Blueprint, render_template, flash, session

from web_app.routes.utils import require_login
analytics_blueprint = Blueprint('analytics', __name__, template_folder='../templates')

ANALYTICS_SERVICE_URL = (
    os.getenv("ANALYTICS_SERVICE_URL") or "http://localhost:5004"
).rstrip("/")
CATEGORY_SERVICE_URL = (
    os.getenv("CATEGORY_SERVICE_URL") or "http://localhost:5003"
).rstrip("/")


def _default_analytics_data():
    return {
        "per_category": [],
        "overall": [],
        "income_vs_expense": {"income": 0, "expense": 0},
        "totals": {
            "savings": 0,
            "total_income": 0,
            "total_expense": 0,
            "transaction_count": 0,
        },
        "summary": {
            "total_income": 0,
            "total_expense": 0,
            "net_balance": 0,
            "transaction_count": 0,
        },
        "transactions": [],
        "by_month": [],
        "budgets": [],
        "errors": [],
    }


@analytics_blueprint.route('/analytics')
def analytics():
    guard = require_login()
    if guard:
        return guard

    analytics_data = _default_analytics_data()
    user_id = session.get("user_id")
    headers = {
        "X-User-Id": str(user_id)
    }

    try:
        resp = requests.get(
            f"{ANALYTICS_SERVICE_URL}/analytics/overview",
            headers=headers,
            timeout=8
        )
        if resp.status_code == 200:
            analytics_data = resp.json()
        else:
            flash(
                f"Analytics service unavailable ({resp.status_code}).",
                "danger",
            )
    except requests.RequestException as exc:
        flash(
            (
                "Analytics service unavailable "
                f"({ANALYTICS_SERVICE_URL}): {exc}"
            ),
            "danger",
        )

    errors = analytics_data.get("errors") or []
    if errors:
        flash("Analytics data is incomplete.", "warning")

    analytics_data.setdefault("budgets", [])
    try:
        resp = requests.get(
            f"{CATEGORY_SERVICE_URL}/category",
            params={"user_id": user_id},
            timeout=5
        )
        if resp.status_code == 200:
            categories = resp.json()
            analytics_data["budgets"] = [
                {
                    "name": (cat.get("name") or "Uncategorised"),
                    "budget_amount": cat.get("budget_amount")
                }
                for cat in categories
            ]
    except requests.RequestException:
        pass

    return render_template(
        "analytics/analytics.html",
        analytics_data=analytics_data
    )

