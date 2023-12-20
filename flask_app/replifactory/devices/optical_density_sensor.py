from enum import Enum
import threading
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
from pyftdi.i2c import I2cNackError
from scipy.optimize import curve_fit

from flask_app.replifactory.devices import Device, DeviceCallback
from flask_app.replifactory.devices.laser import Laser
from flask_app.replifactory.devices.photodiode import Photodiode

global_lock = threading.RLock()


@dataclass
class CurveFittingParameters:
    infinity_x_asymptote: float  # a
    hill: float  # b
    inflection: float  # c
    small_x_asymptote: float  # d
    rate_of_change: float  # g

    def __init__(
        self,
        infinity_x_asymptote: float,
        hill: float,
        inflection: float,
        small_x_asymptote: float,
        rate_of_change: float,
    ):
        self.infinity_x_asymptote = infinity_x_asymptote
        self.hill = hill
        self.inflection = inflection
        self.small_x_asymptote = small_x_asymptote
        self.rate_of_change = rate_of_change


default_curve_fitting_parameters = CurveFittingParameters(
    *[
        4.922604096995577,
        0.9064619103638237,
        19.999999999969816,
        -0.49999999999999994,
        2.286809580704199,
    ]
)


class OpticalDensitySensor(Device):
    class States(Device.States, Enum):
        STATE_MEASURING = 121

    def __init__(
        self,
        photodiode: Photodiode,
        laser: Laser,
        lock=global_lock,
        delay_before_measure=0.02,
        curve_fitting_parameters: CurveFittingParameters = default_curve_fitting_parameters,
        name: Optional[str] = None,
        callback: Optional[DeviceCallback] = None,
    ):
        super().__init__(
            name or f"Optical Density Sensor {photodiode.diode_cs}", callback=callback
        )
        self.photodiode = photodiode
        self.laser = laser
        self.delay_before_measure = delay_before_measure
        self.lock = lock
        self.curve_fitting_parameters = curve_fitting_parameters
        self._value = 0

    def od_calibration_function(self, x, a, b, c, d, g):
        """
        converts signal mV to optical density
        4 Parameter logistic function
        adapted from:
        https://weightinginbayesianmodels.github.io/poctcalibration/calib_tut4_curve_background.html

        :param x: signal voltage in millivolts
        :param a: On the scale of y; horizontal asymptote as x goes to infinity.
        :param b: Hill coefficient
        :param c: Inflection point.
        :param d: On the scale of y; horizontal asymptote as x goes, in theory, to negative infinity,
                but, in practice, to zero.
        :return: y - optical density
        """
        y = d + (a - d) / ((1 + (x / c) ** b) ** g)
        return y

    def od_calibration_function_inverse(self, y, a, b, c, d, g):
        """
        converts optical density to signal mV

        Inverse of 4 Parameter logistic function
        adapted from:
        https://weightinginbayesianmodels.github.io/poctcalibration/calib_tut4_curve_background.html

        :param y: optical density
        :param a: On the scale of y; horizontal asymptote as x goes to infinity.
        :param b: Hill coefficient
        :param c: Inflection point.
        :param d: On the scale of y; horizontal asymptote as x goes, in theory, to negative infinity,
                but, in practice, to zero.
        :return: x - signal voltage in millivolts
        """
        x = c * (((a - d) / (y - d)) ** (1 / g) - 1) ** (1 / b)
        return x

    def calibration_function(self, mv):
        a = self.curve_fitting_parameters.infinity_x_asymptote
        b = self.curve_fitting_parameters.hill
        c = self.curve_fitting_parameters.inflection
        d = self.curve_fitting_parameters.small_x_asymptote
        g = self.curve_fitting_parameters.rate_of_change
        return self.od_calibration_function(mv, a, b, c, d, g)

    def fit_calibration_function(self):
        # try:
        calibration_od = np.array(list(self.calibration_od_to_mv.keys()))
        calibration_mv = np.array(list(self.calibration_od_to_mv.values()))

        max_len = len(max(calibration_mv, key=len))
        calibration_mv_filled = np.array(
            [list(i) + [np.nan] * (max_len - len(i)) for i in calibration_mv]
        )
        calibration_mv_err = np.nanstd(calibration_mv_filled, 1)
        # calibration_mv = np.array(list(self.calibration_od_to_mv.values())).mean(1)
        calibration_mv = np.nanmean(calibration_mv_filled, 1)

        calibration_mv_err += 0.01  # allows curve fit with single measurements

        coefs, _ = curve_fit(
            self.od_calibration_function_inverse,
            calibration_od,
            calibration_mv,
            maxfev=5000,
            p0=(20, 5, 0.07, -0.2, 1),
            bounds=[(3, 0, 0, -0.5, 0), (200, 10, 20, 0.1, 5)],
            sigma=calibration_mv_err,
        )
        # a, b, c, d, g = coefs
        self.coefs = coefs
        # except:
        #     print("vial %d calibration function fit error" % self.vial_number)
        # def f(mv):
        #     """
        #     converts mV to OD
        #     """
        #     return od_calibration_function(mv, a, b, c, d, g)

    def add_calibration_point(self, mv, od):
        temp = self.calibration_od_to_mv
        if od not in temp:
            temp[od] = []
        temp[od].append(mv)
        self.calibration_od_to_mv = temp

    def _measure_transmitted_intensity(self):
        """
        returns the intensity of the transmitted light
        :return:
        """
        with self.lock:
            with self.laser:
                time.sleep(self.delay_before_measure)
                mv, err = self.photodiode.measure(gain=8, bitrate=16)
                return mv, err

    def _measure_background_intensity(self):
        """
        returns the intensity of the background light (no laser)
        :return:
        """
        mv, err = self.photodiode.measure(gain=8, bitrate=16)
        return mv, err

    def _measure_signal(self):
        background, _ = self._measure_background_intensity()
        transmitted, _ = self._measure_transmitted_intensity()
        # if self.device.directory is not None:
        #     self.log_mv(background=background, transmitted=transmitted)
        signal = transmitted - background
        return signal

    def measure_od(self):
        self._set_state(self.States.STATE_MEASURING)
        signal = self._measure_signal()
        if not callable(self.calibration_function):
            self.fit_calibration_function()
        od = self.calibration_function(signal)
        self._value = od
        self._set_state(self.States.STATE_OPERATIONAL)
        return od

    def test(self):
        signal_wo_laser = self.photodiode.measure()
        self.laser.switch_on()
        signal_w_laser = self.photodiode.measure()
        self.laser.switch_off()
        return signal_wo_laser[0] > signal_w_laser[0]

    def read_state(self):
        try:
            self.measure_od()
        except I2cNackError as exc:
            self._log.warning("Not acknowledge (NACK)")
            self._error = str(exc)
            self._set_state(self.States.STATE_ERROR)
        else:
            self._set_state(self.States.STATE_OPERATIONAL)

    def get_data(self):
        data = super().get_data() | {
            "value": self._value,
        }
        return data

    def get_state_string(self, state=None):
        state = state or self._state
        if state == self.States.STATE_MEASURING:
            return "Measuring"
        return super().get_state_string(state)
