from flask import Blueprint, jsonify, request

alerts_api = Blueprint('alerts_api', __name__)


@alerts_api.get("/health")
def health():
    return jsonify(service="alerts", status="ok")


@alerts_api.post("/alerts/overspend")
def overspend():
    # expected JSON: user_email, category, amount, threshold
    return jsonify(message="overspend alert stub")


@alerts_api.post("/alerts/reward")
def reward():
    # expected JSON: user_email, badge|points
    return jsonify(message="reward alert stub")
