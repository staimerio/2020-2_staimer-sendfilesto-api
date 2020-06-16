"""Services for files controller"""

# Retic
from retic import env, App as app

# Google
from services.googledrive.googledrive import GoogleDrive

# Filetype
import filetype
# Models
from models import File

# Services
from retic.services.responses import success_response_service, error_response_service

# Constants
MAX_SIZE = 1024*1024  # Max 1 GB, 1024 MB, 1048576 Kb


def upload(file):
    """Upload a file to google drive

    :param file: File from a client, it's a stream of a file"""

    """Upload the file to Storage"""
    _parent = env("STORAGE_ROOT")
    _gd = GoogleDrive()

    """Define the media of the file"""
    _media = _gd.create_media_file(file)

    """Check if the size is allow"""
    if _media._size >= MAX_SIZE:
        return error_response_service(
            "The size is not allow. Tha max size is: {}".format(MAX_SIZE)
        )

    """Check that extension is valid"""
    _kind = filetype.guess(_media.getbytes(0, _media._size))
    if _kind is None:
        return error_response_service("The file format is invalid.")

    """Upload to storage"""
    _file_cloud = _gd.upload(_media, file.filename, _parent)
    """Define the response"""
    _data_response = {
        'cloud': _file_cloud.get('id'),
        'filename': file.filename,
        'parent': _parent,
        'size': _file_cloud.get('size'),
        'mimetype': file.mimetype,
        'extension': _kind.EXTENSION,
    }

    return success_response_service(_data_response)


def save_file_db(file_data):
    """Create the new schema

    :param file_data: Object that constains all information about a file
    """
    _response = None
    try:
        _file = File(**file_data)

        """Save in database"""
        _session = app.apps.get("db_sqlalchemy")()
        _session.add(_file)
        _session.commit()

        """Get response from db and define the response"""
        _file_db = _file.to_dict()
        _response = success_response_service(
            data=_file_db, msg="The file did upload."
        )
    except Exception as error:
        _response = error_response_service(msg=str(error))
    finally:
        """Close session"""
        _session.close()
    return _response


def get_by_id_db(id):
    """Find a file in the database by an id

    :param id: identificador of the file in the database, by default it is ``cloud``
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
