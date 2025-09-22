import os
import base64
import pickle
from email import message_from_bytes
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_llm():
    model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")
    temperature = float(os.getenv("TEMPERATURE", 0.2))
    return ChatGoogleGenerativeAI(model=model_name, temperature=temperature)

def get_gmail_service():
    creds = None
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")
    TOKEN_PATH = os.path.join(BASE_DIR, "token.pickle")

    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)

def get_email_content(service, msg_id):
    msg = service.users().messages().get(userId="me", id=msg_id, format="raw").execute()
    raw_msg = base64.urlsafe_b64decode(msg["raw"].encode("ASCII"))
    mime_msg = message_from_bytes(raw_msg)

    subject = mime_msg["subject"]
    body = ""
    if mime_msg.is_multipart():
        for part in mime_msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(errors="ignore")
                break
    else:
        body = mime_msg.get_payload(decode=True).decode(errors="ignore")

    return subject, body

def analyze_with_gemini(llm, subject, body):
    prompt = f"""
Summarize the following email in 2-3 sentences.
Also classify:
- Category: [Work, Security, Promotion, Personal, Other]
- Priority: [Urgent, Normal, Low]

Email:
Subject: {subject}
Body: {body}
"""
    response = llm.invoke(prompt)
    return response.content.strip()

def main():
    service = get_gmail_service()
    llm = get_llm()

    results = service.users().messages().list(userId="me", maxResults=5).execute()
    messages = results.get("messages", [])

    summaries = []

    print("📬 Raw Emails + Gemini Analysis:\n")
    for msg in messages:
        subject, body = get_email_content(service, msg["id"])
        analysis = analyze_with_gemini(llm, subject, body)

        email_summary = f"""
---
📩 Subject: {subject}
🔎 Analysis: {analysis}
"""
        summaries.append(analysis)
        print(email_summary)

    digest_prompt = f"""
Here are multiple email analyses. Create a short daily digest summary highlighting:
- Count per category (Work, Security, Promotion, Personal, Other)
- How many urgent items
- 2-line executive summary

Emails:
{summaries}
"""
    digest = llm.invoke(digest_prompt)
    print("\n📊 Daily Digest Report:\n")
    print(digest.content.strip())

if __name__ == "__main__":
    main()
