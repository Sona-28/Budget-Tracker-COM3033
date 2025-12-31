from flask import Blueprint, jsonify, request
from email_sender import send_email  

alerts_api = Blueprint('alerts_api', __name__)


@alerts_api.get("/health")
def health():
    return jsonify(service="alerts", status="ok")


@alerts_api.post("/alerts/overspend")
def overspend():
    data = request.json
    user_email = data.get("user_email")
    category = data.get("category")
    amount = data.get("amount")
    threshold = data.get("threshold")

    if not user_email:
        return jsonify(message="Missing user_email"), 400

    subject = f"Overspend Alert: {category}"
    body = f"Dear user, you have spent {amount} on {category}, exceeding your threshold of {threshold}."

    success = send_email(user_email, subject, body)
    if success:
        return jsonify(message="Overspend alert sent successfully")
    else:
        return jsonify(message="Failed to send email"), 500


@alerts_api.post("/alerts/reward")
def reward():
    data = request.json
    user_email = data.get("user_email")
    reward_type = data.get("badge") or data.get("points")

    if not user_email or not reward_type:
        return jsonify(message="Missing user_email or reward_type"), 400

    subject = "You've earned a reward!"
    body = f"Congratulations! You have earned: {reward_type}"

    success = send_email(user_email, subject, body)
    if success:
        return jsonify(message="Reward email sent successfully")
    else:
        return jsonify(message="Failed to send email"), 500

@alerts_api.post("/alerts/monthly-summary")
def monthly_summary():
    data = request.json

    user_email = data.get("user_email")
    month = data.get("month")
    total_spent = data.get("total_spent")
    top_category = data.get("top_category")
    budget_status = data.get("budget_status")

    if not user_email or not month:
        return jsonify(message="Missing user_email or month"), 400

    subject = f"Your Monthly Spending Summary – {month}"
    body = (
        f"Hello,\n\n"
        f"Here is your spending summary for {month}:\n\n"
        f"• Total Spent: {total_spent}\n"
        f"• Top Category: {top_category}\n"
        f"• Budget Status: {budget_status}\n\n"
        f"Keep tracking your expenses to stay on top of your finances.\n\n"
        f"– WALL-ET Team"
    )

    success = send_email(user_email, subject, body)

    if success:
        return jsonify(message="Monthly summary email sent successfully")
    else:
        return jsonify(message="Failed to send monthly summary email"), 500
