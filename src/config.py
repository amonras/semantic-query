import configparser
import os
from pathlib import Path


def root_path():
    return Path(__file__).parent.parent


def get_config():
    # Create a ConfigParser instance
    config = configparser.ConfigParser()

    # Load the configuration file
    config.read(root_path() / 'config.ini')

    return config