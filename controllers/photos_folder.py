"""Controller for files"""

# Uuid
import uuid

# Retic
from retic import Request, Response
from retic.services.responses import error_response_service, success_response_service
from retic.services.general.json import jsonify
from retic.services.validations import validate_obligate_fields
from retic import App

# Services
from services.files import photos_folder

# Constants
PLATFORM_DEFAULT = App.config.get('PLATFORM_DEFAULT')


def upload_folder(req: Request, res: Response):
    """Generate folder"""
    _album_code = req.param('album', default_value=uuid.uuid1().hex)
    if req.param('urls'):
        """Upload the file to Storage"""
        _upload_list = photos_folder.download_photos_remote(
            req.param('urls'),
            req.param('headers', default_value={}),
        )
    else:
        return res.bad_request(
            error_response_service(
                "The param ulrs is necesary."
            )
        )
    """Check if the upload was done"""
    if _upload_list['valid'] is False:
        return res.bad_request(_upload_list)

    if not _upload_list['data']['success']:
        return res.bad_request(success_response_service(
            {
                u'success': [],
                u'error': _upload_list['data']['error']
            }
        ))
    """Upload the file to Storage"""
    _uploaded_list = photos_folder.upload_photos(
        _upload_list['data']['success'], _album_code, req.param('album', callback=bool))

    """Check if the upload was done"""
    if _uploaded_list['valid'] is False:
        return res.bad_request(_uploaded_list)
    """Save the file in the database"""
    _photos_db = photos_folder.save_file_db(
        _uploaded_list["data"]["success"],
        _album_code,
        {
            "description": req.param('description', ""),
            "platform": req.param('platform', PLATFORM_DEFAULT, int),
            # TODO: Implement email functionality.
            # "email_to": req.param('email_to', None),
            # "email_from": req.param('email_from', None),
        }
    )

    """Check if the file did upload or response an error message"""
    if _photos_db['valid'] is False:
        return res.bad_request(_photos_db)

    """Define the data response to cliente"""
    _data_response = {
        **_photos_db['data'],
        u'error': _upload_list["data"]["error"]+_uploaded_list["data"]["error"]
    }

    res.ok(success_response_service(
        data=_data_response,
        msg="The upload finishied."
    ))

def show_by_code(req: Request, res: Response):
    """Download a file from a id"""

    """Check if the all obligate params are valids"""
    _validate = validate_obligate_fields({
        u'album': req.param("album"),
        u'filename': req.param("filename"),
        u'code': req.param("code"),
    })

    if _validate["valid"] is False:
        return res.bad_request(
            error_response_service(
                "The param {} is necesary.".format(_validate["error"])
            )
        )

    _photo_db = photos_folder.get_by_code_db(
        req.param("album"),
        req.param("code"),
    )

    """Check if the file was found or response an error message"""
    if _photo_db['valid'] is False:
        return res.not_found(_photo_db)

    """Download from storage by id"""
    _download_file = photos_folder.get_download_from_storage(
        _photo_db['data'], req.param("filename")
    )
    """Return the data to client"""
    if _download_file['valid'] is False:
        """Return a error response to client"""
        res.bad_request(_photo_db)
    else:
        """Response a file data to client"""
        _img_req = _download_file['data']
        _headers = {**_img_req.headers}

        res.set_headers(
            _headers
        )
        res.set_headers('custom_headers', jsonify(_headers))
        res.set_status(200).send(_img_req.content)