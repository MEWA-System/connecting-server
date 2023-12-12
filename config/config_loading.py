"""Module for loading configuration data

Methods
-------
load_config

"""

import os
from configparser import ConfigParser

import yaml

from readings.data_classes import Meter, Table


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

    Change it with the environment variable ``MEWA_YAML_CONFIG_PATH``

    Otherwise, it is set to ``config/modbus_registers.yaml``

    Returns
    -------
    str
        Path to the register reference file
    """
    if "MEWA_YAML_CONFIG_PATH" in os.environ:
        return os.environ["MEWA_YAML_CONFIG_PATH"]
    else:
        return os.getcwd() + "/config/modbus_registers.yaml"


def load_yaml_config() -> (dict[str, Meter], dict[str, Table]):
    """Loads the register reference file

    Returns
    -------
    dict[str, Meter]
        Dictionary containing all meters found in the register reference file
    dict[str, Table]
        Dictionary containing all tables found in the register reference file
    """
    path = get_register_reference_path()
    with open(path, "r") as stream:
        registers = yaml.safe_load(stream)
    meters = registers["meters"]
    tables = registers["tables"]
    return meters, tables
