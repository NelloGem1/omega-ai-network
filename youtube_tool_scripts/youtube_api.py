"""Shared YouTube auth: builds an authorized service, caches the token."""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET = os.path.join(BASE_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_FLAG = os.path.join(BASE_DIR, "use_backup.flag")


def use_backup():
    """Switch all future get_service() calls to the second GCP project."""
    with open(BACKUP_FLAG, "w") as f:
        f.write("1")


def _paths():
    if os.path.exists(BACKUP_FLAG):
        return (os.path.join(BASE_DIR, "client_secret2.json"),
                os.path.join(BASE_DIR, "token2.json"))
    return (CLIENT_SECRET, TOKEN_FILE)


def get_service_mm():
    """Service for the Movie Moments channel (third GCP project)."""
    client_secret = os.path.join(BASE_DIR, "client_secret3.json")
    token_file = os.path.join(BASE_DIR, "token3.json")
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def get_service_mm2():
    """Service for the Movie Moments channel via the second quota pool (project 5)."""
    client_secret = os.path.join(BASE_DIR, "client_secret5.json")
    token_file = os.path.join(BASE_DIR, "token5.json")
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def get_service():
    client_secret, token_file = _paths()
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)
