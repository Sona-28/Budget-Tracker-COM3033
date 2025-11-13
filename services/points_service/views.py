from flask import Blueprint, jsonify, request

points_api = Blueprint('points_api', __name__)


@points_api.get("/health")
def health():
    return jsonify(service="points", status="ok")


@points_api.get("/points/<user_id>")
def get_points(user_id):
    return jsonify(points=0, badge=None)


@points_api.post("/points/monthly-run")
def monthly_run():
    # cron-like trigger later; for now just a stub
    return jsonify(message="monthly points calc stub")
