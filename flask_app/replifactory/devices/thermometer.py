from typing import Optional

from replifactory.devices import Device
from replifactory.drivers.adt75 import ThermometerDriver


class Thermometer(Device):
    def __init__(self, driver: ThermometerDriver, name: Optional[str] = None):
        super().__init__(name or f"Thermometer 0x{driver.port.address:02X}")
        self.driver = driver

    def measure(self):
        return self.driver.measure_one_shot()

    def test(self):
        return self.driver.measure_one_shot() != 0
