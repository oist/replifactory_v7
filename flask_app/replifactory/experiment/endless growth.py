

from flask_app.replifactory.experiment import Experiment
from flask_app.replifactory.machine import Reactor


ENDLESS_GROWTH_PARAMS = {
    "od_dilution_threshold": 0.8,
    "dilution_target_od": 0.3,
    "dilution_volume": 1,  # in mL
    "growth_timeout": 60 * 4,  # in minutes
}


class EndlessGrowthExperiment(Experiment):

    def __init__(self, reactors: list[Reactor]):
        super().__init__()
        self._reactors = reactors

    def warmup(self):
        for reactor in self._reactors:
            reactor.home()

    def routine(self):
        for reactor in self._reactors:
            reactor.cmd_measure_od()

    def cooldown(self):
        for reactor in self._reactors:
            reactor.home()