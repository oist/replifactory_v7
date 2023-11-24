from typing import Optional

from pyftdi.i2c import I2cNackError

from flask_app.replifactory.devices import Device
from flask_app.replifactory.drivers.adt75 import ThermometerDriver


class Thermometer(Device):
    def __init__(self, driver: ThermometerDriver, name: Optional[str] = None, **kwargs):
        super().__init__(name or f"Thermometer 0x{driver.port.address:02X}", **kwargs)
        self.driver = driver
        self._last_value = 0

    def measure(self):
        value = self.driver.measure_one_shot()
        self._last_value = value
        return value

    def _test(self):
        return self.driver.measure_one_shot() != 0

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
