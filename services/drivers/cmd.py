# Retic
from retic import env, App as app
# import subprocess
# Wget
import wget
# Uuid
import uuid


PUBLIC_FILES_FOLDER = app.config.get('PUBLIC_FILES_FOLDER')


def download_file(url):
    _filename = uuid.uuid1().hex
    _output_path = "{0}/{1}".format(PUBLIC_FILES_FOLDER, _filename,)
    filename = wget.download(url, out=_output_path)
    _file = open(_output_path, 'rb')  # opening a binary file
    _binary_file = _file.read()
    return _binary_file
