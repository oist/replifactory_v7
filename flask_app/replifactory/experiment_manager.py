import logging
import threading
from typing import Optional

from flask_app.replifactory.events import Events, eventManager
from flask_app.replifactory.experiment import Experiment, ExperimentCallback
from flask_app.replifactory.machine import BaseMachine
from flask_app.replifactory.machine_manager import machineManager
from flask_app.replifactory.util import get_short_uuid

_instance = None


def experimentManager():
    global _instance
    if _instance is None:
        _instance = ExperimentManager()
    return _instance


class ExperimentManager(ExperimentCallback):

    class NamedExperimentCallback(ExperimentCallback):
        def __init__(self, experiment_id):
            self._experiment_id = experiment_id

        def _on_experiment_status_change(self, state, *args, **kwargs):
            state.update({"experiment_id": self._experiment_id})
            eventManager().fire(Events.EXPERIMENT_STATUS_CHANGE, state)

    def __init__(self):
        self._log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._experiments = {}
        self._lock = threading.RLock()

    def get_states(self):
        with self._lock:
            return {
                experiment_id: experiment.status()
                for experiment_id, (experiment, _) in self._experiments.items()
            }

    def get_state(self, experiment_id: str):
        with self._lock:
            experiment = self._get_experiment(experiment_id)
            if experiment is None:
                raise ValueError(f"Experiment {experiment_id} not found")
            return experiment.status()

    def start_experiment(
        self,
        experiment_class: type[Experiment],
        machine: Optional[BaseMachine] = None,
        *args,
        **kwargs,
    ):
        with self._lock:
            machine = machine or machineManager().get_machine()
            if machine is None:
                raise ValueError("No machine available")
            if not machine.isIdle():
                raise ValueError("Machine is not ready to start experiment")

            while (experiment_id := get_short_uuid()) in self._experiments:
                self._log.debug(
                    f"Generated experiment id {experiment_id} is already in use, generating another one"
                )

            callback = self.NamedExperimentCallback(experiment_id)
            experiment = experiment_class(
                machine=machine,
                experiment_callback=callback,
                id=experiment_id,
                *args,
                **kwargs,
            )

            self._experiments[experiment_id] = (experiment, callback)
            experiment.start()
            self._log.info(
                f"Started experiment {experiment.get_name()} ({experiment_id})"
            )
            return experiment.status()

    def stop_experiment(self, experiment_id: str):
        with self._lock:
            experiment = self._get_experiment(experiment_id)
            if experiment is None:
                raise ValueError(f"Experiment {experiment_id} not found")
            experiment.stop()
            # del self._experiments[experiment_id]
            self._log.info(f"Stopped experiment {experiment_id}")
            return experiment.status()

    def pause_experiment(self, experiment_id: str):
        with self._lock:
            experiment = self._get_experiment(experiment_id)
            if experiment is None:
                raise ValueError(f"Experiment {experiment_id} not found")
            experiment.pause()
            self._log.info(f"Paused experiment {experiment_id}")
            return experiment.status()

    def resume_experiment(self, experiment_id: str):
        with self._lock:
            experiment = self._get_experiment(experiment_id)
            if experiment is None:
                raise ValueError(f"Experiment {experiment_id} not found")
            experiment.resume()
            self._log.info(f"Resumed experiment {experiment_id}")
            return experiment.status()

    def _get_experiment(self, experiment_id: str) -> Experiment:
        experiment, _ = self._experiments.get(experiment_id, None)
        return experiment
