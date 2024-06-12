from dataclasses import dataclass
from datetime import datetime
import logging
from flask_app.replifactory.experiment import Experiment
from flask_app.replifactory.machine import Reactor, ReactorException, ReactorStates


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

    def __init__(self, reactors: list[Reactor], **kwargs):
        super().__init__()
        self._reactors = reactors
        self._params = EndlessGrowthParams(**kwargs)
        self._log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._start_growth_time = {}

    def run(self, *args, **kwargs):
        for reactor in self._reactors:
            self._reset_growth_timeout(reactor)
        return super().run(*args, **kwargs)

    def warmup(self):
        for reactor in self._reactors:
            reactor.home()

    def routine(self):
        for reactor in self._reactors:
            if reactor.state != ReactorStates.READY:
                self._log.warning(f"Reactor {reactor} is not ready")
                continue
            try:
                current_od = reactor.cmd("measure_od")
                if current_od < self._params.od_dilution_threshold:
                    continue
                self._reset_growth_timeout(reactor)
                reactor.cmd(
                    "dilute_to_od",
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
