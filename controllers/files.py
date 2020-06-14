"""Controller for files"""

# Retic
from retic import Request, Response
from retic.services.responses import success_response_service, error_response_service
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

    """Check if the file did upload or response an error message"""
    if not _upload:
        res.bad_request(
            error_response_service("The file did not upload.")
        )
    else:
        res.ok(success_response_service(_upload, "The file did upload."))
