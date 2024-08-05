from typing import Optional

from pyftdi.i2c import I2cNackError

from replifactory.devices import Device, device_command
from replifactory.drivers import Driver, ThermometerDriver


class Thermometer(Device):
    def __init__(self, driver: ThermometerDriver, name: Optional[str] = None, **kwargs):
        super().__init__(name or "Thermometer", **kwargs)
        self.driver = driver
        self._last_value = 0

    @device_command
    def measure(self):
        self._set_state(self.States.STATE_WORKING)
        value = self.driver.read()
        self._last_value = value
        self._set_state(self.States.STATE_OPERATIONAL)
        return value

    def _test(self):
        return self.driver.read() != 0

    def read_state(self):
        try:
            self.measure()
        except I2cNackError as exc:
            self._log.warning("Not acknowledge (NACK)")
            self._error = str(exc)
            self._set_state(self.States.STATE_ERROR)
        else:
            self._set_state(self.States.STATE_OPERATIONAL)

    def get_data(self):
        data = super().get_data()
        data.update(
            {
                "value": self._last_value,
            }
        )
        return data

    def get_drivers(self) -> list[Driver]:
        return [self.driver]
