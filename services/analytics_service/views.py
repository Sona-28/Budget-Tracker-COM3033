from flask import Blueprint, jsonify, request

analytics_api = Blueprint('analytics_api', __name__)


@analytics_api.get("/health")
def health():
    return jsonify(service="analytics", status="ok")


@analytics_api.get("/analytics/overview")
def analytics_overview():
    return jsonify(
        per_category=[],  # for bar/line
        overall=[],  # for pie
        income_vs_expense=[],  # optional
        totals={"savings": 0}
    )
