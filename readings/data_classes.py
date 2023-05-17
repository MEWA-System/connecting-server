import yaml


# classes for yaml to deserialize into
class Meter(yaml.YAMLObject):
    yaml_loader = yaml.SafeLoader
    yaml_tag = u"meter"

    class Identification(yaml.YAMLObject):
        yaml_loader = yaml.SafeLoader
        yaml_tag = u"id"

        def __init__(self, name, slave_id, ip_address, tcp_socket):
            self.name = name
            self.slave_id = slave_id
            self.ip_address = ip_address
            self.tcp_socket = tcp_socket

    def __init__(self, id: Identification, registers: dict):
        self.id = id
        self.registers = registers


class Register(yaml.YAMLObject):
    yaml_loader = yaml.SafeLoader
    yaml_tag = u"reg"

    def __init__(self, register: int, type):
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
