"""
Google Services to upload, read, download files.
Source: https://developers.google.com/docs/api/quickstart/python
"""

# Pickle
import pickle

# Os
import os

# Io
from io import BytesIO

# Google
from googleapiclient.discovery import build, MediaFileUpload
from googleapiclient.http import MediaIoBaseUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Constants
TOKEN_PATH = 'services/googledrive/token.pickle'
CREDENTIALS_PATH = 'services/googledrive/credentials.json'
"""If modifying these scopes, delete the file token.pickle."""
SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleDrive():
    def __init__(self):
        """Instance of Google Drive"""
        self.service = self.login()

    def login(self):
        """Login a user with credentials from a json file and 
        create a token for the next requests"""

        _creds = None
        """Check if a token exists"""
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'rb') as token:
                _creds = pickle.load(token)

        """Check if the token doesn't exists or is invalid"""
        if not _creds or not _creds.valid:
            if _creds and _creds.expired and _creds.refresh_token:
                """If the token expired, refresh the token"""
                _creds.refresh(Request())
            else:
                """Generate a new token"""
                _flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, SCOPES)
                _creds = _flow.run_local_server(port=0)
            """Save the credentials for the next run"""
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(_creds, token)
        """Return a services that allows it interactive with the storage"""
        return build('drive', 'v3', credentials=_creds)

    def upload(self, stream, name, mimetype, parents=[]):
        """Upload a file to google storage"""

        """Metadata of the file"""
        _file_metadata = {
            'name': name,
            "parents": parents
        }

        """Media of the file"""
        _media = MediaIoBaseUpload(
            stream,
            mimetype=mimetype,
            resumable=True
        )

        """Upload a file to Storage"""
        _file = self.service.files().create(
            body=_file_metadata,
            media_body=_media,
            fields='id'
        ).execute()
        return _file
