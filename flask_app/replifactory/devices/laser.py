import logging
import time

from replifactory.devices import Device
from replifactory.drivers.pca9555 import IOPortDriver

LASER_ON = 0
LASER_OFF = 1


log = logging.getLogger(__name__)


class Laser(Device):
    def __init__(self, laser_cs: int, io_driver: IOPortDriver):
        self.laser_cs = laser_cs
        self.io_driver = io_driver

    def configure(self):
        pass

    def switch_on(self):
        log.debug(f"Laser {self.laser_cs} switch ON")
        self.io_driver.write_pin(self.laser_cs, LASER_ON)

    def switch_off(self):
        log.debug(f"Laser {self.laser_cs} switch OFF")
        self.io_driver.write_pin(self.laser_cs, LASER_OFF)

    def blink(self, times: int = 3, freq: float = 3):
        log.debug(f"Laser {self.laser_cs} blink {times} times with freq: {freq} Hz")
        delay = 1 / (freq * 2)
        for i in range(times):
            self.switch_on()
            time.sleep(delay)
            self.switch_off()

    def __enter__(self):
        self.switch_on()
        return self

    def __exit__(self, *args):
        self.switch_off()
