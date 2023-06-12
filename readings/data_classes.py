"""Contains classes for serializing config data and templates for expected data.

"""
import yaml


# classes for yaml to deserialize into
class Meter(yaml.YAMLObject):
    """Class for storing data necessary for reading data from a meter.

    Define in yaml at the root level with: ::

        meter_name: !<meter>
            id: !<id>
                # refer to Identification class
            register_types:
                register_type_name: !<reg_type>
                    # refer to RegisterType class
            registers:
                set_name:
                    register_name: !<reg>
                        # refer to Register class
                combined_set_name:
                    1:
                        register_name: !<reg>
                            # refer to Register class
                    2:
                    # etc

    Attributes
    ----------
    id : Identification
        Information necessary for connection to the meter
    register_types : dict[str, RegisterType]
        Dictionary containing information about register types
    registers : dict[str, dict[str, Register]] | dict[str, dict[any, dict[str, Register]]]
        Sets of registers
    client : pymodbus.client.ModbusBaseClient
        Lazy-loaded Modbus client for the meter
    """
    yaml_loader = yaml.SafeLoader
    yaml_tag = u"meter"
    client = None

    class Identification(yaml.YAMLObject):
        """Class for storing information necessary for connection to a meter.

        Define in yaml within a meter with: ::

            id: !<id>
                attribute: value
                # etc

        Attributes
        ----------
        name : str
            Friendly name of the meter
        slave_id : int
            Modbus slave id
        ip_address : str
            IP address of the meter
        tcp_socket : int
            TCP socket of the meter
        """
        yaml_loader = yaml.SafeLoader
        yaml_tag = u"id"

        def __init__(self, name, slave_id, ip_address, tcp_socket):
            self.name = name
            self.slave_id = slave_id
            self.ip_address = ip_address
            self.tcp_socket = tcp_socket

    class RegisterType(yaml.YAMLObject):
        """Class for storing information about a register type.

        Define in yaml within a meter with: ::

            register_types:
                type_name: !<reg_type>
                    attribute: value
                    # etc

        Attributes
        ----------
        byteorder : str
            Endianess of the register, can take values accepted by pymodbus decoders, such as ``">"``, ``"<"``
        wordorder : str
            Word order of the register, values as above
        length : int
            Amount of concurrent registers necessary to read the whole value
        """
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
    """Class for storing the Modbus address of a register and its intended type.

    **Register name has to match the name of the associated database column.**

    Define in yaml within a register set with: ::

        register_name: !<reg>
            register: address_value
            type: type_name

    Attributes
    ----------
    register : int
        Modbus address of the register
    type : str
        Name of the register type, must be defined in the meter's register_types
        and have an associated decoder in ``_decode_type()`` within ``modbus.py``

    """
    yaml_loader = yaml.SafeLoader
    yaml_tag = u"reg"

    def __init__(self, register: int, type: str):
        self.register = register
        self.type = type

    def __int__(self) -> int:
        return self.register


class DataTemplates:
    """Contains expected keys and types of the data receieved from the meters."""
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
    """Checks if the data matches the template.

    Checks whether the data contains all the keys in the template and if the values have the correct type.

    Parameters
    ----------
    data : dict
        Data to check
    template : dict
        Template to check against, chosen from DataTemplates
    """
    for key, value in template.items():
        if key not in data:
            return False
        if not isinstance(data[key], value):
            return False
    return True
