import logging
import time
from flask_app.replifactory.devices import Device
from flask_app.replifactory.devices.stirrer import Stirrer
from flask_app.replifactory.drivers import Driver


class StirrersGroup(Device):
    def __init__(self, stirrers: list[Stirrer], name: str = "Stirrers Group"):
        super().__init__(name)
        self.log = logging.getLogger(__name__)
        self._stirrers = stirrers

    def read_state(self):
        pass

    def __getitem__(self, key) -> Stirrer:
        return self._stirrers[key]

    # def __setitem__(self, key: int, value: bool):
    #     self._stirrers[key].set_speed()

    def run_all(self, speed):
        for stirrer in self._stirrers:
            stirrer.set_speed(speed)

    def stop_all(self):
        for stirrer in self._stirrers:
            stirrer.set_speed(0.0)

    def test(self):
        try:
            self.run_all(0.2)
            time.sleep(2)
            self.stop_all(0.0)
            return True
        except Exception as e:
            self.log.exception(e)
            return False

    def get_drivers(self) -> list[Driver]:
        return [stirrer.driver for stirrer in self._stirrers]
