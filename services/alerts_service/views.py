import requests
from flask import Blueprint, jsonify, request
from email_sender import send_email  
import os
from dotenv import load_dotenv

load_dotenv()

alerts_api = Blueprint('alerts_api', __name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5001")
TRANSACTION_SERVICE_URL = os.getenv("TRANSACTION_SERVICE_URL", "http://localhost:5002")
CATEGORY_SERVICE_URL = os.getenv("CATEGORY_SERVICE_URL", "http://localhost:5003")

@alerts_api.get("/health")
def health():
    return jsonify(service="alerts", status="ok")


@alerts_api.post("/alerts/overspend")
def overspend():
    user_id = request.headers.get("X-User-Id")
    category_id = request.json.get("category_id")
    date = request.json.get("date")
    if not user_id or not category_id or not date:
        return jsonify(error="Missing required parameters"), 400
    #Fetch category details
    try:
        resp = requests.get(
            f"{CATEGORY_SERVICE_URL}/category/{category_id}",
            params={"user_id": user_id},
            timeout=5
        )
        resp.raise_for_status()
        category_data = resp.json()
        budget_amount = category_data.get("budget_amount")
        if budget_amount is None:
            return jsonify(message="No budget set for this category"), 200
        else:
            category_name = category_data.get("name")
    except requests.RequestException:
        return jsonify(error="Failed to fetch category details"), 503
    #Fetch total spent in category
    try:
        resp = requests.get(
            f"{TRANSACTION_SERVICE_URL}/api/v1/transactions/analytics/by-category",
            headers={"X-User-Id": user_id},
            timeout=5
        )
        resp.raise_for_status()
        by_category = resp.json()
        for record in by_category:
            if record["category"] == category_name:
                total_spent = record["total"]
                break
        else:
            total_spent = 0
    except requests.RequestException:
        return jsonify(error="Failed to connect to transaction service"), 503
    #Check overspend
    if total_spent > budget_amount:
        #Fetch user email
        try:
            resp = requests.get(
                f"{AUTH_SERVICE_URL}/users/{user_id}",
                timeout=5
            )
            resp.raise_for_status()
            user_data = resp.json()
            user_email = user_data.get("email")
            user_name = user_data.get("firstname") + " " + user_data.get("lastname")
            if not user_email:
                return jsonify(error="User email not found"), 404
        except requests.RequestException:
            return jsonify(error="Failed to fetch user details"), 503
        #Send email alert
        subject = f"Overspend Alert: {category_name} Budget Exceeded"
        body = (
            f"Dear {user_name},\n\n"
            f"You have exceeded your budget for the category '{category_name}'.\n"
            f"Budget Amount: {budget_amount}\n"
            f"Total Spent: {total_spent}\n\n"
            f"Please review your expenses.\n\n"
            f"Best regards,\n"
            f"WALL-ET Team"
        )
        send_email(user_email, subject, body)
        return jsonify(message="Overspend alert sent"), 200
    return jsonify(message="No overspend detected"), 200
    