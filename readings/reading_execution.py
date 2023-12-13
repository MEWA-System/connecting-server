"""Module containing functions for taking and saving specific readings.

"""
import asyncio

from readings.db_functions import ingest, ingest_phases
from readings.modbus import read_registers, read_phases, read_avg, read_panel
from readings.data_classes import Meter, Table, Register, DataTemplates, is_correct_to_template


# Old hardcoded functions
def measure_and_save_phases():
    phases = asyncio.run(read_phases())
    for phase in phases:
        assert is_correct_to_template(phase, DataTemplates.PHASE)
    ingest_phases(phases)


def measure_and_save_avg():
    avg = asyncio.run(read_avg())
    assert is_correct_to_template(avg, DataTemplates.AVG)
    ingest("electric_avg", avg)


def measure_and_save_panel():
    panel = asyncio.run(read_panel())
    assert is_correct_to_template(panel, DataTemplates.PANEL)
    ingest("panel", panel)


# The proper generic API
def measure_and_save(table: Table, table_name: str, meters: dict[str, Meter]):
    """Takes a reading from a meter and saves it to the database.

    Parameters
    ----------
    table : Table
        Table to save the reading to
    table_name : str
        Name of the table (necessary, because Table can't easily get the name from the key it's stored in)
    meters : dict[str, Meter]
        Dictionary of meters to take the reading from

    """
    match table.type:  # Yes, I'm using match-case in Python. Yes, I'm a C++ programmer.
        case Table.Types.SIMPLE:
            # Verify that values of table.fields are Register objects
            if not all(isinstance(field, Register) for field in table.fields.values()):
                raise TypeError("Simple table fields must be Register objects")

            data = asyncio.run(read_registers(meters, table.fields))
            ingest(table_name, data)
        case Table.Types.SYMBOLIC:
            # Verify that values of table.fields are dicts of Register objects
            if not all(isinstance(fields, dict) for fields in table.fields.values()):
                raise TypeError("Symbolic table fields must be dicts of Register objects")

            for symbol, fields in table.fields.items():
                data = asyncio.run(read_registers(meters, fields))
                ingest(table_name, data, symbols={table.symbol_field: symbol})
        case _:
            raise ValueError(f"Table type {table.type} not recognized")
