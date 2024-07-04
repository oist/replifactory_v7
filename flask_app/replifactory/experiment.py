import logging
import threading
import time
from datetime import datetime, timezone
from enum import Enum
from threading import Thread
from typing import Optional

from flask_app.replifactory.events import Events, eventManager
from flask_app.replifactory.machine import BaseMachine
from flask_app.replifactory.util.module_loading import import_string


class ExperimentStatuses(str, Enum):
    READY = "ready"
    STARTING = "starting"
    RESTORING = "restoring"
    RUNING = "runing"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    DONE = "done"
    FAILED = "failed"


class ExperimentCallback():
    def _on_experiment_status_change(self, status, *args, **kwargs):
        pass


class Experiment:
    """Base class to create experiment"""
    name = "Experiment"

    def __init__(self, machine: BaseMachine, experiment_callback: Optional[ExperimentCallback] = None,  *args, **kwargs):
        self._machine = machine
        self._thread = None
        self._abort = False
        self._startTime = None
        self._cycles = 0
        self._cycleTime = 60.0
        self._warmupEnabled = True
        self._lock = threading.RLock()
        self._status = ExperimentStatuses.READY
        self._experiment_callback = experiment_callback or ExperimentCallback()
        self._log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @classmethod
    def get_name(cls):
        return cls.name

    def status(self):
        return {
            "name": self.get_name(),
            "startTime": self._startTime,
            "cycles": self._cycles,
            "cycleTime": self._cycleTime,
            "warmupEnabled": self._warmupEnabled,
            "running": self._thread is not None,
            "abort": self._abort,
            "status": self._status,
        }

    def start(self):
        with self._lock:
            if self._thread is not None:
                raise Exception("Experiment is already running")
            self._log.info("Starting experiment")
            self._set_status(ExperimentStatuses.STARTING)
            self._startTime = datetime.now(timezone.utc)
            self._thread = Thread(target=self._experiment_loop, args=({},), daemon=True)
            eventManager().fire(Events.EXPERIMENT_STARTED, payload={"time": self._startTime})
            self._thread.start()

    def restore(self, cycle_num: int):
        """Run main cycle without warming up"""
        with self._lock:
            if self._thread is not None:
                raise Exception("Experiment is already running")
            self._set_status(ExperimentStatuses.RESTORING)
            self._cycles = cycle_num
            self._warmupEnabled = False
            self._thread = Thread(target=self._experiment_loop, args=({},), daemon=True)
            eventManager().fire(Events.EXPERIMENT_RESTORED, payload={"time": datetime.now(timezone.utc)})
            self._thread.start()

    def stop(self):
        with self._lock:
            if self._thread is not None and self._abort is False:
                self._set_status(ExperimentStatuses.CANCELLING)
                aborting_thread = self._thread

                def wait_and_fire():
                    aborting_thread.join()
                    self._status = ExperimentStatuses.CANCELLED
                    eventManager().fire(Events.EXPERIMENT_CANCELLED, payload={"time": datetime.now(timezone.utc)})
                    self._log.info("Experiment cancelled")

                self._abort = True
                eventManager().fire(Events.EXPERIMENT_CANCELLING, payload={"time": datetime.now(timezone.utc)})
                Thread(target=wait_and_fire, daemon=True).start()

                self._machine.cancel_long_operation()

    def pause(self):
        pass

    def resume(self):
        pass

    def _experiment_loop(self, *args, **kwargs):
        self._set_status(ExperimentStatuses.RUNING)
        if self._warmupEnabled:
            self.warmup()
        while self._abort is False:
            start_cycle_time = datetime.now()
            self._cycles += 1
            self._log.info(f"Cycle {self._cycles} started")
            eventManager().fire(Events.EXPERIMENT_NEW_CYCLE, payload={"time": start_cycle_time, "cycle": self._cycles})
            routine_result = self.routine()
            routine_result = routine_result if routine_result else {}
            error_happend, error_message = self.error_condition(**routine_result)
            if error_happend:
                eventManager().fire(Events.EXPERIMENT_FAILED, payload={"time": datetime.now(timezone.utc), "message": error_message})
                self._set_status(ExperimentStatuses.FAILED)
                break
            if self.success_condition(**routine_result):
                break
            end_cycle_time = datetime.now()
            elapsed_time = end_cycle_time - start_cycle_time
            sleep_time = self._cycleTime - elapsed_time.total_seconds()
            if sleep_time < 0:
                eventManager().fire(Events.EXPERIMENT_CYCLE_TOO_LONG_WARNING, payload={"time": end_cycle_time, "cycle": self._cycles, "elapsed_time": elapsed_time})
            else:
                time.sleep(sleep_time)
            eventManager().fire(Events.EXPERIMENT_CYCLE_COMPLETE, payload={"time": datetime.now(timezone.utc), "cycle": self._cycles})

        self.cooldown()
        eventManager().fire(Events.EXPERIMENT_DONE, payload={"time": datetime.now(timezone.utc)})
        if self._status != ExperimentStatuses.FAILED:
            self._set_status(ExperimentStatuses.DONE)
        self._thread = None
        self._log.info("Experiment loop end")

    def routine(self):
        return {}

    def success_condition(self, **kawrgs):
        return self._abort or self._cycles > 10

    def error_condition(self, **kwargs):
        return (False, 'No errors')

    def warmup(self):
        pass

    def cooldown(self):
        pass

    def compatible(self, reactor):
        """Check if the experiment is compatible with the given reactor"""
        return True

    def _set_status(self, status: ExperimentStatuses):
        self._status = status
        self._experiment_callback._on_experiment_status_change(self.status())


class ExperimentRegistry:

    def __init__(self):
        self._experiments = {}

    def register(self, experiment):
        key = f"{experiment.__module__}.{experiment.__name__}"
        self._experiments[key] = experiment

    def get(self, name):
        return self._experiments.get(name)

    def list(self):
        return {id: experiment.get_name() for id, experiment in self._experiments.items()}


experimentRegistry = ExperimentRegistry()


def register_experiment(registerable: type[Experiment] | str):
    if isinstance(registerable, str):
        registerable = import_string(registerable)
    experimentRegistry.register(registerable)
    return registerable
