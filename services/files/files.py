"""Services for files controller"""

# Retic
from retic import env, App as app

# Google
from services.googledrive.googledrive import GoogleDrive

# Filetype
import filetype

# Models
from models import File, Folder

# Services
from retic.services.responses import success_response_service, error_response_service

# Utils
from services.utils.general import get_bytes_from_mb, get_mb_from_bytes

# Constants
MAX_SIZE = get_bytes_from_mb(env("STORAGE_MAX_SIZE"))  # Max 0.05 GB, 50 MB, 51200 Kb


def upload(file, gd):
    """Upload a file to google drive

    :param file: File from a client, it's a stream of a file"""

    try:
        """Upload the file to Storage"""
        _parent = env("STORAGE_ROOT")

        """Define the media of the file"""
        _media = gd.create_media_file(file)

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
        _extension = _kind.EXTENSION if _kind else file.filename.split('.')[-1]

        """Upload to storage"""
        _file_cloud = gd.upload(_media, file.filename, [_parent])
        """Define the response"""
        _data_response = {
            'cloud': _file_cloud.get('id'),
            'filename': file.filename,
            'parent': _parent,
            'size': _file_cloud.get('size'),
            'mimetype': file.mimetype,
            'extension': _extension,
        }

        return success_response_service(_data_response)
    except Exception as err:
        return error_response_service(str(err))


def upload_files(files):
    """Upload a file list to google drive

    :param files: Files from a client, it's a stream list of a files"""

    try:
        _files_upload_success = []
        _files_upload_error = []
        _gd = GoogleDrive()
        """Upload the file to Storage"""
        for file in files:
            """Define the media of the file"""
            _file_cloud = upload(file, _gd)

            """Check if has error"""
            if _file_cloud["valid"] is False:
                """Add file to error list"""
                _files_upload_error.append({
                    'msg': _file_cloud['msg'],
                    'filename': file.filename
                })
            else:
                """Add file to success list"""
                _files_upload_success.append({
                    **_file_cloud['data']
                })

        """Define the response"""
        _data_response = {
            'success': _files_upload_success,
            'error': _files_upload_error,
        }
        return success_response_service(_data_response)
    except Exception as err:
        return error_response_service(str(err))


def save_file_db(files, code, metadata):
    """Create the new schema

    :param files: Storage files that contains information about the upload of the files
    :param metadata: Object that constains all information about a file
    """
    _response = None
    _session = app.apps.get("db_sqlalchemy")()
    try:
        """Save folder"""
        _folder_db = Folder(**metadata, code=code)

        """Create File instance for insert to db"""
        for _file in files:
            """Create the scheme"""
            _file_db = File(**_file)
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


def get_by_id_db(id):
    """Find a file in the database by an id

    :param id: identificador of the file in the database, by default the key is ``cloud``
    """

    """Find in database"""
    _session = app.apps.get("db_sqlalchemy")()
    _file = _session.query(File).filter_by(cloud=id).first()
    _session.close()

    """Check if the file exists"""
    if not _file:
        return error_response_service(msg="File not found.")
    else:
        return success_response_service(
            data=_file.to_dict(), msg="File found."
        )


def get_all_by_folder_db(code):
    """Find all files in the database by a key and his value

    :param code: identificador of the key in the database
    """

    """Find in database"""
    _session = app.apps.get("db_sqlalchemy")()

    """Search folder"""
    _folder = _session.query(Folder).filter_by(code=code).first()
    if not _folder:
        return error_response_service(msg="Folder not found.")

    """Search files in the folder"""
    _files = _session.query(File).join(
        File.folders).filter_by(code=code)

    """Close the session"""
    _session.close()

    """Get response from db and define the response"""
    _files_json = files_to_dict(_files)
    _folder_json = _folder.to_dict()

    """Transform the response to client"""
    _data_response = {
        u"success": _files_json,
        **_folder_json,
    }
    return success_response_service(
        data=_data_response, msg="Files found."
    )


def files_to_dict(files):
    """Get response from db and define the

    :param files: files list from the db    
    """
    _files_json = list()
    for _file in files:
        _files_json.append(_file.to_dict())
    return _files_json


def get_download_from_storage(file):
    """Download a file from storage

    :param file: File instance of the file from the db
    """
    try:
        _gd = GoogleDrive()

        """Get te ddata from the storage by id"""
        _data_file = _gd.download(file['cloud'])
        """Return the data to cliente"""
        return success_response_service(
            data=_data_file
        )
    except Exception as err:
        return error_response_service(str(err))
