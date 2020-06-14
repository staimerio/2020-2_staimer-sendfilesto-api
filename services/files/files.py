"""Services for files controller"""

# Retic
from retic import env

# Google
from services.googledrive.googledrive import GoogleDrive


def upload(file):
    """Upload a file to google drive

    :param file: File from a client, it's a stream of a file"""    
    
    _gd = GoogleDrive()
    
    """Upload the file"""
    _upload = _gd.upload(file, file.name,
                         file.mimetype, env.list("STORAGE_ROOT"))
    return _upload
        
