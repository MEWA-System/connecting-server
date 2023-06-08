import asyncio

from db_functions import ingest, ingest_phases
from modbus import read_phases, read_avg, read_panel
from data_classes import DataTemplates, is_correct_to_template


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
