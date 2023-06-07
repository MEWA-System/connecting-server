import os
from configparser import ConfigParser


class ConfigNotFound(Exception):
    pass


# Base source https://www.postgresqltutorial.com/postgresql-python/connect/
def load_config(section: str, filename=os.getcwd() + "/config/config.ini"):
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
    return os.getcwd() + "/readings/modbus_registers.yaml"
