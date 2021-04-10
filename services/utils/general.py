"""Services for general utils"""
# Os
import os

def get_bytes_from_mb(size):
    """Get bytes from a size in megabytes

    :param size: Integer value in MB
    """
    return size*1024*1024


def get_mb_from_bytes(size):
    """Get megabytes from a size in bytes

    :param size: Integer value in bytes
    """
    return size/1024/1024



def rmfile(path):
    """Delete files from a path

    :param path: Path of the folder with files to will delete
    """
    os.remove(path)

def is_windows():
    if os.name == 'nt':
        return True
    return False