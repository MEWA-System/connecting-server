import yaml


# classes for yaml to deserialize into
class Meter(yaml.YAMLObject):
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


# classes for holding data, to transfer to the db saving function
class PhaseReadings:
    phase: int
    voltage: float
    current: float
    power_active: float
    power_reactive: float


class ElectricReadings:
    phase1: PhaseReadings
    phase2: PhaseReadings
    phase3: PhaseReadings
    power_active_avg: float
