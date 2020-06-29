"""Services for general utils"""


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
