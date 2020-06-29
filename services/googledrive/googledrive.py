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
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Retic
from retic import App

# Constants
"""If modifying these scopes, delete the file token.pickle."""
SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleDrive():
    def __init__(self):
        """Instance of Google Drive"""
        self.storage_token_path = App.config.get('STORAGE_TOKEN_PATH')
        self.storage_credentials_path = App.config.get('STORAGE_CREDENTIALS_PATH')
        self.service = self.login()


    def login(self):
        """Login a user with credentials from a json file and 
        create a token for the next requests"""

        _creds = None
        """Check if a token exists"""
        if os.path.exists(self.storage_token_path):
            with open(self.storage_token_path, 'rb') as token:
                _creds = pickle.load(token)

        """Check if the token doesn't exists or is invalid"""
        if not _creds or not _creds.valid:
            if _creds and _creds.expired and _creds.refresh_token:
                """If the token expired, refresh the token"""
                _creds.refresh(Request())
            else:
                """Generate a new token"""
                _flow = InstalledAppFlow.from_client_secrets_file(
                    self.storage_credentials_path, SCOPES)
                _creds = _flow.run_local_server(port=0)
            """Save the credentials for the next run"""
            with open(self.storage_token_path, 'wb') as token:
                pickle.dump(_creds, token)
        """Return a services that allows it interactive with the storage"""
        return build('drive', 'v3', credentials=_creds)

    def create_media_file(self, file):
        """Media of the file"""
        _media = MediaIoBaseUpload(
            file,
            mimetype=file.mimetype,
            resumable=True
        )
        return _media

    def upload(self, media_body, name, parents=[]):
        """Upload a file to google storage

        :param media_body: Instance of the media file for the file
        :param name: Name of the file will be uploaded
        :param parents: Google folder indicates where the file will be uploaded
        """

        """Metadata of the file"""
        _file_metadata = {
            'name': name,
            "parents": parents
        }

        """Upload a file to Storage"""
        _file = self.service.files().create(
            body=_file_metadata,
            media_body=media_body,
            fields='id,size'
        ).execute()
        return _file

    def download(self, file_id):
        """Download a file from a specific id

        :param file_id: Code of the file to will downloaded
        https://developers.google.com/drive/api/v3/reference/files/get
        """
        request = self.service.files().get_media(
            fileId=file_id
        )
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        return fh.getvalue()
