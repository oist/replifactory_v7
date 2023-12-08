import logging
import math
import time
from enum import Enum
from typing import Literal, Optional

from flask_app.replifactory.devices import Device, DeviceCallback
from flask_app.replifactory.drivers.pca9685 import PWMDriver


class Valve(Device):
    class States(Device.States, Enum):
        STATE_OPENING = 101
        STATE_OPEN = 102
        STATE_CLOSING = 103
        STATE_CLOSE = 104
        STATE_BEETWEEN = 105

    POSITION_STATE = [
        States.STATE_OPEN,
        States.STATE_CLOSE,
        States.STATE_BEETWEEN,
    ]

    def __init__(
        self,
        pwm_channel: int,
        driver: PWMDriver,
        open_duty_cycle: float = 0.0,
        closed_duty_cycle: float = 1.0,
        change_state_delay: float = 2.0,
        name: Optional[str] = None,
        init_state: Optional[Literal[States.STATE_OPEN, States.STATE_CLOSE]] = None,
        callback: Optional[DeviceCallback] = None,
    ):
        super().__init__(name or f"Valve {pwm_channel}", callback)
        self._log = logging.getLogger(__name__)
        self._driver = driver
        self._pwm_channel = pwm_channel
        self._open_duty_cycle = open_duty_cycle
        self._closed_duty_cycle = closed_duty_cycle
        self._change_state_delay = change_state_delay
        self._state = init_state

    def reset(self):
        if self._state == self.States.STATE_OPEN:
            self.open()
        elif self._state == self.States.STATE_CLOSE:
            self.close()

    @property
    def is_close(self) -> bool:
        if self._state not in self.POSITION_STATE:
            self.read_state()
        return self._state == self.States.STATE_CLOSE

    @property
    def is_open(self) -> bool | None:
        if self._state not in self.POSITION_STATE:
            self.read_state()
        return self._state == self.States.STATE_OPEN

    def open(self, wait: bool = True) -> None:
        self._set_state(self.States.STATE_OPENING)
        self._driver.set_duty_cycle(self._pwm_channel, self._open_duty_cycle)
        if wait:
            time.sleep(self._change_state_delay)
        self._is_open = True
        self._set_state(self.States.STATE_OPEN)

    def close(self, wait: bool = True) -> None:
        self._set_state(self.States.STATE_CLOSING)
        self._driver.set_duty_cycle(self._pwm_channel, self._closed_duty_cycle)
        if wait:
            time.sleep(self._change_state_delay)
        self._is_open = False
        self._set_state(self.States.STATE_CLOSE)

    def set_state(self, open: bool = False, wait: bool = True) -> None:
        if open is False:
            self.close(wait)
        else:
            self.open(wait)

    def read_state(self) -> bool | None:
        duty_cycle = self._driver.get_duty_cycle(self._pwm_channel)
        if math.isclose(duty_cycle, self._open_duty_cycle, rel_tol=5e-3):
            self._set_state(self.States.STATE_OPEN)
        elif math.isclose(duty_cycle, self._closed_duty_cycle, rel_tol=5e-3):
            self._set_state(self.States.STATE_CLOSE)
        else:
            self._set_state(self.States.STATE_BEETWEEN)

    def _test(self):
        self.open()
        self.close()
        self.open()

    def get_state_string(self, state=None):
        state = state or self._state
        if state == self.States.STATE_OPENING:
            return "Opening"
        elif state == self.States.STATE_OPEN:
            return "Open"
        elif state == self.States.STATE_CLOSING:
            return "Closing"
        elif state == self.States.STATE_CLOSE:
            return "Close"
        elif state == self.States.STATE_BEETWEEN:
            return "Beetwen"
        return super().get_state_string(state)
