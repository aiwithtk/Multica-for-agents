import os
import pickle
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv()


SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_youtube_client():
    creds = None
    
    token_path = os.getenv("YOUTUBE_TOKEN_PICKLE_PATH", "token.pickle")
    client_secrets_path = os.getenv("YOUTUBE_CLIENT_SECRETS_PATH", "client_secrets.json")

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secrets_path):
                print(f"⚠️ {client_secrets_path} is missing! Please configure OAuth2.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
            
    return build('youtube', 'v3', credentials=creds)
