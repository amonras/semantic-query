import configparser
import logging
import os
from pathlib import Path

import fsspec

logging.basicConfig(
    level=logging.INFO,
    # Define the format of the logs, include the function name and line number
    format="%(asctime)s - %(name)s.%(funcName)s [%(levelname)s]: %(message)s",
)


def root_path():
    return Path(__file__).parent.parent


def get_config():
    # Create a ConfigParser instance
    config = configparser.ConfigParser()

    # Load the configuration file
    config.read(root_path() / 'config.ini')

    return config


def configure_fsspec():
    config = get_config()

    s3_config = {
        "key": os.getenv("AWS_ACCESS_KEY_ID", config.get('s3', 'key')),
        "secret": os.getenv("AWS_SECRET_ACCESS_KEY", config.get('s3', 'secret')),
        "client_kwargs": {
            "endpoint_url": os.getenv("S3_ENDPOINT", config.get('s3', 'endpoint_url'))
        }
    }

    fsspec.config.conf = {
        "s3": s3_config
    }


# Call the function to configure fsspec
configure_fsspec()


def get_fs():
    conf = get_config()
    if conf['storage']['type'] == 's3':
        fs = fsspec.filesystem("s3")
    else:
        fs = fsspec.filesystem("file")
    return fs
