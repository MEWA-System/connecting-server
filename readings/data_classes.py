# classes for yaml to deserialize into
class Meter:
    class Identification:
        name: str
        id: int
        id_register: int


# classes for transferring data between
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
