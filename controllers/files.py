"""Controller for files"""

# Retic
from retic import Request, Response
from retic.services.responses import error_response_service
from retic.services.general import validate_obligate_fields

# Services
import services.files.files as files


def upload(req: Request, res: Response):
    """Upload to Storage"""

    """Check if the all obligate params are valids"""
    _validate = validate_obligate_fields({
        u'files': req.files.get("files", None)
    })
    if _validate["valid"] is False:
        return res.bad_request(
            error_response_service(
                "The param {} is necesary.".format(_validate["error"])
            )
        )

    """Upload the file to Storage"""
    _upload = files.upload(req.files.get("files"))

    """Check if the upload was done"""
    if _upload['valid'] is False:
        return _upload

    """Save the file in the database"""
    _file_db = files.save_file_db({
        **_upload["data"],
        "description": req.param('description', ""),
        "email_to": req.param('email_to', None),
        "email_from": req.param('email_from', None),
    })

    """Check if the file did upload or response an error message"""
    if _file_db['valid'] is False:
        res.bad_request(_file_db)
    else:
        res.ok(_file_db)

def get_by_id(req: Request, res: Response):
    """Get a file by his id"""

    _file_db = files.get_by_id_db(req.param("id"))

    """Check if the file was found or response an error message"""
    if _file_db['valid'] is False:
        res.not_found(_file_db)
    else:
        res.ok(_file_db)
