"""Services for files controller"""

# Retic
from retic import env, App as app

# Google
from services.googlephotos.googlephotos import GooglePhotos

# Uuid
import uuid

# Asyncio
import asyncio

# Aiohttp
import aiohttp

# Models
from models import File, Folder

# Services
from retic.services.responses import success_response_service, error_response_service
from retic.services.general.urls import slugify

# Utils
from services.utils.general import get_bytes_from_mb, get_mb_from_bytes

# Constants
MAX_SIZE = get_bytes_from_mb(env.int("STORAGE_MAX_SIZE"))


def upload(file, gphotos):
    """Upload a file to google drive

    :param file: File from a client, it's a stream of a file"""

    try:
        """Upload the file to Storage"""
        _parent = env("STORAGE_ROOT")

        _filename_split = file['filename'].split('.')
        _slug = slugify(_filename_split[0])
        _extension = _filename_split[-1]

        _extension_full = ".{0}".format(_extension)

        """Define the media of the file"""
        _media = gphotos.create_media_file(file['binary'], _extension_full)

        _size = len(file['binary'])

        """Check if the size is allow"""
        if _size == 0:
            return error_response_service(
                "The file contains no data."
            )
        elif _size >= MAX_SIZE:
            return error_response_service(
                "The size is not allow. Tha max size is: {}MB".format(
                    get_mb_from_bytes(MAX_SIZE))
            )

        """Define the response"""
        _data_response = {
            # 'cloud': _file_cloud.get('id'),
            'binary': file['binary'],
            'filename': file['filename'],
            'filename_slug': "{0}.{1}".format(_slug, _extension),
            'mimetype': _media._mimetype,
            'size': _size,
            'extension': _extension,
        }

        return success_response_service(_data_response)
    except Exception as err:
        return error_response_service(str(err))


def download_photos_remote(urls, headers):
    """Upload a url list to google photos

    :param urls: Urls from a client, it's a url list of a files
    :param header: Headers to include  in the request to image
    """

    """Define all variables"""
    _images_success = []
    _images_error = []
    try:
        async def get_download_item_req(url):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url=url, headers=headers) as response:
                        _downloaded_image = await response.read()
                        if _downloaded_image:
                            _images_success.append(
                                {
                                    u'binary': _downloaded_image,
                                    u'filename': url.split('/')[-1]
                                }
                            )
                        else:
                            _images_error.append({u'url': url})
            except Exception as e:
                _images_error.append({u'url': url})

        async def main():
            promises = [get_download_item_req(_url)
                        for _url in urls]
            await asyncio.gather(*promises)

        asyncio.run(main())

        _response = {
            'success': _images_success,
            'error': _images_error
        }
        return success_response_service(
            data=_response
        )
    except Exception as err:
        return error_response_service(
            msg=str(err)
        )


def upload_photos(photos, album, hasAlbum):
    """Upload a url list to google photos

    :param urls: Urls from a client, it's a url list of a files
    :param header: Headers to include  in the request to image
    """
    try:
        _files_upload = []
        _files_upload_success = []
        _files_upload_error = []
        _gphotos = GooglePhotos()

        for _file in photos:
            """Define the media of the file"""
            _file_cloud = upload(_file, _gphotos)
            """Check if has error"""
            if _file_cloud["valid"] is False:
                _files_upload_error.append(_file)
            else:
                _files_upload.append(_file_cloud['data'])

        if not _files_upload:
            """Define the response"""
            _data_response = {
                'success': [],
                'error': _files_upload_error,
            }
            return error_response_service(_data_response)

        """Upload to storage"""
        _files_cloud = _gphotos.async_upload_pothos(_files_upload)

        """Check if its valid"""
        if _files_cloud['valid'] is False:
            return _files_cloud

        _files_upload_cloud = _gphotos.upload_photos_album(
            _files_cloud['data']['photos'], album, hasAlbum)

        for _file_upload_cloud in _files_upload_cloud['photos']:
            """Define the response"""
            _data_response = {
                'cloud': _file_upload_cloud['id'],
                'filename': _file_upload_cloud['filename_slug'],
                'title': _file_upload_cloud['filename'],
                'parent': album,
                'size': _file_upload_cloud['size'],
                'mimetype': _file_upload_cloud['mimeType'],
                'extension': _file_upload_cloud['extension'],
                'width': _file_upload_cloud['mediaMetadata']['width'],
                'height': _file_upload_cloud['mediaMetadata']['height'],
            }
            _files_upload_success.append(_data_response)

        """Define the response"""
        _data_response = {
            'success': _files_upload_success,
            'error': (_files_upload_error or []) + (_files_upload_cloud['error'] or []),
        }
        return success_response_service(_data_response)
    except Exception as err:
        return error_response_service(str(err))


def save_file_db(files, album_id, metadata):
    """Create the new schema

    :param files: Storage files that contains information about the upload of the files
    :param album_id: Id of the album to save files
    :param metadata: Object that constains all information about a file
    """
    _response = None
    _session = app.apps.get("db_sqlalchemy")()
    try:
        """Save folder"""
        _folder_db = Folder(**metadata, code=album_id)

        """Create File instance for insert to db"""
        for _file in files:
            """Generate folder"""
            _file_code = uuid.uuid1().hex
            """Create the scheme"""
            _file_db = File(**_file, code=_file_code)
            """Into folder to file"""
            _folder_db.files.append(_file_db)

        """Save in database"""
        _session.add(_folder_db)
        _session.commit()

        """Get response from db and define the response"""
        _files_json = files_to_dict(_folder_db.files)
        _folder_json = _folder_db.to_dict()

        """Define the response to cliente"""
        _response = success_response_service(
            data={**_folder_json, u"success": _files_json},
        )
    except Exception as error:
        """Response the error to client"""
        _response = error_response_service(str(error))
    finally:
        """Close session"""
        _session.close()
    return _response


def get_by_filename_db(album, filename):
    """Find a file in the database by an id

    :param album: album of the photo
    :param filename: filename of the photo
    """

    """Find in database"""
    _session = app.apps.get("db_sqlalchemy")()
    _photo = _session.query(File).filter_by(
        parent=album, filename=filename).first()
    _session.close()

    """Check if the file exists"""
    if not _photo:
        return error_response_service(msg="Photo not found.")
    else:
        return success_response_service(
            data=_photo
        )


def get_download_from_storage(file):
    """Download a file from storage

    :param file: File instance of the file from the db
    """
    try:
        _gphotos = GooglePhotos()

        """Get te ddata from the storage by id"""
        _data_file = _gphotos.download(file.cloud)
        """Return the data to cliente"""
        return success_response_service(
            data=_data_file
        )
    except Exception as err:
        return error_response_service("Bad request.")


def files_to_dict(files):
    """Get response from db and define the

    :param files: files list from the db    
    """
    _files_json = list()
    for _file in files:
        """Add file to list"""
        _files_json.append(_file.to_dict())
    return _files_json
