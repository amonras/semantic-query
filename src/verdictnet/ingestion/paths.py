from pathlib import Path

import fsspec

from verdictnet.config import root_path, get_config, logging

logger = logging.getLogger(__name__)

conf = get_config()


def fsspec_walk(path):
    """
    Implement os.walk over fsspec filesystems. Prepend the necessary prefix to the paths
    depending on configured the storage type.
    """
    fs, _, _ = fsspec.get_fs_token_paths(path)
    if conf['storage']['type'] == 's3':
        prefix = "s3://"
    else:
        prefix = "file://"

    for dirpath, dirnames, filenames in fs.walk(path):
        yield prefix + dirpath, dirnames, filenames


def raw_path():
    """
    Return the path where we store raw objects downloaded from the internet
    """
    if conf['storage']['type'] == 'local':
        return root_path() / conf['storage']['bucket'] / conf['storage']['raw']
    elif conf['storage']['type'] == 's3':
        return f"s3://{conf['storage']['bucket']}/{conf['storage']['raw']}"


def refined_path():
    """
    Return the path where we store refined objects as JSON files ready to be ingested
    into the database
    """
    if conf['storage']['type'] == 'local':
        return root_path() / conf['storage']['bucket'] / conf['storage']['refined']
    elif conf['storage']['type'] == 's3':
        return f"s3://{conf['storage']['bucket']}/{conf['storage']['refined']}"


def html_path():
    """
    Return the path where we store refined objects as JSON files ready to be ingested
    into the database
    """
    if conf['storage']['type'] == 'local':
        return root_path() / conf['storage']['bucket'] / conf['storage']['html']
    elif conf['storage']['type'] == 's3':
        return f"s3://{conf['storage']['bucket']}/{conf['storage']['html']}"
