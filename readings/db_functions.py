import sys
from typing import Optional

from questdb.ingress import Sender, IngressError, TimestampMicros

from config.config_loading import load_config

# Global variables
config = None


def ingest(table: str, reading: dict[str, any],
           timestamp=TimestampMicros.now(),
           symbols: Optional[dict[str, str]] = None):
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
    i = 1
    ts = TimestampMicros.now()
    for phase in phases:
        ingest("phase", phase, timestamp=ts, symbols={"phase": str(i)})
        i += 1
