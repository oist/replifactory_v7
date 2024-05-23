import logging
import threading
from typing import Optional

from flask_app.replifactory.devices import Device, DeviceCallback
from flask_app.replifactory.drivers.mcp3421 import ADCDriver
from flask_app.replifactory.drivers.pca9555 import REGISTER_OUTPUT_PORT_1, IOPortDriver

global_lock = threading.RLock()
log = logging.getLogger(__name__)


REACTOR_ADC_EN_PIN = 14
I2C_PORT_IO_REACTOR = 0x22


class Photodiode(Device):
    def __init__(
        self,
        diode_cs: int,
        adc_driver: Optional[ADCDriver] = None,
        io_driver: Optional[IOPortDriver] = None,
        lock=global_lock,
        name: str = "Photodiode",
        callback: Optional[DeviceCallback] = None,
    ):
        super().__init__(name or f"Photodiode {diode_cs}", callback)
        self.adc_driver = adc_driver
        self.io_driver = io_driver
        self.diode_cs = diode_cs
        self.lock = lock

    def measure(self, gain: int = 8, bitrate: int = 16) -> tuple[float, float]:
        with self.lock:
            if self.io_driver and self.adc_driver:
                log.debug(f"Measure {self.name} (cs={self.diode_cs})")
                if self.io_driver.port.address == I2C_PORT_IO_REACTOR:
                    log.debug(f"Connect ADC to {self.name}")
                    self.io_driver.write_pin(REACTOR_ADC_EN_PIN, 1)
                    value = self.adc_driver.measure(gain=gain, bitrate=bitrate)
                    log.debug(f"Disconnect ADC from {self.name}")
                    self.io_driver.write_pin(REACTOR_ADC_EN_PIN, 0)
                    return value
                else:
                    self.io_driver.write_to(REGISTER_OUTPUT_PORT_1, [self.diode_cs])
                    return self.adc_driver.measure(gain=gain, bitrate=bitrate)
            return (0.0, 0.0)
