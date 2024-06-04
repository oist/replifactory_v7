import logging
import time
from enum import Enum
from typing import Optional

from flask_app.replifactory.devices import Device, DeviceCallback
from flask_app.replifactory.drivers.pca9555 import IOPortDriver

LASER_ON = 0
LASER_OFF = 1

REACTOR_LASER_EN_PIN = 15
I2C_PORT_IO_REACTOR = 0x22

log = logging.getLogger(__name__)


class Laser(Device):
    class States(Device.States, Enum):
        STATE_ON = 121
        STATE_OFF = 122

    def __init__(
        self,
        laser_cs: int,
        io_driver: IOPortDriver,
        name: Optional[str] = None,
        callback: Optional[DeviceCallback] = None,
    ):
        super().__init__(name or f"Laser {laser_cs}", callback)
        self.laser_cs = laser_cs
        self.io_driver = io_driver

    def read_state(self):
        self._set_state(self.States.STATE_OPERATIONAL)

    def switch_on(self):
        log.debug(f"{self.name} switch ON")
        if self.io_driver.port.address == I2C_PORT_IO_REACTOR:
            self.io_driver.write_pin(REACTOR_LASER_EN_PIN, 1)
        else:
            self.io_driver.write_pin(self.laser_cs, LASER_ON)
        self._set_state(self.States.STATE_ON)

    def switch_off(self):
        log.debug(f"{self.name} switch OFF")
        if self.io_driver.port.address == I2C_PORT_IO_REACTOR:
            self.io_driver.write_pin(REACTOR_LASER_EN_PIN, 0)
        else:
            self.io_driver.write_pin(self.laser_cs, LASER_OFF)
        self._set_state(self.States.STATE_OFF)

    def blink(self, times: int = 3, freq: float = 3):
        log.debug(f"{self.name} blink {times} times with freq: {freq} Hz")
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
