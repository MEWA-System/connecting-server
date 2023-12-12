"""Module for loading configuration data

Methods
-------
load_config

"""

import os
from configparser import ConfigParser


class ConfigNotFound(Exception):
    pass


# Base source https://www.postgresqltutorial.com/postgresql-python/connect/
def load_config(section: str, filename=os.getcwd() + "/config/config.ini"):
    """Loads configuration from a .ini file.

    The working directory is assumed to be the root of the project,
    one folder higher than the config folder.

    Parameters
    ----------
    section : str
        Section of the config file to load
    filename : str, optional
        Path to the config file, by default os.getcwd() + "/config/config.ini"

    Raises
    ------
    ConfigNotFound
        Raised if the section is not found in the config file

    Returns
    -------
    dict[str, str]
        Dictionary of the configuration

    """
    # Create a parser
    parser = ConfigParser()
    # Read config file
    parser.read(filename)

    # Get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise ConfigNotFound(f"Section {section} not found in the {filename} file")
    return config


def get_register_reference_path():
    """Returns the path to the register reference file

    Assumes the working directory is the root of the project.

    Currently locked to /config/modbus_registers.yaml

    Returns
    -------
    str
        Path to the register reference file
    """
    return os.getcwd() + "/config/modbus_registers.yaml"
