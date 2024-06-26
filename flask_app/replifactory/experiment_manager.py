import logging
import threading
from typing import Optional
from flask_app.replifactory.experiment import experimentRegistry
from flask_app.replifactory.machine import BaseMachine
from flask_app.replifactory.machine_manager import machineManager


_instance = None


def experimentManager():
    global _instance
    if _instance is None:
        _instance = ExperimentManager()
    return _instance


class ExperimentManager():

    def __init__(self):
        self._log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._experiments = {}
        self._lock = threading.RLock()

    def start_experiment(self, experiment_id: str, machine: Optional[BaseMachine] = None, *args, **kwargs):
        with self._lock:
            experiment_class = experimentRegistry.get(experiment_id)
            if experiment_class is None:
                raise ValueError(f"Experiment class {experiment_id} not found")
            if experiment_id in self._experiments:
                raise ValueError(f"Experiment {experiment_id} already running")
            machine = machine or machineManager().get_machine()
            if machine is None:
                raise ValueError("No machine available")
            if not machine.isIdle():
                raise ValueError("Machine is not ready to start experiment")

            experiment = experiment_class(machine=machine, *args, **kwargs)
            self._experiments[experiment_id] = experiment
            experiment.start()
            self._log.info(f"Started experiment {experiment_id}")
            return experiment.status()

    def stop_experiment(self, experiment_id: str):
        with self._lock:
            experiment = self._experiments.get(experiment_id)
            if experiment is None:
                raise ValueError(f"Experiment {experiment_id} not found")
            experiment.stop()
            del self._experiments[experiment_id]
            self._log.info(f"Stopped experiment {experiment_id}")
            return experiment.status()

    def pause_experiment(self, experiment_id: str):
        with self._lock:
            experiment = self._experiments.get(experiment_id)
            if experiment is None:
                raise ValueError(f"Experiment {experiment_id} not found")
            experiment.pause()
            self._log.info(f"Paused experiment {experiment_id}")
            return experiment.status()

    def resume_experiment(self, experiment_id: str):
        with self._lock:
            experiment = self._experiments.get(experiment_id)
            if experiment is None:
                raise ValueError(f"Experiment {experiment_id} not found")
            experiment.resume()
            self._log.info(f"Resumed experiment {experiment_id}")
            return experiment.status()
