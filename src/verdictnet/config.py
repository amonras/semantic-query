import configparser
import json
import logging
import os
from pathlib import Path
from typing import Optional

import fsspec
from airflow.hooks.base import BaseHook

logging.basicConfig(
    level=logging.INFO,
    # Define the format of the logs, include the function name and line number
    format="%(asctime)s - %(name)s.%(funcName)s [%(levelname)s]: %(message)s",
)

logger = logging.getLogger(__name__)

_fsspec_configured = False


def root_path():
    return Path(__file__).parent


def get_config():
    # Create a ConfigParser instance
    config = configparser.ConfigParser()

    # Load the configuration file from the current folder, or from the package root folder
    config.read(filenames=['config.ini', root_path() / 'config.ini'])

    return config


def configure_fsspec():
    global _fsspec_configured
    if _fsspec_configured:
        return

    config = get_config()

    # Check if running within Airflow
    if 'AIRFLOW_HOME' in os.environ:
        # Retrieve the connection details from Airflow
        connection = BaseHook.get_connection('minio')
        s3_config = {
            "key": connection.login,
            "secret": connection.password,
            "client_kwargs": {
                "endpoint_url": connection.extra_dejson.get('endpoint_url')
            }
        }
    else:
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

    # TODO: Warning. This is potentially logging sensitive passwords. Password obfuscation should be implemented.
    logger.info("fsspec configured with: %s", json.dumps(fsspec.config.conf))
    _fsspec_configured = True


def get_fs(conf: Optional[configparser.ConfigParser] = None):
    configure_fsspec()
    conf = conf or get_config()
    if conf['storage']['type'] == 's3':
        fs = fsspec.filesystem("s3")
    else:
        fs = fsspec.filesystem("file")
    return fs
