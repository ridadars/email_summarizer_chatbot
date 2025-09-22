import os
import pickle
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def main():
    creds = None

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")
    token_path = os.path.join(BASE_DIR, "token.pickle")

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(userId="me", maxResults=5).execute()
    messages = results.get("messages", [])

    if not messages:
        print("No messages found.")
    else:
        print("Recent Messages:")
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()

            headers = msg_data["payload"]["headers"]
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")

            body = ""
            try:
                if "data" in msg_data["payload"]["body"]:
                    body = msg_data["payload"]["body"]["data"]
                elif "parts" in msg_data["payload"]:
                    for part in msg_data["payload"]["parts"]:
                        if part["mimeType"] == "text/plain" and "data" in part["body"]:
                            body = part["body"]["data"]
                            break
                if body:
                    body = base64.urlsafe_b64decode(body).decode("utf-8")
            except Exception as e:
                body = f"(Error decoding body: {e})"

            print(f"\nSubject: {subject}")
            print(f"Body: {body[:200]}...") 

if __name__ == "__main__":
    main()
