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

from config.config_loading import load_config, ConfigNotFound
from readings.reading_execution import measure_and_save_avg, measure_and_save_panel, measure_and_save_phases


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


jobs: dict[str, Optional[Job]] = {
    "phases": None,
    "avg": None,
    "panel": None,
}


def init_jobs():
    """Initializes the jobs with the intervals specified in the config file.

    Intervals can be configured in the /config/config.ini file: ::

        [reading_intervals]
        job_name = # Interval in seconds

    Defaults to 15 minutes if an interval is not specified.

    The jobs are:
        - ``"phases"``: ``measure_and_save_phases``
        - ``"avg"``: ``measure_and_save_avg``
        - ``"panel"``: ``measure_and_save_panel``

    """
    try:
        intervals = load_config(section="reading_intervals")
    except ConfigNotFound:
        print("Interval config not found, using default values of 15 minutes")
        intervals = {}

    jobs["phases"] = Job(timedelta(seconds=int(intervals.get("phases", 15 * 60))), measure_and_save_phases)
    jobs["avg"] = Job(timedelta(seconds=int(intervals.get("avg", 15 * 60))), measure_and_save_avg)
    jobs["panel"] = Job(timedelta(seconds=int(intervals.get("panel", 15 * 60))), measure_and_save_panel)


def start_jobs():
    """Starts all the jobs.

    If the jobs have not been initialized, ``init_jobs()`` is run.

    """
    if any(job is None for job in jobs.values()):
        init_jobs()
    for job in jobs.values():
        job.start()


# For only running the scheduler
if __name__ == "__main__":
    start_jobs()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            for job in jobs.values():
                job.stop()
            break
