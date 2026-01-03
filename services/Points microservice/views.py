from flask import Blueprint, request, jsonify
from models import PointsAccount, RewardLog
from extensions import db

points_api = Blueprint("points_api", __name__)


@points_api.get("/health")
def health():
    return jsonify(service="points", status="ok")

POINTS_PER_CURRENCY = 2.0
PENALTY_PER_OVER = 1.5

# POINTS EVALUATION 

@points_api.post("/points/evaluate")
def evaluate_points():
    data = request.json or {}

    # 🔹 user_id MUST come from web_app
    user_id = data.get("user_id")
    budget = data.get("budget")
    spent = data.get("spent")

    if not all([user_id, budget, spent]):
        return jsonify({"error": "user_id, budget and spent are required"}), 400

    # find or create points account
    account = PointsAccount.query.filter_by(user_id=user_id).first()
    if not account:
        account = PointsAccount(user_id=user_id, total_points=0)
        db.session.add(account)

    delta = budget - spent

    if delta >= 0:
        points = int(delta * 2)
        reason = f"Under budget by £{delta}"
    else:
        points = int(delta)   # negative points
        reason = f"Overspent by £{abs(delta)}"

    account.total_points += points

    log = RewardLog(
        user_id=user_id,
        points=points,
        reason=reason
    )

    db.session.add(log)
    db.session.commit()

    return jsonify({
        "user_id": user_id,
        "awarded_points": points,
        "total_points": account.total_points,
        "reason": reason
    })


# POINTS SUMMERY 

@points_api.get("/points/summary")
def points_summary():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    account = PointsAccount.query.filter_by(user_id=user_id).first()

    if not account:
        return jsonify({"user_id": user_id, "total_points": 0})

    logs = RewardLog.query.filter_by(user_id=user_id).order_by(
        RewardLog.created_at.desc()
    ).limit(10)

    return jsonify({
        "user_id": user_id,
        "total_points": account.total_points,
        "logs": [
            {"points": l.points, "reason": l.reason, "date": l.created_at.isoformat()}
            for l in logs
        ]
    })
