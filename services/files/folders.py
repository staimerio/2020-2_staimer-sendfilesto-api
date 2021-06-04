"""Services for folder controller"""

# Retic
from retic import env, App as app

# Models
from models import File, Folder

# Services
from retic.services.responses import success_response_service, error_response_service

# SQLAlchemy
from sqlalchemy import update, desc

# Time
from datetime import datetime


def get_all_by_folder_db(code):
    """Find all files in the database by a key and his value

    :param code: id of the key in the database
    """

    """Find in database"""
    _session = app.apps.get("db_sqlalchemy")()

    """Search folder"""
    _folder_db = _session.query(Folder).filter_by(
        code=code, is_deleted=False).first()
    if not _folder_db:
        return error_response_service(msg="Folder not found.")

    """Search files in the folder"""
    _files_db = _session.query(File).join(
        File.folders).filter_by(code=code).order_by(desc(File.filename)).all()

    """Close the session"""
    _session.close()

    """Get response from db and define the response"""
    _files_json = files_to_dict(_files_db)
    _folder_json = _folder_db.to_dict()

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
        """Add file to list"""
        _files_json.append(_file.to_dict())
    return _files_json


def get_folder_by_id_db(code):
    """Soft delete of a folder by his code

    :param code: id of the key in the database
    """

    """Find in database"""
    _session = app.apps.get("db_sqlalchemy")()

    """Search folder"""
    _folder_db = _session.query(Folder).filter_by(
        code=code, is_deleted=False).first()
    if not _folder_db:
        return success_response_service(
            data={}, msg="Folder not found."
        )

    """Make changes"""
    _folder_db.is_deleted = True
    _folder_db.deleted_at = datetime.now()

    """Save folder"""
    _session.commit()

    """Transform the response to client"""
    _data_response = {
        **_folder_db.to_dict()
    }

    """Close the session"""
    _session.close()
    return success_response_service(
        data=_data_response, msg="Folder deleted."
    )
