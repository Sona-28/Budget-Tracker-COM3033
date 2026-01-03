#!/usr/bin/env python3
from datetime import datetime
import os
import requests
from dotenv import load_dotenv
from app import create_app

load_dotenv()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5001")
TRANSACTION_SERVICE_URL = os.getenv("TRANSACTION_SERVICE_URL", "http://localhost:5002")
POINTS_SERVICE_URL = os.getenv("POINTS_SERVICE_URL", "http://localhost:5004")

def run_cron_job():
    today = datetime.now()
    last_month = today.month - 1 or 12
    last_year = today.year - 1 if today.month == 1 else today.year
    total_income = 0
    total_expense = 0
    try:
        headers = {"X-API-Key": os.getenv("INTERNAL_API_KEY")}
        resp = requests.get(f"{AUTH_SERVICE_URL}/users", headers=headers, timeout=5)
        resp.raise_for_status()
        users = resp.json()
        
        for user in users:
            uid = user["id"]
            user_email = user.get("email") 
            user_name = user.get("firstname") + " " + user.get("lastname")
            headers_tx = {"X-User-Id": str(uid)}
            tx_resp = requests.get(f"{TRANSACTION_SERVICE_URL}/api/v1/transactions/analytics/export", headers=headers_tx, timeout=5)
            if tx_resp.status_code == 200:
                transactions = tx_resp.json()
                category_totals = {}
                for record in transactions:
                    tx_date = datetime.fromisoformat(record["date"])
                    if tx_date.year == last_year and tx_date.month == last_month:
                        if record["type"] == "income":
                            total_income += record["amount"]
                        elif record["type"] == "expense":
                            total_expense += record["amount"]
                            category_name = record["category"]
                            category_totals[category_name] = category_totals.get(category_name, 0) + record["amount"]
                
                # Find top category
                if category_totals:
                    top_category = max(category_totals, key=category_totals.get)
                else:
                    top_category = None
                
                # Fetch user points
                points_resp = requests.get(f"{POINTS_SERVICE_URL}/points/{uid}", timeout=5)
                if points_resp.status_code == 200:
                    points_data = points_resp.json()
                    user_points = points_data.get("total_points", 0)
                else:
                    user_points = 0
                # Send alert email
                if user_email:
                    subject = f"Monthly Summary Email for {last_month}/{last_year}"
                    body = f"""
Dear {user_name},

Here is your monthly summary for {last_month}/{last_year}:

Total Income: ${total_income:.2f}
Total Expenses: ${total_expense:.2f}
Top Spending Category: {top_category or 'None'}
Current Points: {user_points}

Keep up the good work!

Best,
WALL-ET Team
"""
                    from email_sender import send_email
                    send_email(user_email, subject, body)

    except Exception as e:
        print("Error in cron job:", str(e))

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        run_cron_job()

    