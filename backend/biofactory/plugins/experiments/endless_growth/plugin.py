from dataclasses import dataclass, fields
from datetime import datetime

from biofactory.experiment import Experiment
from biofactory.machine import ReactorException, ReactorStates
from biofactory.plugins import PluginUiModuleMetadata
from biofactory.plugins.experiments import ExperimentPlugin


def init_plugin(*args, **kwargs):
    return EndlessGrowthExperimentPlugin()
    # return ExperimentPlugin(EndlessGrowthExperiment, name="Endless Growth Plugin", frontend_modules=[
    #     {"name": "endlessGrowth", "url": "/static/plugins/endless_growth.js"}
    # ])


@dataclass(frozen=True)
class EndlessGrowthParams:
    od_dilution_threshold = 0.8
    dilution_target_od = 0.3
    dilution_volume = 1.0  # in mL
    growth_timeout = 60 * 4  # in minutes


class EndlessGrowthExperiment(Experiment):
    """Measure optical density and dilute if value more that threshold until it reaches target value.
    Abort with arror if growth timeout is reached.
    """

    name = "Endless Growth"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reactors = self._machine.get_reactors()
        valid_keys = {field.name for field in fields(EndlessGrowthParams)}
        filtered_kwargs = {
            key: value for key, value in kwargs.items() if key in valid_keys
        }
        self._params = EndlessGrowthParams(**filtered_kwargs)
        self._start_growth_time = {}

    def _experiment_loop(self, *args, **kwargs):
        for reactor in self._reactors:
            self._reset_growth_timeout(reactor)
        return super()._experiment_loop(*args, **kwargs)

    def warmup(self):
        for reactor in self._reactors:
            reactor.home()

    def routine(self):
        for reactor in self._reactors:
            if self.is_interrupted():
                return
            if reactor.state != ReactorStates.READY:
                self._log.warning(f"Reactor {reactor} is not ready")
                continue
            try:
                current_od = reactor.cmd("measure_od")
                if current_od < self._params.od_dilution_threshold:
                    continue
                self._reset_growth_timeout(reactor)
                reactor.cmd(
                    "dilute",
                    self._params.dilution_target_od,
                    self._params.dilution_volume,
                )
                self._reset_growth_timeout(reactor)
            except ReactorException as e:
                return {"error": e}

    def error_condition(self):
        return super().error_condition()

    def cooldown(self):
        for reactor in self._reactors:
            reactor.home()

    def _reset_growth_timeout(self, reactor):
        self._start_growth_time[str(reactor)] = datetime.now()


class EndlessGrowthExperimentPlugin(ExperimentPlugin):
    experiment_class = EndlessGrowthExperiment
    name = "Endless Growth Experiment"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_ui_modules(self):
        return [
            PluginUiModuleMetadata(
                moduleName="endless-growth-experiment-description",
                path="endless-growth-experiment-description.umd.cjs",
                kind="description",
            ),
            PluginUiModuleMetadata(
                moduleName="endless-growth-experiment-parameters",
                path="endless-growth-experiment-parameters.umd.cjs",
                kind="parameters",
            ),
            PluginUiModuleMetadata(
                moduleName="endless-growth-experiment-dashboard",
                path="endless-growth-experiment-dashboard.umd.cjs",
                kind="dashboard",
            ),
        ]
