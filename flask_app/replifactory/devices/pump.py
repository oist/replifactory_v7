import math
from typing import Optional

from flask_app.replifactory.devices import Device
from flask_app.replifactory.devices.step_motor import Motor


class Pump(Device):
    motor: Motor
    max_speed_rps: float

    def __init__(
        self,
        motor: Motor,
        max_speed_rps: float = None,
        name: Optional[str] = None,
    ):
        super().__init__(name or f"Pump {motor.driver.spi_port.cs}")
        self.motor = motor

    def read_state(self):
        pass

    def pump(self, volume: float, rot_per_sec: float = None):
        """Pump certain amount of liquid

        Args:
            volume (float): amount that have to be pumped
            rot_per_sec (float, optional): Pumping speed in rotations per second. Defaults to None.
        """
        rotations = self.__calibration_function(abs(volume))
        if volume < 0:
            rotations *= -1
        if volume != 0:
            if rot_per_sec is None:
                rot_per_sec = self.max_speed_rps
            self.motor.move(n_revolutions=rotations, revolution_per_second=rot_per_sec)

    def __calibration_function(self, volume: float):
        if len(self.coefs) < 3:
            return None
        else:
            a, b, c = self.coefs
            return self.__pump_calibration_function(volume, a, b, c)

    def __pump_calibration_function(x, a, b, c):
        """
        converts pumped volume (x) to motor rotations(y)
        """
        y = a * x + b * x * math.exp(-c * x)
        return y

    def test(self):
        return self.motor.test()
