"""Controller for files"""

# Uuid
import uuid

# Retic
from retic import Request, Response
from retic.services.responses import error_response_service, success_response_service
from retic.services.validations import validate_obligate_fields
from retic import App

# Services
import services.files.files as files

# Constants
PLATFORM_DEFAULT = App.config.get('PLATFORM_DEFAULT')
STORAGE_CREDENTIALS_DEFAULT = App.config.get('STORAGE_CREDENTIALS_DEFAULT')
DRIVER_REQUEST_DEFAULT = App.config.get('DRIVER_REQUEST_DEFAULT')


def upload(req: Request, res: Response):
    """Upload to Storage"""

    """Get the files from the request, if it doesn't exist,
    return an empty list"""
    _files = req.files.getlist('files') or list()
    _credential = req.param(
        'credential', default_value=STORAGE_CREDENTIALS_DEFAULT)

    """Check if the all obligate params are valids"""
    _validate = validate_obligate_fields({
        u'files': _files
    })

    if _validate["valid"] is False:
        return res.bad_request(
            error_response_service(
                "The param {} is necesary.".format(_validate["error"])
            )
        )

    """Upload the file to Storage"""
    _upload_list = files.upload_files(_files, _credential)

    """Generate folder"""
    _folder_code = uuid.uuid1().hex

    """Check if the upload was done"""
    if _upload_list['valid'] is False:
        return res.bad_request(_upload_list)
    elif not _upload_list["data"]["success"]:
        """The result has errors and doesn't have any success file"""
        return res.ok(success_response_service(
            data={**_upload_list['data'], u"code": _folder_code},
            msg="Upload finished with errors."
        ))

    """Save the file in the database"""
    _file_db = files.save_file_db(
        _upload_list["data"]["success"],
        _folder_code,
        {
            "description": req.param('description', ""),
            "platform": req.param('platform', PLATFORM_DEFAULT, int),
            # TODO: Implement email functionality.
            # "email_to": req.param('email_to', None),
            # "email_from": req.param('email_from', None),
        }
    )

    """Check if the file did upload or response an error message"""
    if _file_db['valid'] is False:
        return res.bad_request(_file_db)

    """Define the data response to cliente"""
    _data_response = {
        **_file_db['data'],
        u'error': _upload_list["data"]["error"]
    }

    res.ok(success_response_service(
        data=_data_response,
        msg="The upload finishied."
    ))


def upload_remote(req: Request, res: Response):
    """Upload to Storage"""

    """Get the files from the request, if it doesn't exist,
    return an empty list"""
    _credential = req.param(
        'credential', default_value=STORAGE_CREDENTIALS_DEFAULT)
    _driver = req.param(
        'driver', default_value=DRIVER_REQUEST_DEFAULT,)
    _extension = req.param(
        'extension', default_value=None,)

    """Check if the all obligate params are valids"""
    _validate = validate_obligate_fields({
        u'url': req.param('url')
    })

    if _validate["valid"] is False:
        return res.bad_request(
            error_response_service(
                "The param {} is necesary.".format(_validate["error"])
            )
        )

    """Upload the file to Storage"""
    _upload_list = files.upload_files_remote_uplaod(
        req.param('url'), _credential, driver=_driver, extension=_extension)

    """Generate folder"""
    _folder_code = uuid.uuid1().hex

    """Check if the upload was done"""
    if _upload_list['valid'] is False:
        return res.bad_request(_upload_list)
    elif not _upload_list["data"]["success"]:
        """The result has errors and doesn't have any success file"""
        return res.ok(success_response_service(
            data={**_upload_list['data'], u"code": _folder_code},
            msg="Upload finished with errors."
        ))

    """Save the file in the database"""
    _file_db = files.save_file_db(
        _upload_list["data"]["success"],
        _folder_code,
        {
            "description": req.param('description', ""),
            "platform": req.param('platform', PLATFORM_DEFAULT, int),
            # TODO: Implement email functionality.
            # "email_to": req.param('email_to', None),
            # "email_from": req.param('email_from', None),
        }
    )

    """Check if the file did upload or response an error message"""
    if _file_db['valid'] is False:
        return res.bad_request(_file_db)

    """Define the data response to cliente"""
    _data_response = {
        **_file_db['data'],
        u'error': _upload_list["data"]["error"]
    }

    res.ok(success_response_service(
        data=_data_response,
        msg="The upload finishied."
    ))


def get_by_id(req: Request, res: Response):
    """Get a file by his id"""
    _file_db = files.get_by_id_db(req.param("id"))
    """Check if the file was found or response an error message"""
    if _file_db['valid'] is False:
        res.not_found(_file_db)
    """Transform data"""
    _data_response = {
        **_file_db['data'].to_dict()
    }
    res.ok(success_response_service(
        data=_data_response,
        msg="File found."
    ))


def download_by_id(req: Request, res: Response):
    """Download a file from a id"""

    _file_db = files.get_by_id_db(
        req.param("file")
    )

    """Check if the file was found or response an error message"""
    if _file_db['valid'] is False:
        return res.not_found(_file_db)

    """Download from storage by id"""
    _download_file = files.get_download_from_storage(
        _file_db['data']
    )
    """Return the data to client"""
    if _download_file['valid'] is False:
        """Return a error response to client"""
        res.bad_request(_file_db)
    else:
        res.set_headers({'Content-Type': 'application/octet-stream'})
        """Response a file data to client"""
        res.set_status(200).send(_download_file['data'])
