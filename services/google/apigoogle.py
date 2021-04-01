"""
Google Services to upload, read, download files.
Source: https://developers.google.com/docs/api/quickstart/python
"""

# Pickle
import pickle
# Google
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# Retic
from retic import App
from retic.services.general.json import parse

# Models
from models import Credential

# Constants
"""If modifying these scopes, delete the file token.pickle."""
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/photoslibrary',
    'https://www.googleapis.com/auth/photoslibrary.sharing'
]


def get_credentials(credential):
    """Login a user with credentials from a json file and
    create a token for the next requests"""

    """Get credential from db"""
    _session = App.apps.get("db_sqlalchemy")()
    _credential_db = _session.query(Credential).filter_by(
        credential=credential).first()

    _creds = None
    """Check if a token exists"""
    if _credential_db.picky:
        _creds = pickle.loads(_credential_db.picky)
    """Check if the token doesn't exists or is invalid"""
    if not _creds or not _creds.valid:
        if _creds and _creds.expired and _creds.refresh_token:
            """If the token expired, refresh the token"""
            _creds.refresh(Request())
        else:
            """Generate a new token"""
            _flow = InstalledAppFlow.from_client_config(
                parse(_credential_db.key), SCOPES)
            _creds = _flow.run_local_server(port=0)

        """Save the credentials for the next run"""
        _credential_db.picky = pickle.dumps(_creds)
        _session.commit()
    return _creds
