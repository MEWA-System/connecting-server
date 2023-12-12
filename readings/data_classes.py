"""Contains classes for serializing config data and templates for expected data.

"""
import yaml
import threading


# classes for yaml to deserialize into
class Meter(yaml.YAMLObject):
    """Class for storing data necessary for reading data from a meter.

    Define in yaml at the root level with: ::

        meters:
            meter_name: !<meter>
                id: !<id>
                    # refer to Identification class
                register_types:
                    register_type_name: !<reg_type>
                        # refer to RegisterType class

    Attributes
    ----------
    id : Identification
        Information necessary for connection to the meter
    register_types : dict[str, RegisterType]
        Dictionary containing information about register types
    client : pymodbus.client.ModbusBaseClient
        Lazy-loaded Modbus client for the meter
    lock : threading.Lock
        Lock for the client, to prevent concurrent connections
    """
    yaml_loader = yaml.SafeLoader
    yaml_tag = u"meter"
    client = None
    lock = threading.Lock()

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

        def __init__(self, byteorder, wordorder, length, read_type="input"):
            self.byteorder = byteorder
            self.wordorder = wordorder
            self.length = length
            self.read_type = read_type

    def __init__(self, id: Identification, register_types: dict[str, RegisterType]):
        self.id = id
        self.register_types = register_types


class Table(yaml.YAMLObject):
    """Dictionary containing registers for a QuestDB table.

    Define in yaml at the root level with: ::

        tables:
            table_name: !<table>
                type: simple
                fields:
                    register_name: !<reg>
                        # refer to Register class
                    register_name2: !<reg>
                        # refer to Register class
                    # etc

    or, for a symbolic table: ::

        tables:
            table_name: !<table>
                type: symbolic
                symbol_field: name_of_symbol
                fields:
                    symbol_value:
                        register_name: !<reg>
                            # refer to Register class
                    symbol_value2:
                    # etc


    In a simple table, all fields are ingested to the same row

    In a symbolic table, some fields are separated to several rows, per each symbol value.
    The fields under each symbol are intended to have duplicate names between the symbols,
    but different registers or meters


    Attributes
    ----------
    type : str
        Type of the table, either ``simple`` or ``symbolic``
    fields : dict[str, Register] | dict[str, dict[any, Register]]
        Dictionary of registers that will be read and ingested into the table
        In a symbolic table, the registers must be nested in another dictionary,
        representing the symbol they will be grouped by
    symbol_name : str
        Name of the field used for storing the symbol in a symbolic table
    """
    class Types:
        SIMPLE = "simple"
        SYMBOLIC = "symbolic"

    yaml_loader = yaml.SafeLoader
    yaml_tag = u"table"

    def __init__(self, fields: dict, type: str = Types.SIMPLE, symbol_name: str = None):
        self.type = type
        self.fields = fields
        self.symbol_name = symbol_name


class Register(yaml.YAMLObject):
    """Class for storing the Modbus address of a register and its intended type.

    **Register name has to match the name of the associated database column.**

    Define in yaml within a table's fields section with: ::

        register_name: !<reg>
            register: address_value
            type: type_name        # must be defined in the meter's register_types
            meter: meter_name      # must be defined in meters: section

    Attributes
    ----------
    register : int
        Modbus address of the register
    type : str
        Name of the register type, must be defined in the meter's register_types
        and have an associated decoder in ``_decode_type()`` within ``modbus.py``
    meter : str
        Name of the meter the register should be read from

    """
    yaml_loader = yaml.SafeLoader
    yaml_tag = u"reg"

    def __init__(self, register: int, type: str, meter: str):
        self.register = register
        self.type = type
        self.meter = meter

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
