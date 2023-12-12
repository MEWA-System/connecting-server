"""Module for scheduling of taking readings.

It can be run as a standalone script, which launches jobs for all implemented meters,
or imported and used in another script.

The working directory must be the root of the project (one folder up) for the script to work.

If not specified, the default interval is 15 minutes.

"""
import threading
import time
from datetime import timedelta
from typing import Optional

from config.config_loading import load_config, ConfigNotFound, load_yaml_config
from readings.reading_execution import measure_and_save


# Base source: https://medium.com/greedygame-engineering/an-elegant-way-to-run-periodic-tasks-in-python-61b7c477b679
class Job(threading.Thread):
    """A job that runs periodically.

    Attributes
    ----------
    interval : timedelta
        The interval between executions.
    execute : function
        The function to execute periodically.
    args : list
        The arguments to pass to the function.
    kwargs : dict
        The keyword arguments to pass to the function.


    """
    def __init__(self, interval, execute, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs

    def stop(self):
        self.stopped.set()
        self.join()

    def run(self):
        """Starts the job.

        Function in field ``execute`` will now be executed periodically, according to the interval.

        """
        while not self.stopped.wait(self.interval.total_seconds()):
            self.execute(*self.args, **self.kwargs)


jobs: dict[str, Optional[Job]] = {}


def init_jobs():
    """Initializes the jobs with the intervals specified in the config file.

    Intervals can be configured in the /config/config.ini file: ::

        [reading_intervals]
        job_name = # Interval in seconds

    Defaults to 15 minutes if an interval is not specified.

    The jobs are readings of tables loaded from the register reference file.

    """
    # TODO: Move intervals to yaml config
    try:
        intervals = load_config(section="reading_intervals")
        for name, interval in intervals.items():
            intervals[name] = int(interval)
    except ConfigNotFound:
        print("Interval config not found, using default values of 15 minutes")
        intervals = {}

    global jobs

    meters, tables = load_yaml_config()
    for name, table in tables.items():
        jobs[name] = Job(
            interval=timedelta(seconds=intervals.get(name, 15 * 60)),
            execute=measure_and_save,
            # kwargs passed to measure_and_save
            table=table,
            table_name=name,
            meters=meters,
        )


def start_jobs():
    """Starts all the jobs.

    If the jobs have not been initialized, ``init_jobs()`` is run.

    """
    if not jobs or any(job is None for job in jobs.values()):
        init_jobs()
    for job in jobs.values():
        job.start()


def _main():
    """Main function for running the scheduler as a standalone script.

    """
    start_jobs()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            for job in jobs.values():
                job.stop()
            break


# For only running the scheduler
if __name__ == "__main__":
    _main()
