from typing import Optional

from flask_app.replifactory.devices import Device, DeviceCallback
from flask_app.replifactory.devices.step_motor import Motor


class Pump(Device):

    def __init__(
        self,
        motor: Motor,
        max_speed_rps: Optional[float] = None,
        name: Optional[str] = None,
        callback: Optional[DeviceCallback] = None,
    ):
        super().__init__(name or "Pump", callback=callback)
        self.motor = motor
        self.max_speed_rps = max_speed_rps or motor.max_speed_rps
        self.coefficients = {
            1: 10,
            5: 9.5,
            10: 9.0,
            50: 8.5,
        }
        self.points = sorted([(rot, coef) for rot, coef in self.coefficients.items()])

    def read_state(self):
        motor_state = self.motor.read_state()
        if motor_state == self.States.STATE_ERROR:
            self._set_state(self.States.STATE_ERROR)
        elif motor_state == self.States.STATE_WORKING:
            self._set_state(self.States.STATE_WORKING)
        elif motor_state == self.States.STATE_OPERATIONAL:
            self._set_state(self.States.STATE_OPERATIONAL)
        else:
            self._set_state(motor_state)

    def stop(self):
        self.motor.stop()
        self._set_state(self.States.STATE_OPERATIONAL)

    @property
    def is_pumping(self):
        return self.motor.is_moving

    @property
    def is_idle(self):
        return self.motor.is_idle

    def get_data(self):
        return super().get_data() | {
            "max_speed_rps": self.max_speed_rps,
        }

    def run(self, forward: bool = True, rot_per_sec: Optional[float] = None):
        self._set_state(self.States.STATE_WORKING)
        self.motor.run(forward, rot_per_sec or self.max_speed_rps)

    def pump(self, volume: float, rot_per_sec: Optional[float] = None):
        """Pump certain amount of liquid

        Args:
            volume (float): amount that have to be pumped
            rot_per_sec (float, optional): Pumping speed in rotations per second. Defaults to None.
        """
        rotations = self.calculate_rotations(abs(volume))
        if volume < 0:
            rotations *= -1
        if volume != 0:
            if rot_per_sec is None:
                rot_per_sec = self.max_speed_rps
            self._set_state(self.States.STATE_WORKING)
            self.motor.move(n_revolutions=rotations, revolution_per_second=rot_per_sec)
            self._set_state(self.States.STATE_OPERATIONAL)

    def calculate_rotations(self, volume):
        # Get the coefficients for the given pumpId
        # Convert the coefficients into a list of (rotations, coefficient) pairs and sort
        points = self.points

        # If volume is larger than the largest known, use the largest coefficient
        if volume >= points[-1][0] * points[-1][1]:
            return volume / points[-1][1]

        # Find the two points surrounding the given volume
        lower_point = points[0]
        upper_point = points[-1]
        for i in range(len(points) - 1):
            if volume >= points[i][0] * points[i][1] and volume <= points[i + 1][0] * points[i + 1][1]:
                lower_point = points[i]
                upper_point = points[i + 1]
                break

        # Calculate the interpolation factor
        lower_volume = lower_point[0] * lower_point[1]
        upper_volume = upper_point[0] * upper_point[1]
        factor = (volume - lower_volume) / (upper_volume - lower_volume)

        # Interpolate the coefficient
        interpolated_coefficient = lower_point[1] + (upper_point[1] - lower_point[1]) * factor

        # Calculate the rotations
        rotations = volume / interpolated_coefficient

        return rotations

    def calculate_volume(self, rotations):
        coefficients = self.coefficients

        if rotations <= min(coefficients.keys()):
            correction_coefficient = coefficients[min(coefficients.keys())]
        else:
            for i in range(len(coefficients) - 1):
                if list(coefficients.keys())[i] <= rotations < list(coefficients.keys())[i + 1]:
                    correction_coefficient = coefficients[list(coefficients.keys())[i]] + \
                                             (rotations - list(coefficients.keys())[i]) * \
                                             (coefficients[list(coefficients.keys())[i + 1]] - coefficients[
                                                 list(coefficients.keys())[i]]) / \
                                             (list(coefficients.keys())[i + 1] - list(coefficients.keys())[i])
                    break
            else:
                correction_coefficient = coefficients[max(coefficients.keys())]
        volume = rotations * correction_coefficient
        return round(volume, 2)

    def test(self):
        return self.motor.test()
