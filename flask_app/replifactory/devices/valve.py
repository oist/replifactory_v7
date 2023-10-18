import logging
import math
import time
from typing import Optional

from replifactory.devices import Device
from replifactory.drivers.pca9685 import PWMDriver


class Valve(Device):
    def __init__(
        self,
        pwm_channel: int,
        driver: PWMDriver,
        open_duty_cycle: float = 0.0,
        closed_duty_cycle: float = 1.0,
        change_state_delay: float = 2.0,
        name: Optional[str] = None,
    ):
        super().__init__(name or f"Valve {pwm_channel}")
        self.log = logging.getLogger(__name__)
        self.driver = driver
        self.pwm_channel = pwm_channel
        self.open_duty_cycle = open_duty_cycle
        self.closed_duty_cycle = closed_duty_cycle
        self.change_state_delay = change_state_delay
        self._is_open = None

    @property
    def is_close(self) -> bool:
        return self.is_open is False

    @property
    def is_open(self) -> bool | None:
        if self._is_open is None:
            return self.update_state()
        return self._is_open

    @is_open.setter
    def is_open(self, value: bool):
        self.set_state(value)

    def open(self, wait: bool = True) -> None:
        self.driver.set_duty_cycle(self.pwm_channel, self.open_duty_cycle)
        if wait:
            time.sleep(self.change_state_delay)
        self._is_open = True

    def close(self, wait: bool = True) -> None:
        self.driver.set_duty_cycle(self.pwm_channel, self.closed_duty_cycle)
        if wait:
            time.sleep(self.change_state_delay)
        self._is_open = False

    def set_state(self, open: bool = False, wait: bool = True) -> None:
        if open is False:
            self.close(wait)
        else:
            self.open(wait)

    def update_state(self) -> bool | None:
        duty_cycle = self.driver.get_duty_cycle(self.pwm_channel)
        if math.isclose(duty_cycle, self.open_duty_cycle, rel_tol=1e-3):
            self._is_open = True
        elif math.isclose(duty_cycle, self.closed_duty_cycle, rel_tol=1e-3):
            self._is_open = False
        else:
            self._is_open = None
        return self._is_open

    def test(self):
        try:
            self.open()
            self.close()
            self.open()
            return True
        except Exception as e:
            self.log.exception(e)
            return False
