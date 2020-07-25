"""Controller for files"""

# Retic
from retic import Request, Response

# Services
import services.files.folders as folders


def get_by_folder(req: Request, res: Response):
    """Get files by his folder"""

    _folder_db = folders.get_all_by_folder_db(
        req.param("folder")
    )

    """Check if the file was found or response an error message"""
    if _folder_db['valid'] is False:
        res.not_found(_folder_db)
    else:
        res.ok(_folder_db)


def delete_by_folder(req: Request, res: Response):
    """Delete a folder by his folder"""

    _folder_db = folders.get_folder_by_id_db(
        req.param("folder")
    )

    """Check if the file was found or response an error message"""
    if _folder_db['valid'] is False:
        res.not_found(_folder_db)
    else:
        res.ok(_folder_db)
