#!/usr/bin/env python3
from datetime import datetime

from services.alerts_service.utils import send_monthly_summary

# TODO: Fetch summaries from database or analytics service
summaries = []  # List of dicts: {"email": "", "name": "", "total_spent": 0, "top_category": "", "budget_status": ""}

def monthly_summary_cron():
    month = datetime.now().strftime("%B %Y")

    for summary in summaries:
        success = send_monthly_summary(
            user_email=summary["email"],
            name=summary["name"],
            month=month,
            total_spent=summary["total_spent"],
            top_category=summary["top_category"],
            budget_status=summary["budget_status"]
        )
        if success:
            print(f"Email sent to {summary['email']}")
        else:
            print(f"Failed to send email to {summary['email']}")

if __name__ == "__main__":
    monthly_summary_cron()
