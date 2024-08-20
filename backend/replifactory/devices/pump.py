from typing import Optional

from replifactory.devices import Device, DeviceCallback, device_command
from replifactory.devices.step_motor import Motor


class Pump(Device, DeviceCallback):

    def __init__(
        self,
        motor: Motor,
        max_speed_rps: Optional[float] = None,
        name: Optional[str] = None,
        callback: Optional[DeviceCallback] = None,
    ):
        super().__init__(name or "Pump", callback=callback)
        self.motor = motor
        self.motor.set_callback(self)
        self.max_speed_rps = max_speed_rps or motor._profile.max_speed_rps
        self.coefficients = {
            1: 10,
            5: 9.5,
            10: 9.0,
            50: 8.5,
        }
        self.points = sorted([(rot, coef) for rot, coef in self.coefficients.items()])

    def reset(self):
        self.motor.reset()

    @device_command
    def read_state(self):
        motor_state = self.motor.read_state()
        self._on_device_state_change(self.motor, motor_state)
        return motor_state

    @device_command
    def stop(self):
        self._log.debug(f"Stoping {self.name}")
        self._set_state(self.States.STATE_FINISHING)
        self.motor.stop()
        # self._set_state(self.States.STATE_OPERATIONAL)

    @device_command
    def set_profile(self, profile):
        self.motor.set_profile(profile)

    def _on_device_state_change(self, device, state):
        if state == self.States.STATE_ERROR:
            self._set_state(self.States.STATE_ERROR, force=True)
        elif state == self.States.STATE_WORKING:
            self._set_state(self.States.STATE_WORKING, force=True)
        elif state == self.States.STATE_OPERATIONAL:
            self._set_state(self.States.STATE_OPERATIONAL, force=True)
        else:
            self._set_state(state, force=True)
        return self._state

    def is_pumping(self):
        return self.read_state() == self.States.STATE_WORKING

    def is_idle(self):
        return self.read_state() == self.States.STATE_OPERATIONAL

    def is_error(self):
        return self.read_state() == self.States.STATE_ERROR

    def get_data(self):
        return super().get_data() | {
            "max_speed_rps": self.max_speed_rps,
            "motor": self.motor.get_data(),
        }

    @device_command
    def run(self, forward: bool = True, rot_per_sec: Optional[float] = None):
        self._set_state(self.States.STATE_WORKING)
        self.motor.run(forward, rot_per_sec or self.max_speed_rps)

    @device_command
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
            if (
                volume >= points[i][0] * points[i][1]
                and volume <= points[i + 1][0] * points[i + 1][1]
            ):
                lower_point = points[i]
                upper_point = points[i + 1]
                break

        # Calculate the interpolation factor
        lower_volume = lower_point[0] * lower_point[1]
        upper_volume = upper_point[0] * upper_point[1]
        factor = (volume - lower_volume) / (upper_volume - lower_volume)

        # Interpolate the coefficient
        interpolated_coefficient = (
            lower_point[1] + (upper_point[1] - lower_point[1]) * factor
        )

        # Calculate the rotations
        rotations = volume / interpolated_coefficient

        return rotations

    def calculate_volume(self, rotations):
        coefficients = self.coefficients

        if rotations <= min(coefficients.keys()):
            correction_coefficient = coefficients[min(coefficients.keys())]
        else:
            for i in range(len(coefficients) - 1):
                if (
                    list(coefficients.keys())[i]
                    <= rotations
                    < list(coefficients.keys())[i + 1]
                ):
                    correction_coefficient = coefficients[
                        list(coefficients.keys())[i]
                    ] + (rotations - list(coefficients.keys())[i]) * (
                        coefficients[list(coefficients.keys())[i + 1]]
                        - coefficients[list(coefficients.keys())[i]]
                    ) / (
                        list(coefficients.keys())[i + 1] - list(coefficients.keys())[i]
                    )
                    break
            else:
                correction_coefficient = coefficients[max(coefficients.keys())]
        volume = rotations * correction_coefficient
        return round(volume, 2)

    def test(self):
        return self.motor.test()

    def get_drivers(self):
        return self.motor.get_drivers()
