import logging
import threading
import time
from typing import Optional, Union

import replifactory.drivers.pca9685 as pca9685
from flask_app.replifactory.devices import Device
from flask_app.replifactory.util import BraceMessage as __

logger = logging.getLogger(__name__)


class Stirrer(Device):
    lock = threading.RLock()

    def __init__(
        self,
        pwm_channel: int,
        name: Optional[str] = None,
        driver: pca9685.PWMDriver = None,
        low_speed: float = 0.0002,
        fast_speed: float = 1,
        acceleration_delay: float = 0.1,
        accelerate_threshold: float = 0.2,
    ):
        super().__init__(name or f"Stirrer {pwm_channel}")
        self.pwm_channel = pwm_channel
        self.driver = driver
        self.slow_speed = low_speed
        self.fast_speed = fast_speed
        self.acceleration_delay = acceleration_delay
        self.accelerate_threshold = accelerate_threshold

    def get_speed(self) -> float:
        """Return stirrer speed

        Returns:
            float: value from 0 to 1
        """
        return self.driver.get_duty_cycle(self.pwm_channel)

    # def get_speed(self) -> Union[int, float]:
    #     with self.lock:
    #         duty_cycle = self.driver.get_duty_cycle(self.pwm_channel)
    #     if math.isclose(duty_cycle, 0.0, rel_tol=1e-2):
    #         return 0
    #     elif math.isclose(duty_cycle, self.slow_speed, rel_tol=1e-2):
    #         return 1
    #     elif math.isclose(duty_cycle, self.fast_speed, rel_tol=1e-2):
    #         return 2
    #     return duty_cycle

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
        if type(speed) is int:
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
                self.driver.set_duty_cycle(self.pwm_channel, self.fast_speed)
                logger.debug(f"Wait {self.acceleration_delay} sec to accelerate")
                time.sleep(self.acceleration_delay)
            self.driver.set_duty_cycle(self.pwm_channel, duty_cycle)
        logger.debug("exit set_speed")

    def emergency_stop(self):
        self.set_speed(0.0)

    def test(self):
        pass
