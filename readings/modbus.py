"""Module for reading data from the meters using the Modbus protocol.

Requires a register reference yaml file.
See Also
--------
``config.config_loading.get_register_reference_path``
    See for information on the location of the file
``readings.data_classes.Meter``
    See for information on the structure of the file

"""
from typing import Optional

import yaml
from pymodbus import client as mbc, payload as mbp

from config.config_loading import get_register_reference_path
from readings.data_classes import Meter, Register

# Global variables
# Dictionary containing all loaded meters
meters: Optional[dict[str, Meter]] = None
# Path to the register and meter config file
config: str = get_register_reference_path()


def _get_meters() -> dict[str, Meter]:
    """Lazily loads the register reference file and returns the meters dictionary

    Returns
    -------
    dict[str, Meter]
        Dictionary containing all meters found in the register reference file
    """
    global meters
    if meters is None:
        _load_register_reference()
    return meters


def _get_electric() -> Meter:
    meters = _get_meters()
    return meters["electric"]


def _get_panel() -> Meter:
    return _get_meters()["water_panel"]


async def _connect_meter(meter: Meter):
    """Lazily connects to the meter, creates a client if needed

    Parameters
    ----------
    meter : Meter
        Reference to the meter object
    """
    if meter.client is None:
        meter.client = mbc.AsyncModbusTcpClient(meter.id.ip_address, meter.id.tcp_socket)
    if not meter.client.connected:
        await meter.client.connect()


def _load_register_reference():
    global config, meters
    with open(config, "r") as stream:
        meters = yaml.safe_load(stream)


async def _modbus_test(phase: int):
    global meters
    electric = meters["electric"]
    assert electric is not None
    client = mbc.AsyncModbusTcpClient(electric.id.ip_address, electric.id.tcp_socket)
    await client.connect()
    response = await client.read_input_registers(electric.registers["phases"][phase]["voltage"].register, 1,
                                                 electric.id.slave_id)
    print(response)

    await client.close()


def _decode_type(register: Register, decoder: mbp.BinaryPayloadDecoder) -> any:
    """Decodes the register value based on the register type

    Supported types:
        - ``"float"`` (4 bytes) ``-> float``
        - ``"int"`` (2 bytes) ``-> int``
        - ``"uint8"`` (1 byte) ``-> int``
        - ``"bool8"`` (1 byte) ``-> bool``

    Parameters
    ----------
    register : Register
        current register with supported type-string in register.type
    decoder :  mbp.BinaryPayloadDecoder
        pymodbus decoder created from the response and containing the necessary number of bytes for the type

    Raises
    ------
    ValueError
        If the register type is not supported by the decoder or implemented in this function

    Returns
    -------
    any
        Decoded value, type depends on the register type


    """
    match register.type:
        case "float":
            return decoder.decode_32bit_float()
        case "int":
            return decoder.decode_16bit_int()
        case "uint8":
            return decoder.decode_8bit_uint()
        case "bool8":
            return bool(decoder.decode_8bit_uint())
        case _:
            raise ValueError(f"Register type unsupported by the decoder: {register.type}")


async def _read_register(meter: Meter, register: Register) -> any:
    """Reads a given register from the meter.

    Requires the meter to be connected and the register to be defined in the meter configuration.

    Parameters
    ----------
    meter : Meter
        Reference to the meter object
        Needs to be already connected
    register : Register
        Reference to the intended register object

    Returns
    -------
    any
        Value from the register decoded according to its type
    """
    assert meter.client is not None
    reg_type = meter.register_types[register.type]
    if reg_type is None:
        raise ValueError(f"Register type '{register.type}' not found in configuration")

    response = await meter.client.read_input_registers(register.register, reg_type.length, meter.id.slave_id)
    if response.isError():
        raise ConnectionError(f"Error reading register {register.register}: {response}")

    decoder = mbp.BinaryPayloadDecoder.fromRegisters(response.registers, reg_type.byteorder, reg_type.wordorder)

    return _decode_type(register, decoder)


async def _read_registers(meter: Meter, registers: dict[str, Register]) -> dict:
    """Reads a set of registers from the meter

    Lazy-connects to the meter if needed

    Parameters
    ----------
    meter : Meter
        Reference to the meter object
    registers : dict[str, Register]
        Dictionary of registers to read, with the register name as key and the register object as value

    Returns
    -------
    dict
        Contains the decoded values, with the same keys as the input dictionary
    """
    assert isinstance(registers, dict)
    await _connect_meter(meter)
    results = {}
    for key, register in registers.items():
        results[key] = await _read_register(meter, register)
    return results


# Public functions for reading data from specific register sets
async def read_phases() -> list[dict]:
    """Reads measurements of all phases from the electric meter.

    Reads the register set ``"phases"`` from the meter ``"electric"``
    defined in the register reference file, so those need to be defined.

    Returns
    -------
    list[dict]
        List of dictionaries of phase readings
    """
    electric = _get_electric()
    phases = []
    for phase_id, phase in electric.registers["phases"].items():
        phases.append(await _read_registers(electric, phase))
    return phases


async def read_avg() -> dict:
    """Reads the average measurements from the electric meter.

    Reads the register set ``"average"`` from the meter ``"electric"``,
    which needs to be defined in the register reference file.

    Returns
    -------
    dict
        Dictionary of average readings
    """
    electric = _get_electric()
    return await _read_registers(electric, electric.registers["average"])


async def read_panel() -> dict:
    """Reads the measurements from the water panel.

    Reads the register set ``"panel"`` from the meter ``"water_panel"``,
    which needs to be defined in the register reference file.

    Returns
    -------
    dict
        Dictionary of water panel readings
    """
    panel = _get_panel()
    return await _read_registers(panel, panel.registers["panel"])


# For testing purposes
def _test_main():
    import asyncio

    electric = _get_electric()
    print(electric)
    print(f'voltage register = {electric.registers["phases"][1]["voltage"].register}')

    res = asyncio.run(read_phases())
    print("Phases:")
    print(res)


if __name__ == "__main__":
    meters = None
    _test_main()
