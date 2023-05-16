from pymodbus import client as mbc
import yaml
from data_classes import Meter
from typing import Optional


global data
electric: Optional[Meter] = None


def load_register_reference():
    with open("modbus_registers.yaml", "r") as stream:
        try:
            global data, electric
            data = yaml.safe_load(stream)
            electric = data["electric_meter"]
        except yaml.YAMLError as ex:
            print(ex)


async def read_phase(phase: int):
    global electric
    assert electric is not None
    client = mbc.AsyncModbusTcpClient(electric.id.ip_address, electric.id.tcp_socket)
    await client.connect()
    response = await client.read_input_registers(electric.registers["phases"][phase]["voltage"], 1, electric.id.slave_id)
    print(response)

    await client.close()


import asyncio

if __name__ == "__main__":
    load_register_reference()
    #assert electric_meter is not None
    print(electric)
    print(f'voltage register = {electric.registers["phases"][1]["voltage"]}')

    asyncio.run(read_phase(1))
