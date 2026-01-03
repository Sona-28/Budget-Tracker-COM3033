#!/usr/bin/env python3
import os
import requests
from datetime import datetime, timedelta
from app import create_app
from dotenv import load_dotenv
from models import PointsAccount
from extensions import db
from collections import defaultdict

load_dotenv()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5001")
TRANSACTION_SERVICE_URL = os.getenv("TRANSACTION_SERVICE_URL", "http://localhost:5002")
CATEGORY_SERVICE_URL = os.getenv("CATEGORY_SERVICE_URL", "http://localhost:5003")
app = create_app()

with app.app_context():
    try:
        headers = {"X-API-Key": os.getenv("INTERNAL_API_KEY")}
        resp = requests.get(f"{AUTH_SERVICE_URL}/users", headers=headers, timeout=5)
        resp.raise_for_status()
        users = resp.json()
        
        for user in users:
            uid = user["id"]
            
            # Calculate last month dates
            today = datetime.now()
            first_current = today.replace(day=1)
            last_prev = first_current - timedelta(days=1)
            first_prev = last_prev.replace(day=1)
            
            total_points = 0
            # Get all transactions
            headers_tx = {"X-User-Id": str(uid)}
            tx_resp = requests.get(f"{TRANSACTION_SERVICE_URL}/api/v1/transactions/analytics/export", headers=headers_tx, timeout=5)
            if tx_resp.status_code == 200:
                transactions = tx_resp.json()
                
                # Filter for last month and group by category
                category_spent = defaultdict(float)
                for tx in transactions:
                    tx_date = datetime.fromisoformat(tx["date"].replace('Z', '+00:00'))
                    if first_prev <= tx_date <= last_prev and tx["type"] == "expense":
                        category_spent[tx["category"]] += tx["amount"]
                for category_name, spent in category_spent.items():
                    # Get budget for category
                    cat_resp = requests.get(f"{CATEGORY_SERVICE_URL}/category/budget/{category_name}", params={"user_id": uid}, timeout=5)
                    if cat_resp.status_code == 200:
                        category = cat_resp.json()
                        budget = category.get("budget_amount", 0)
                        if budget == None:
                            continue
                        if spent < budget:
                            print("Spent less than budget for category:", category_name)
                            saved = budget - spent
                            points = int(saved // 5)
                            print(f"Awarded {points} points for category {category_name}")
                        else:
                            overspent = spent - budget
                            points = -int(overspent // 10)
                        
                        total_points += points
                        print(f"Total points so far for user {uid}: {total_points}")
            
            # Ensure total_points >= 0
            total_points = max(0, total_points)
            
            # Add points entry if any
            if total_points > 0:
                points_entry = PointsAccount(user_id=uid, points=total_points, reason="Monthly evaluation")
                db.session.add(points_entry)
        db.session.commit()
        print(f"Monthly points evaluation completed for {len(users)} users.")
    except Exception as e:
        print(f"Failed: {str(e)}")

