import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL")
NOTIFY_EMAIL_PASSWORD = os.getenv("NOTIFY_EMAIL_PASSWORD")

def send_email(recipient: str, subject: str, body: str):
    """
    Sends email via SMTP.
    """
    msg = MIMEMultipart()
    msg["From"] = NOTIFY_EMAIL
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(NOTIFY_EMAIL, NOTIFY_EMAIL_PASSWORD)
        server.sendmail(NOTIFY_EMAIL, recipient, msg.as_string())
