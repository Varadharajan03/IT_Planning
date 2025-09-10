from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
import re
import os

GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH", "token.json")
GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")

import base64
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service():
    creds = None
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
    service = build("gmail", "v1", credentials=creds)
    return service

def check_leave_mail():
    service = get_gmail_service()
    results = service.users().messages().list(userId="me", q="subject:Leave").execute()
    messages = results.get("messages", [])

    if not messages:
        return None

    # Take latest leave mail
    msg = service.users().messages().get(userId="me", id=messages[0]["id"]).execute()
    payload = msg["payload"]
    headers = payload["headers"]

    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
    sender = next((h["value"] for h in headers if h["name"] == "From"), "")

    # Get body
    body = ""
    if "data" in payload["body"]:
        body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")

    # Try to extract email mentioned in mail body
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", body)
    leave_email = match.group(0) if match else sender

    return leave_email
