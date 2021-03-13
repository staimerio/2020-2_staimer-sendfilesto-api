"""
Google Services to upload, read, download files.
Source: https://learndataanalysis.org/upload-media-items-google-photos-api-and-python-part-4/
Source: https://developers.google.com/photos/library/guides/access-media-items
"""

# Pickle
import codecs
import pickle

# Os
import os

# Io
from io import BytesIO

# Requests
import requests

# Asyncio
import asyncio

# Aiohttp
import aiohttp

# Mimetypes
import mimetypes

# Google
from googleapiclient.discovery import build, MediaFileUpload
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Retic
from retic import env, App

# base64
from base64 import b64decode

# Time
from time import sleep

# Services
from retic.services.responses import success_response_service, error_response_service
from retic.services.general.json import jsonify, parse

# Models
from models import Credential

# Constants
"""If modifying these scopes, delete the file token.pickle."""
SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary',
    'https://www.googleapis.com/auth/photoslibrary.sharing'
]

# Constants
PHOTOS_TOKEN_PATH = App.config.get('PHOTOS_TOKEN_PATH')
PHOTOS_CREDENTIALS_PATH = App.config.get('PHOTOS_CREDENTIALS_PATH')
STORAGE_CREDENTIALS_DEFAULT = App.config.get('STORAGE_CREDENTIALS_DEFAULT')
# PHOTOS_ROOT = App.config.get('PHOTOS_ROOT')

image_dir = os.path.join(os.getcwd(), 'Images To Upload')
upload_url = 'https://photoslibrary.googleapis.com/v1/uploads'
mimetypes.init()
SLEEP_TIME = 40


class GooglePhotos():
    def __init__(self, credential=STORAGE_CREDENTIALS_DEFAULT):
        """Instance of Google Drive"""
        self.service = self.login_v2(credential)

    def login(self):
        """Login a user with credentials from a json file and
        create a token for the next requests"""

        _creds = None
        """Check if a token exists"""
        if os.path.exists(PHOTOS_TOKEN_PATH):
            with open(PHOTOS_TOKEN_PATH, 'rb') as token:
                _creds = pickle.load(token)
                self.token = _creds

        """Check if the token doesn't exists or is invalid"""
        if not _creds or not _creds.valid:
            if _creds and _creds.expired and _creds.refresh_token:
                """If the token expired, refresh the token"""
                _creds.refresh(Request())
            else:
                """Generate a new token"""
                _flow = InstalledAppFlow.from_client_secrets_file(
                    PHOTOS_CREDENTIALS_PATH, SCOPES)
                _creds = _flow.run_local_server(port=0)
            """Save the credentials for the next run"""
            with open(PHOTOS_TOKEN_PATH, 'wb') as token:
                pickle.dump(_creds, token)
                self.token = _creds
        """Return a services that allows it interactive with the storage"""
        service = build('photoslibrary', 'v1', credentials=_creds)
        # Call the Photo v1 API
        # results = service.albums().list(
        #     pageSize=10, fields="nextPageToken,albums(id,title)").execute()

        # imgs_response = service.mediaItems().batchGet(
        #     mediaItemIds=[
        #         'AP7Z0LgMS8ZpRJBJe4qI-By9c23uW4nv1WmJSI65bt0rcFmlu7zG4ud4FWcTY9eYmqtzXfACm_LkROK10GZaNexhInWDUM6WWg']
        # ).execute()
        return service

    def login_v2(self, credential):
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
            self.token = _creds
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

            self.token = _creds
        """Return a services that allows it interactive with the storage"""
        service = build('photoslibrary', 'v1', credentials=_creds)
        # Call the Photo v1 API
        # results = service.albums().list(
        #     pageSize=10, fields="nextPageToken,albums(id,title)").execute()

        # imgs_response = service.mediaItems().batchGet(
        #     mediaItemIds=[
        #         'AP7Z0LgMS8ZpRJBJe4qI-By9c23uW4nv1WmJSI65bt0rcFmlu7zG4ud4FWcTY9eYmqtzXfACm_LkROK10GZaNexhInWDUM6WWg']
        # ).execute()
        return service

    def create_media_file(self, file, extension):
        _file = BytesIO(b64decode(file))
        _mimetype = mimetypes.types_map[extension] or 'application/octet-stream'
        """Media of the file"""
        _media = MediaIoBaseUpload(
            _file,
            mimetype=_mimetype,
            resumable=True
        )
        return _media

    def async_upload_pothos(self, photos):
        """Upload a file to google storage

        :param photos: Photos to uploaded
        """
        _uploaded_photos = []
        try:
            async def upload_item_req(photo):
                headers = {
                    'Authorization': 'Bearer ' + self.token.token,
                    'Content-type': photo['mimetype'],
                    'X-Goog-Upload-Protocol': 'raw',
                    'X-Goog-Upload-File-Name': photo['filename']
                }
                img = photo['binary']
                async with aiohttp.ClientSession() as session:
                    async with session.post(url=upload_url, data=img, headers=headers) as response:
                        _uploaded_image = await response.read()
                        if _uploaded_image:
                            _uploaded_photos.append(
                                {
                                    **photo,
                                    u'uploadToken': _uploaded_image.decode('utf-8'),
                                }
                            )

            async def main():
                promises = [upload_item_req(photo)
                            for photo in photos]
                await asyncio.gather(*promises)

            asyncio.run(main())
            """Define response of the service"""
            _response = {
                u'photos': _uploaded_photos
            }
            return success_response_service(
                data=_response
            )
        except Exception as err:
            return error_response_service(
                msg=str(err)
            )

    def sync_upload_pothos(self, photos, noSleep):
        """Upload a file to google storage

        :param photos: Photos to uploaded
        """
        _uploaded_photos = []
        try:
            def upload_item_req(photo):
                headers = {
                    'Authorization': 'Bearer ' + self.token.token,
                    'Content-type': photo['mimetype'],
                    'X-Goog-Upload-Protocol': 'raw',
                    'X-Goog-Upload-File-Name': photo['filename']
                }
                img = photo['binary']
                response = requests.post(
                    url=upload_url, data=img, headers=headers)
                _uploaded_image = response.content
                if _uploaded_image:
                    _uploaded_photos.append(
                        {
                            **photo,
                            u'uploadToken': _uploaded_image.decode('utf-8'),
                        }
                    )
            _count = 0
            for idx, photo in enumerate(photos):
                upload_item_req(photo)

                if(not noSleep and _count == SLEEP_TIME):
                    for idj in range(0, 60):
                        sleep(1)
                    _count = 0
                else:
                    _count += 1

                # with codecs.open('b.txt', mode='w', encoding='utf-8') as f:
                #     f.write('{0}'.format(_count))
            """Define response of the service"""
            _response = {
                u'photos': _uploaded_photos
            }
            return success_response_service(
                data=_response
            )
        except Exception as err:
            return error_response_service(
                msg='{0} images {1}'.format(len(_uploaded_photos), str(err))
            )

    def upload_photos_album(self, photos, album, hasAlbum, noSleep):
        """Upload files to Album"""
        _uploaded_photos = []
        _uploaded_error = []
        _album = {
            "album": {
                "title": album
            }
        }
        # if not hasAlbum:
        """If the album doesnot exist, create a new album from the code"""
        album_response = self.service.albums().create(body=_album).execute()
        _album_id = album_response['id']
        _share = {
            "sharedAlbumOptions": {
                "isCollaborative": "true",
                "isCommentable": "true"
            }
        }
        """Make public the album"""
        _share_response = self.service.albums().share(
            albumId=_album_id, body=_share).execute()
        # else:
        #     """Use the album passed in the parameters"""
        #     _album_id = album

        _count = SLEEP_TIME
        """Merge the information with original photos"""
        for idx, _photo in enumerate(photos):

            if(not noSleep and _count == SLEEP_TIME):
                for idj in range(0, 60):
                    sleep(1)
                _count = 0
            else:
                _count += 1
            # with codecs.open('a.txt', mode='w', encoding='utf-8') as f:
            #     f.write('{0}'.format(_count))

            """Create request body"""
            _request_body = {
                "albumId": _album_id,
                'newMediaItems': [
                    {
                        'description': _photo['filename'],
                        'simpleMediaItem': {
                            'uploadToken': _photo['uploadToken']
                        }
                    }
                ]
            }
            _upload_response = self.service.mediaItems(
            ).batchCreate(body=_request_body).execute()

            _results = _upload_response['newMediaItemResults']

            _uploaded_photo = None
            for _gphoto in _results:
                if _gphoto['uploadToken'] == _photo['uploadToken']:
                    _uploaded_photo = _gphoto
                    break
            if _uploaded_photo and 'mediaItem' in _uploaded_photo:
                _uploaded_photos.append(
                    {
                        **_photo,
                        **_uploaded_photo['mediaItem']
                    }
                )
            else:
                _uploaded_error.append(_uploaded_photo)
        _response = {
            u'photos': _uploaded_photos,
            u'error': _uploaded_error
        }
        return _response

    def download(self, file_id):
        """Download a file from a specific id

        :param file_id: Code of the file to will downloaded
        https://developers.google.com/drive/api/v3/reference/files/get
        """
        _img_response = self.service.mediaItems().get(
            mediaItemId=file_id
        ).execute()
        _url = "{0}=w{1}-h{2}".format(
            _img_response['baseUrl'],
            _img_response['mediaMetadata']['width'],
            _img_response['mediaMetadata']['height'],
        )
        _img_request = requests.get(_url)

        return _img_request

# photos=GooglePhotos()
# print("")
