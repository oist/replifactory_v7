from flask_app.replifactory.experiment import Experiment
from flask_app.replifactory.machine import ReactorException, ReactorStates


class ODMeasureExperiment(Experiment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reactors = self._machine.get_reactors()

    def warmup(self):
        for reactor in self._reactors:
            reactor.home()

    def routine(self):
        for reactor in self._reactors:
            if self._abort:
                return
            if reactor.state != ReactorStates.READY:
                self._log.warning(f"Reactor {reactor} is not ready")
                continue
            try:
                reactor.cmd("measure_od")
            except ReactorException as e:
                return {"error": e}

    def cooldown(self):
        for reactor in self._reactors:
            reactor.home()
