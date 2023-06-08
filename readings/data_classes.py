import yaml


# classes for yaml to deserialize into
class Meter(yaml.YAMLObject):
    """
    Class for storing data necessary for reading data from a meter\n
    Define in yaml with tag !<meter>
    Contains:
        Identification necessary for connection
        A pymodbus connection
        Sets of registers
        Information about register types
    """
    yaml_loader = yaml.SafeLoader
    yaml_tag = u"meter"
    client = None

    class Identification(yaml.YAMLObject):
        yaml_loader = yaml.SafeLoader
        yaml_tag = u"id"

        def __init__(self, name, slave_id, ip_address, tcp_socket):
            self.name = name
            self.slave_id = slave_id
            self.ip_address = ip_address
            self.tcp_socket = tcp_socket

    class RegisterType(yaml.YAMLObject):
        yaml_loader = yaml.SafeLoader
        yaml_tag = u"reg_type"

        def __init__(self, byteorder, wordorder, length):
            self.byteorder = byteorder
            self.wordorder = wordorder
            self.length = length

    def __init__(self, id: Identification, registers: dict, register_types: dict[str, RegisterType]):
        self.id = id
        self.registers = registers
        self.register_types = register_types


class Register(yaml.YAMLObject):
    yaml_loader = yaml.SafeLoader
    yaml_tag = u"reg"

    def __init__(self, register: int, type: str):
        self.register = register
        self.type = type

    def __int__(self) -> int:
        return self.register


# Expected types for returned data from modbus.py functions
class DataTemplates:
    PHASE = {
        "voltage": float,
        "current": float,
        "power_active": float,
        "power_reactive": float,
        "power_apparent": float,
    }

    AVG = {
        "current_demand": float,  # A/15min
        "power_active_demand": float,  # kW/15min
        "power_apparent_demand": float,  # kVA/15min
    }

    PANEL = {
        "pressure_status": bool,
        "diverter_status": bool,
        "oil_status": bool,
        "water_status": bool,
        "water_level": int,
        "diverter_position": int,
    }
# End DataTemplates


def is_correct_to_template(data: dict, template: dict) -> bool:
    for key, value in template.items():
        if key not in data:
            return False
        if not isinstance(data[key], value):
            return False
    return True
