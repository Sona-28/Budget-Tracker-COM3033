import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

values = dotenv_values()

SMTP_SERVER = values.get("SMTP_SERVER", "smtp.example.com")
SMTP_PORT = int(values.get("SMTP_PORT", 587))
SMTP_USERNAME = values.get("SMTP_USERNAME")
SMTP_PASSWORD = values.get("SMTP_PASSWORD")



def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = SMTP_USERNAME
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Email error:", e)
        return False

