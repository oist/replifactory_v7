from flask_app.replifactory.experiment import Experiment
from flask_app.replifactory.machine import ReactorException, ReactorStates
from flask_app.replifactory.plugins import PluginUiModuleMetadata
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
    name = "Optical Density Measure"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_ui_modules(self):
        return [
            PluginUiModuleMetadata(
                moduleName="od-measure-experiment-description",
                path="od-measure-experiment-description.umd.min.js",
                kind="description",
            ),
            PluginUiModuleMetadata(
                moduleName="od-measure-experiment-parameters",
                path="od-measure-experiment-parameters.umd.min.js",
                kind="parameters",
            ),
            PluginUiModuleMetadata(
                moduleName="od-measure-experiment-dashboard",
                path="od-measure-experiment-dashboard.umd.min.js",
                kind="dashboard",
            ),
        ]
