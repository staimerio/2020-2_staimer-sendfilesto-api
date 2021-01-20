"""Services for files controller"""

# Retic
from retic import env, App as app

# Uuid
import uuid

# Asyncio
import asyncio

# Aiohttp
import aiohttp

# Filetype
import filetype

# Google
from services.googledrive.googledrive import GoogleDrive

# Models
from models import File, Folder, Object

# Services
from retic.services.responses import success_response_service, error_response_service
from retic.services.general.urls import slugify
from retic.services.general.json import jsonify, parse


# Utils
from services.utils.general import get_bytes_from_mb, get_mb_from_bytes

# Constants
MAX_SIZE = get_bytes_from_mb(env.int("STORAGE_MAX_SIZE"))


def upload(file, gd):
    """Upload a file to google drive

    :param file: File from a client, it's a stream of a file"""

    try:
        """Upload the file to Storage"""
        _parent = env("STORAGE_ROOT")

        """Define the media of the file"""
        _media = gd.create_media_file_from_binary(
            file['binary'], mimetype=file['mimetype'])

        """Check if the size is allow"""
        if _media._size == 0:
            return error_response_service(
                "The file contains no data."
            )
        elif _media._size >= MAX_SIZE:
            return error_response_service(
                "The size is not allow. Tha max size is: {}MB".format(
                    get_mb_from_bytes(MAX_SIZE))
            )

        """Check that extension is valid"""
        _kind = filetype.guess(_media.getbytes(0, _media._size))
        """If the kind is not in the libs, get the extension from the filename"""
        _extension_file = file['extension'] if 'extension' in file else 'unk'
        _extension = _kind.EXTENSION if _kind else _extension_file

        """Upload to storage"""
        _file_cloud = gd.upload(_media, file['filename'], [_parent])
        """Define the response"""
        _data_response = {
            'cloud': _file_cloud.get('id'),
            'filename': file['filename'],
            'title': file['filename'],
            'parent': _parent,
            'size': _file_cloud.get('size'),
            'mimetype': file['mimetype'],
            'extension': _extension,
        }

        return success_response_service(_data_response)
    except Exception as err:
        return error_response_service(str(err))


def download_files_remote(items, headers):
    """Upload a url list to google items

    :param items: Items from a client, it's a url list of a files
    :param header: Headers to include  in the request to image
    """

    """Define all variables"""
    _items_success = []
    _items_error = []
    try:
        async def get_download_item_req(_item):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url=_item['url'], headers=headers) as response:
                        _downloaded_item = await response.read()
                        if _downloaded_item:
                            _items_success.append(
                                {
                                    **_item,
                                    u'binary': _downloaded_item,
                                }
                            )
                        else:
                            _items_error.append({u'item': _item})
            except Exception as e:
                _items_error.append({u'item': _item})

        async def main():
            promises = [get_download_item_req(_item)
                        for _item in items]
            await asyncio.gather(*promises)

        asyncio.run(main())

        _response = {
            'success': _items_success,
            'error': _items_error
        }
        return success_response_service(
            data=_response
        )
    except Exception as err:
        return error_response_service(
            msg=str(err)
        )


def upload_files(files, album, hasAlbum):
    """Upload a url list to google files

    :param urls: Urls from a client, it's a url list of a files
    :param header: Headers to include  in the request to image
    """
    try:
        _files_upload = []
        _files_upload_success = []
        _files_upload_error = []
        _gd = GoogleDrive()

        for _file in files:
            """Define the media of the file"""
            _file_cloud = upload(_file, _gd)
            """Check if has error"""
            if _file_cloud["valid"] is False:
                del _file['binary']
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

        """Define the response"""
        _data_response = {
            'success': _files_upload,
            'error': _files_upload_error or [],
        }
        return success_response_service(_data_response)
    except Exception as err:
        return error_response_service(str(err))


def save_file_db(files, folder_id, metadata):
    """Create the new schema

    :param files: Storage files that contains information about the upload of the files
    :param folder_id: Id of the album to save files
    :param metadata: Object that constains all information about a file
    """
    _response = None
    _session = app.apps.get("db_sqlalchemy")()
    try:
        """Save folder"""
        _folder_db = Folder(**metadata, code=folder_id)

        _object_content = {
            u'files': files
        }
        _object_code = uuid.uuid1().hex

        _object_db = Object(
            content=jsonify(_object_content),
            code=_object_code,
            parent=folder_id
        )
        """Into folder to file"""
        _folder_db.objects.append(_object_db)
        """Save in database"""
        _session.add(_folder_db)
        _session.commit()

        """Get response from db and define the response"""
        _folder_json = _folder_db.to_dict()
        _object_json = _object_db.to_dict()

        """Define the response to cliente"""
        _response = success_response_service(
            data={**_folder_json, u"success": [_object_json]},
        )
    except Exception as error:
        """Response the error to client"""
        _response = error_response_service(str(error))
    finally:
        """Close session"""
        _session.close()
    return _response

def get_download_from_storage(file, filename):
    """Download a file from storage

    :param file: File instance of the file from the db
    """
    try:
        _object = parse(file.content)
        _selected_file = None
        for _file in _object['files']:
            if _file['filename'] == filename:
                _selected_file = _file
                break
        if not _selected_file:
            raise Exception("File not found")
        _gd = GoogleDrive()

        """Get te ddata from the storage by id"""
        _data_file = _gd.download(_selected_file['cloud'])
        """Return the data to cliente"""
        return success_response_service(
            data=_data_file
        )
    except Exception as err:
        return error_response_service("Bad request.")

def get_by_code_db(folder, code):
    """Find a file in the database by an id

    :param album: album of the photo
    :param code: code of the object
    """

    """Find in database"""
    _session = app.apps.get("db_sqlalchemy")()
    _file = _session.query(Object).filter_by(
        parent=folder, code=code).first()
    _session.close()

    """Check if the file exists"""
    if not _file:
        return error_response_service(msg="File not found.")
    else:
        return success_response_service(
            data=_file
        )