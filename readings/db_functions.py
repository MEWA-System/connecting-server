"""Module for ingesting data into QuestDB.

Requires a configuration file in the config folder with the following format: ::

    [questdb_influx]
    host = # IP address of the QuestDB server
    port = # Port of the QuestDB's InfluxDB line protocol

"""
import sys
from typing import Optional

from questdb.ingress import Sender, IngressError, TimestampMicros

from config.config_loading import load_config

# Global variables
config = None


def ingest(table: str, reading: dict[str, any],
           timestamp=TimestampMicros.now(),
           symbols: Optional[dict[str, str]] = None):
    """Ingests data from a reading into QuestDB.

    Verifying that the data has the format correct to the table is the responsibility of the caller.

    Parameters
    ----------
    table : str
        The table to ingest the data into.
    reading : dict[str, any]
        The data to ingest. The keys are expected to be the column names.
    timestamp : TimestampMicros, optional
        The timestamp to use for the data. Defaults to the current time.
    symbols : dict[str, str], optional
        The symbols to categorize the data by. Defaults to None.

    Examples
    --------
    Simple ingest:

    >>> ingest("ambient", {"temperature": 20, "humidity": 50})

    Ingest simultaneusly taken data from a dictionary, categorized by the key:

    >>> ts = TimestampMicros.now()
    >>> for room, reading in rooms.values():
    >>>     ingest("ambient", reading, timestamp=ts, symbols={"location": room})


    """
    if symbols is None:
        symbols = {}
    global config
    if config is None:
        config = load_config(section="questdb_influx")
    try:
        with Sender(**config) as sender:
            print(reading)
            sender.row(
                table,
                symbols=symbols,
                columns={
                    "ts": timestamp,
                    **reading,
                },
            )
            sender.flush()
    except IngressError as e:
        sys.stderr.write(f"Failed to send data to QuestDB: {e}\n")


def ingest_phases(phases: list[dict[str, any]]):
    """Ingests a list of specifically phase readings into QuestDB.
    """
    i = 1
    ts = TimestampMicros.now()
    for phase in phases:
        ingest("phase", phase, timestamp=ts, symbols={"phase": str(i)})
        i += 1
