import logging
import threading
import time
from enum import Enum
from typing import Optional, Union

import flask_app.replifactory.drivers.pca9685 as pca9685
from flask_app.replifactory.devices import Device, DeviceCallback
from flask_app.replifactory.util import BraceMessage as __

logger = logging.getLogger(__name__)


class Stirrer(Device):
    class States(Device.States, Enum):
        STATE_STOPED = 111
        STATE_STIRRING = 112

    lock = threading.RLock()

    def __init__(
        self,
        pwm_channel: int,
        driver: pca9685.PWMDriver,
        name: Optional[str] = None,
        low_speed: float = 0.0002,
        fast_speed: float = 1,
        acceleration_delay: float = 0.1,
        accelerate_threshold: float = 0.2,
        init_speed: float = 0.0,
        callback: Optional[DeviceCallback] = None,
    ):
        super().__init__(name or f"Stirrer {pwm_channel}", callback=callback)
        self.pwm_channel = pwm_channel
        self.driver = driver
        self.slow_speed = low_speed
        self.fast_speed = fast_speed
        self.acceleration_delay = acceleration_delay
        self.accelerate_threshold = accelerate_threshold
        self._speed = init_speed

    def reset(self):
        self.set_speed(self._speed)

    def read_state(self):
        self._speed = self.get_speed()

    def get_speed(self) -> float:
        """Return stirrer speed

        Returns:
            float: value from 0 to 1
        """
        return self.driver.get_duty_cycle(self.pwm_channel)

    def get_data(self):
        return super().get_data() | {
            "speed": self._speed,
        }

    def speed_to_duty_cycle(self, speed: int):
        if speed == 0:
            return 0.0
        elif speed == 1:
            return self.slow_speed
        elif speed == 2:
            return self.fast_speed
        raise ValueError("Speed should be in [0, 1, 2]")

    def set_speed(self, speed: Union[float, int], accelerate=True):
        logger.debug(
            __(
                "enter set_speed(speed={speed}, accelerate={accelerate})",
                speed=speed,
                accelerate=accelerate,
            )
        )
        if isinstance(speed, int):
            duty_cycle = self.speed_to_duty_cycle(speed)
        else:
            duty_cycle = speed
        if duty_cycle > 1.0:
            logger.warning(
                f"Duty cycle {duty_cycle} bigger than range [0.0, 1.0]. Set to 1.0"
            )
            duty_cycle = 1.0
        elif duty_cycle < 0:
            logger.warning(
                f"Duty cycle {duty_cycle} lower than range [0.0, 1.0]. Set to 0.0"
            )
            duty_cycle = 0.0
        with self.lock:
            if 0 < duty_cycle < self.accelerate_threshold and accelerate:
                logger.debug(
                    f"Duty cycle {duty_cycle} lower than accelerate threshold {self.accelerate_threshold}. Accelerating."
                )
                self._set_speed(self.fast_speed)
                logger.debug(f"Wait {self.acceleration_delay} sec to accelerate")
                time.sleep(self.acceleration_delay)
            self._set_speed(duty_cycle)
        logger.debug("exit set_speed")

    def _set_speed(self, speed: float):
        self.driver.set_duty_cycle(self.pwm_channel, speed)
        self._speed = speed
        if speed > 0:
            self._set_state(self.States.STATE_STIRRING, force=True)
        else:
            self._set_state(self.States.STATE_STOPED)

    def emergency_stop(self):
        self.set_speed(0.0)

    def test(self):
        pass

    def get_state_string(self, state=None):
        state = state or self._state
        if state == self.States.STATE_STOPED:
            return "Stoped"
        elif state == self.States.STATE_STIRRING:
            return "Stirring"
        return super().get_state_string(state)

    def get_drivers(self):
        return [self.driver]
