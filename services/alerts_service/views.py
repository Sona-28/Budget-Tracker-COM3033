import requests
from flask import Blueprint, jsonify, request
from email_sender import send_email  
import os
from dotenv import load_dotenv

load_dotenv()

alerts_api = Blueprint('alerts_api', __name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5001")

@alerts_api.get("/health")
def health():
    return jsonify(service="alerts", status="ok")


@alerts_api.post("/alerts/overspend")
def overspend():
    data = request.json
    user_id = data.get("user_id")
    category = data.get("category")
    amount = data.get("amount")
    budget = data.get("budget")

    try:
        resp = requests.get(f"{AUTH_SERVICE_URL}/users/{user_id}", timeout=5)
        resp.raise_for_status()
        user = resp.json()
    except requests.RequestException:
        return jsonify(message="Could not fetch user info"), 500
    receive_email = user.get("receive_email")
    if not receive_email:
        return jsonify(message="User has opted out of email notifications"), 200
    user_email = user.get("email")
    name = user.get("firstname") + " " + user.get("lastname")

    if not user_email:
        return jsonify(message="Missing user_email"), 400

    subject = f"Overspend Alert: {category}"
    body = f"Dear {name}, you have spent {amount} on {category}, exceeding your threshold of {budget}."

    success = send_email(user_email, subject, body)
    if success:
        return jsonify(message="Overspend alert sent successfully")
    else:
        return jsonify(message="Failed to send email"), 500


@alerts_api.post("/alerts/reward")
def reward():
    data = request.json
    user_id = data.get("user_id")
    reward_type = data.get("points")

    try:
        resp = requests.get(f"{AUTH_SERVICE_URL}/users/{user_id}", timeout=5)
        resp.raise_for_status()
        user = resp.json()
    except requests.RequestException:
        return jsonify(message="Could not fetch user info"), 500
    receive_email = user.get("receive_email")
    if not receive_email:
        return jsonify(message="User has opted out of email notifications"), 200
    user_email = user.get("email")
    name = user.get("firstname") + " " + user.get("lastname")
    if not user_email or not reward_type:
        return jsonify(message="Missing user_email or reward_type"), 400

    subject = "You've earned a reward!"
    body = f"Congratulations! {name}, you have earned: {reward_type}"

    success = send_email(user_email, subject, body)
    if success:
        return jsonify(message="Reward email sent successfully")
    else:
        return jsonify(message="Failed to send email"), 500


