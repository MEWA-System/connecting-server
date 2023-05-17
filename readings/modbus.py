from pymodbus import client as mbc, payload as mbp
import yaml
from data_classes import Meter, Register
from typing import Optional


global data
electric: Optional[Meter] = None

# klient dla każdego urządzenia


async def init():
    load_register_reference()
    # stwórz klienta dla każdego urządzenia


def load_register_reference():
    with open("modbus_registers.yaml", "r") as stream:
        try:
            global data, electric
            data = yaml.safe_load(stream)
            electric = data["electric_meter"]
        except yaml.YAMLError as ex:
            print(ex)


async def _modbus_test(phase: int):
    global electric
    assert electric is not None
    client = mbc.AsyncModbusTcpClient(electric.id.ip_address, electric.id.tcp_socket)
    await client.connect()
    response = await client.read_input_registers(electric.registers["phases"][phase]["voltage"].register, 1, electric.id.slave_id)
    print(response)

    await client.close()


async def read(target) -> dict:
    pass


async def _read_register(client, register: Register):
    response = await client.read_input_registers(register.register, 1, electric.id.slave_id)
    decoder = mbp.BinaryPayloadDecoder.fromRegisters(response.registers)
    if register.type == "float":
        return decoder.decode_32bit_float()


import asyncio

if __name__ == "__main__":
    load_register_reference()
    #assert electric_meter is not None
    print(electric)
    print(f'voltage register = {electric.registers["phases"][1]["voltage"].register}')

    asyncio.run(_modbus_test(1))
