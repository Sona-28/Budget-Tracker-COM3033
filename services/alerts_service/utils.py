from email_sender import send_email

def send_monthly_summary(user_email, name, month, total_spent, top_category, budget_status):
    subject = f"Your Monthly Spending Summary – {month}"
    body = (
        f"Hello {name},\n\n"
        f"Here is your spending summary for {month}:\n\n"
        f"• Total Spent: {total_spent}\n"
        f"• Top Category: {top_category}\n"
        f"• Budget Status: {budget_status}\n\n"
        f"Keep tracking your expenses to stay on top of your finances.\n\n"
        f"– WALL-ET Team"
    )
    return send_email(user_email, subject, body)
