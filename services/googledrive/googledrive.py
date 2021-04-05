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

# base64
from base64 import b64decode

# Mimetypes
import mimetypes

# Retic
from retic import App

# Services
from services.google.apigoogle import get_credentials

# Constants
"""If modifying these scopes, delete the file token.pickle."""
SCOPES = ['https://www.googleapis.com/auth/drive']

# Constants
STORAGE_TOKEN_PATH = App.config.get('STORAGE_TOKEN_PATH')
STORAGE_CREDENTIALS_PATH = App.config.get('STORAGE_CREDENTIALS_PATH')
STORAGE_CREDENTIALS_DEFAULT = App.config.get('STORAGE_CREDENTIALS_DEFAULT')

mimetypes.init()


class GoogleDrive():
    def __init__(self, credential=STORAGE_CREDENTIALS_DEFAULT):
        """Instance of Google Drive"""
        self.service = self.login_v2(credential)
        self.credential = credential

    def login(self):
        """Login a user with credentials from a json file and 
        create a token for the next requests"""

        _creds = None
        """Check if a token exists"""
        if os.path.exists(STORAGE_TOKEN_PATH):
            with open(STORAGE_TOKEN_PATH, 'rb') as token:
                _creds = pickle.load(token)

        """Check if the token doesn't exists or is invalid"""
        if not _creds or not _creds.valid:
            if _creds and _creds.expired and _creds.refresh_token:
                """If the token expired, refresh the token"""
                _creds.refresh(Request())
            else:
                """Generate a new token"""
                _flow = InstalledAppFlow.from_client_secrets_file(
                    STORAGE_CREDENTIALS_PATH, SCOPES)
                _creds = _flow.run_local_server(port=0)
            """Save the credentials for the next run"""
            with open(STORAGE_TOKEN_PATH, 'wb') as token:
                pickle.dump(_creds, token)
        """Return a services that allows it interactive with the storage"""
        return build('drive', 'v3', credentials=_creds)

    def login_v2(self, credential):
        """Login a user with credentials from a json file and
        create a token for the next requests"""

        """Get credential from db"""
        self.token = get_credentials(credential)
        """Return a services that allows it interactive with the storage"""
        return build('drive', 'v3', credentials=self.token)

    def create_media_file(self, file):
        """Media of the file"""
        _media = MediaIoBaseUpload(
            file,
            mimetype=file['mimetype'] if 'mimetype' in file else file.mimetype,
            resumable=True
        )
        return _media

    def create_media_file_binary(self, file):
        _file = BytesIO(b64decode(file))
        _mimetype = 'application/octet-stream'
        """Media of the file"""
        _media = MediaIoBaseUpload(
            _file,
            mimetype=_mimetype,
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

    def create_media_file_from_binary(self, file, extension=None, mimetype=None):
        _file = BytesIO(file)
        _mimetype = mimetypes.types_map[extension] if extension else mimetype if mimetype else 'application/octet-stream'
        """Media of the file"""
        _media = MediaIoBaseUpload(
            _file,
            mimetype=_mimetype,
            resumable=True
        )
        return _media
