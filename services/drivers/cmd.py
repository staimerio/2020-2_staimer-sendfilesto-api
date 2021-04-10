# Retic
from retic import env, App as app
import subprocess
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


def download_file_cmd(url, stdout=None, stderr=None):
    _filename = uuid.uuid1().hex
    _output_path = "{0}/{1}".format(PUBLIC_FILES_FOLDER, _filename,)
    try:
        _cmd = ['wget', '-O', _output_path, '"{0}"'.format(url)]
        print(_cmd)
        process = subprocess.call(_cmd)
    except OSError as e:
        raise Exception(
            "Executable '{0}' not found".format(self.executable))
    _file = open(_output_path, 'rb')  # opening a binary file
    _binary_file = _file.read()
    print("///{0}".format(len(_binary_file)))
    return _binary_file


def _merge_args_opts(args_opts_dict, **kwargs):
    """Merge options with their corresponding arguments.

    Iterates over the dictionary holding arguments (keys) and options (values). Merges each
    options string with its corresponding argument.

    Parameters
    -----------
    args_opts_dict : dict
        a dictionary of arguments and options
    kwargs : dict
        *input_option* - if specified prepends ``-i`` to input argument

    Returns
    --------
    list
        a merged list of strings with arguments and their corresponding options
    """
    merged = []

    if not args_opts_dict:
        return merged

    for arg, opt in args_opts_dict.items():
        if not _is_sequence(opt):
            opt = shlex.split(opt or '')
        merged += opt

        if not arg:
            continue

        if 'add_input_option' in kwargs:
            merged.append('-i')

        merged.append(arg)

    return merged
