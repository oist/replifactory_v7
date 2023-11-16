import logging
import threading

from flask_app.replifactory.devices import Device
from flask_app.replifactory.drivers.mcp3421 import ADCDriver
from flask_app.replifactory.drivers.pca9555 import REGISTER_OUTPUT_PORT_1, IOPortDriver

global_lock = threading.RLock()
log = logging.getLogger(__name__)


class Photodiode(Device):
    def __init__(
        self,
        diode_cs: int,
        adc_driver: ADCDriver = None,
        io_driver: IOPortDriver = None,
        lock=global_lock,
        name: str = "Photodiode",
    ):
        self.adc_driver = adc_driver
        self.io_driver = io_driver
        self.diode_cs = diode_cs
        self.lock = lock
        self._name = name

    def measure(self, gain: int = 8, bitrate: int = 16) -> tuple[float, float]:
        with self.lock:
            log.debug(f"Measure {self.name} (cs={self.diode_cs})")
            self.io_driver.write_to(REGISTER_OUTPUT_PORT_1, [self.diode_cs])
            return self.adc_driver.measure(gain=gain, bitrate=bitrate)
