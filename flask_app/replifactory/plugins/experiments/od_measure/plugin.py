from flask_app.replifactory.experiment import Experiment
from flask_app.replifactory.machine import ReactorException, ReactorStates
from flask_app.replifactory.plugins.experiments import ExperimentPlugin


def init_plugin(app):
    return ODMeasureExperimentPlugin()


class ODMeasureExperiment(Experiment):
    name = "Optical Density Measure"

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


class ODMeasureExperimentPlugin(ExperimentPlugin):
    experiment_class = ODMeasureExperiment

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_frontend_modules(self):
        return [{"name": "parameters", "path": f"/static/{self.name}/od-measure-replyfactory-plugin.5b25b8e62e64f558.umd.min.js"}]
