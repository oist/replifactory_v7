import time

from biofactory.devices import Device
from biofactory.devices.stirrer import Stirrer
from biofactory.drivers import Driver


class StirrersGroup(Device):
    def __init__(self, stirrers: list[Stirrer], name: str = "Stirrers Group"):
        super().__init__(name)
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
            self.stop_all()
            return True
        except Exception as e:
            self._log.exception(e)
            return False

    def get_drivers(self) -> list[Driver]:
        return [stirrer.driver for stirrer in self._stirrers]
