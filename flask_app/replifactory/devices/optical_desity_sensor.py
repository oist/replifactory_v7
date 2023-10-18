import threading
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.optimize import curve_fit

from replifactory.devices import Device
from replifactory.devices.laser import Laser
from replifactory.devices.photodiode import Photodiode

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
    # adc_driver: ADCDriver
    # io_port_driver: IOPortDriver
    laser: Laser
    photodiode: Photodiode

    def __init__(
        self,
        # adc_driver: ADCDriver = None,
        # io_port_driver: IOPortDriver = None,
        photodiode: Photodiode = None,
        laser: Laser = None,
        lock=global_lock,
        delay_before_measure=0.02,
        curve_fitting_parameters: CurveFittingParameters = default_curve_fitting_parameters,
        name: Optional[str] = None,
    ):
        super().__init__(name or f"Optical Density Sensor {photodiode.diode_cs}")
        # self.adc_driver = adc_driver
        # self.io_port_driver = io_port_driver
        self.photodiode = photodiode
        self.laser = laser
        self.delay_before_measure = delay_before_measure
        self.lock = lock
        self.curve_fitting_parameters = curve_fitting_parameters

    # def measure_od_all(device, vials_to_measure=(1, 2, 3, 4, 5, 6, 7)):
    #     available_vials = []
    #     for v in vials_to_measure:
    #         if device.locks_vials[v].acquire(blocking=False):
    #             available_vials += [v]

    #     od_values = {}
    #     if len(available_vials) > 0:
    #         # Stop stirrers completely and wait 10 seconds for vortex to settle bubbles to raise above laser level.
    #         # Waiting enough time for the smallest bubbles to raise improves the measurement precision.
    #         # for vial in available_vials:
    #         #     device.stirrers.set_speed(vial=vial, speed=3)
    #         # time.sleep(2)
    #         # Stir at minimum speed (without forming vortex) to homogenize turbidity and prevent precipitation
    #         for vial in available_vials:
    #             device.stirrers.set_speed(vial=vial, speed=0)
    #         time.sleep(4)
    #         # for vial in available_vials:
    #         #     device.stirrers.set_speed(vial=vial, speed=1)
    #         # time.sleep(3)
    #         # for vial in available_vials:
    #         #     device.stirrers.set_speed(vial=vial, speed=0)
    #         # time.sleep(1)
    #         for vial in available_vials:
    #             od = device.od_sensors[vial].measure_od()
    #             od_values[vial] = od
    #         for vial in available_vials:
    #             device.stirrers.set_speed(vial=vial, speed=2)
    #         # time.sleep(2)
    #         # for vial in available_vials:
    #         #     device.stirrers.set_speed(vial=vial, speed=3)
    #         # time.sleep(5)
    #         # for vial in available_vials:
    #         #     device.stirrers.set_speed(vial=vial, speed=2)
    #         # for vial in available_vials:
    #         #     device.stirrers.set_speed(vial=vial, speed=3)
    #         # time.sleep(2)
    #         # for vial in available_vials:
    #         #     device.stirrers.set_speed(vial=vial, speed=2)
    #         # time.sleep(1)
    #         for v in available_vials:
    #             device.locks_vials[v].release()

    #         # assign values to culture.od parameter, which writes to csv file and calculates mu
    #         for v in od_values.keys():
    #             device.cultures[v].od = od_values[v]
    #     return od_values

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

    # @property
    # def coefs(self):
    #     return self.device.calibration_coefs_od[self.vial_number]

    # @coefs.setter
    # def coefs(self, value):
    #     self.device.calibration_coefs_od[self.vial_number] = list(value)
    #     try:
    #         self.device.save()
    #     except Exception:
    #         pass

    def calibration_function(self, mv):
        a = self.curve_fitting_parameters.infinity_x_asymptote
        b = self.curve_fitting_parameters.hill
        c = self.curve_fitting_parameters.inflection
        d = self.curve_fitting_parameters.small_x_asymptote
        g = self.curve_fitting_parameters.rate_of_change
        return self.od_calibration_function(mv, a, b, c, d, g)

    # @property
    # def calibration_od_to_mv(self):
    #     return self.device.calibration_od_to_mv[self.vial_number]

    # @calibration_od_to_mv.setter
    # def calibration_od_to_mv(self, value):
    #     value = float(value)
    #     self.device.calibration_od_to_mv[self.vial_number] = value
    #     # self.fit_calibration_function()
    #     self.device.save()

    # def fit_calibration_function(self):
    #     calibration_mv = list(self.device.calibration_mv_to_od[self.vial_number].keys())
    #     calibration_od = list(self.device.calibration_mv_to_od[self.vial_number].values())
    #     calibration_mv = np.array(sorted(calibration_mv))
    #     calibration_od = np.array(sorted(calibration_od)[::-1])
    #     drop_index = calibration_od < 5
    #     calibration_mv = calibration_mv[drop_index]
    #     calibration_od = calibration_od[drop_index]
    #
    #     if calibration_mv is not None:
    #         if len(calibration_mv) >= 4:
    #             coefs, _ = curve_fit(od_calibration_function, calibration_mv, calibration_od, p0=(0, 2, 0, 20, 1),
    #                                  bounds=[(-0.5, 0, 0, 20, 0), (0.1, 5, 20, 200, 3)],
    #                                  sigma=1 / (calibration_mv * 0.1 + 0.0001), max_nfev=5000)
    #             a, b, c, d, g = coefs
    #
    #             def f(mv):
    #                 """
    #                 converts mV to OD
    #                 """
    #                 return od_calibration_function(mv, a, b, c, d, g)
    #             self.calibration_function = f
    #             return a, b, c, d, g

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

    # def add_calibration_point(self, od, mv): # before copilot suggestion
    #     try:
    #         self.calibration_od_to_mv[od] += [mv]
    #     except KeyError:
    #         self.calibration_od_to_mv[od] = [mv]

    # def calibration_curve(self):
    #     if len(calibration_mv) < 4:
    #         print("OD SENSOR %d: NOT ENOUGH CALIBRATION POINTS (%d/4)" % (self.vial_number, len(calibration_mv)))
    #     else:
    #         plt.figure(figsize=[6, 4], dpi=100)
    #         try:
    #             a, b, c, d, g = self.fit_calibration_function()
    #             xmin = min(calibration_mv)
    #             xmax = max(calibration_mv)
    #             x = np.linspace(xmin, 50, 501)
    #             y = self.calibration_function(x)
    #             plt.plot(x, y, "k:")
    #             plt.title("od_min: %.3f    slope: %.3f    mv_inflec: %.3f    od_max: %.3f, g: %.3f" % (a, b, c, d, g),
    #                       fontsize=8)
    #         except:
    #             print("Could not fit calibration function")
    #
    #         plt.plot(calibration_mv, calibration_od, "r.")
    #         plt.xlabel("ADC signal (mV)")
    #         plt.ylabel("Optical Density")
    #         plt.suptitle("OD sensor calibration, vial %d" % self.vial_number, fontsize=10)
    #         # plt.show()

    # def plot_calibration_curve(self):
    #     plt.figure(figsize=[4, 2], dpi=150)

    #     calibration_od = np.array(list(self.calibration_od_to_mv.keys()))
    #     calibration_mv = np.array(list(self.calibration_od_to_mv.values()))
    #     max_len = len(max(calibration_mv, key=len))
    #     calibration_mv_filled = np.array(
    #         [list(i) + [np.nan] * (max_len - len(i)) for i in calibration_mv]
    #     )
    #     calibration_mv_err = np.nanstd(calibration_mv_filled, 1)
    #     # calibration_mv = np.array(list(self.calibration_od_to_mv.values())).mean(1)
    #     calibration_mv = np.nanmean(calibration_mv_filled, 1)

    #     xmin = min(calibration_mv)
    #     # xmax = max(calibration_mv)
    #     x = np.linspace(xmin, 50, 501)
    #     y = self.calibration_function(x)
    #     a, b, c, d, g = self.coefs
    #     plt.plot(x, y, "b:", label="function fit")
    #     plt.title(
    #         "od_max: %.3f    slope: %.3f    mv_inflec: %.3f    od_min: %.3f, g: %.3f"
    #         % (a, b, c, d, g),
    #         fontsize=8,
    #     )
    #     #     plt.plot(calibration_mv, calibration_od, "r.")
    #     plt.errorbar(
    #         calibration_mv,
    #         calibration_od,
    #         xerr=calibration_mv_err,
    #         fmt="b.",
    #         label="calibration data",
    #     )
    #     plt.xlabel("signal[mV] (background-subtracted)")
    #     plt.ylabel("OD")
    #     plt.title("Vial %d OD calibration" % self.vial_number, fontsize=8)

    #     if self.device.is_connected():
    #         sig = self.measure_signal()
    #         od = self.calibration_function(sig)
    #         plt.axhline(od, ls="-", c="r")
    #         plt.axvline(
    #             sig, ls="-", c="r", label="current measurement (%.2f,%.2f)" % (sig, od)
    #         )
    #     plt.legend()

    #     plt.show()

    def measure_transmitted_intensity(self):
        """
        returns the intensity of the transmitted light
        :return:
        """
        with self.lock:
            with self.laser:
                time.sleep(self.delay_before_measure)
                mv, err = self.photodiode.measure(gain=8, bitrate=16)
                return mv, err

    def measure_background_intensity(self):
        """
        returns the intensity of the background light (no laser)
        :return:
        """
        mv, err = self.photodiode.measure(gain=8, bitrate=16)
        return mv, err

    # def pause_mixers_and_measure_od(self):
    #     vial = self.vial_number
    #     self.device.locks_vials[vial].acquire()
    #     while self.device.is_pumping_in_vial == vial:
    #         time.sleep(1)
    #
    #     self.device.stirrers.set_speed(vial=vial, speed=0)  # wait 10s for vortex to stop
    #     time.sleep(10)
    #     self.device.stirrers.set_speed(vial=vial, speed=1)  # mix very slowly while measuring OD
    #     time.sleep(5)
    #
    #     od = self.measure_od()
    #
    #     self.device.stirrers.set_speed(vial=vial, speed=2)  # resume normal stirring speed
    #     self.device.locks_vials[vial].release()
    #     return od

    # def log_od(self, od):
    #     directory = os.path.join(self.device.directory, "vial_%d" % self.vial_number)
    #     if not os.path.exists(directory):
    #         os.mkdir(directory)
    #
    #     filepath = os.path.join(directory, "od.csv")
    #     if not os.path.exists(filepath):
    #         with open(filepath, "w+") as f:
    #             f.write("time,od\n")
    #     with open(filepath, "a") as f:
    #         data_string = "%.1f,%.4f\n" % (time.time(), od)
    #         f.write(data_string)

    # def log_mv(self, background, transmitted):
    #     directory = os.path.join(self.device.directory, "vial_%d" % self.vial_number)
    #     if not os.path.exists(directory):
    #         os.mkdir(directory)

    #     filepath = os.path.join(directory, "photodiode_millivolts.csv")
    #     if not os.path.exists(filepath):
    #         with open(filepath, "w+") as f:
    #             f.write("time,transmitted,background\n")
    #     with open(filepath, "a") as f:
    #         data_string = "%d,%.4f,%.4f\n" % (int(time.time()), transmitted, background)
    #         f.write(data_string)

    def measure_signal(self):
        background, _ = self.measure_background_intensity()
        transmitted, _ = self.measure_transmitted_intensity()
        # if self.device.directory is not None:
        #     self.log_mv(background=background, transmitted=transmitted)
        signal = transmitted - background
        return signal

    def measure_od(self):
        signal = self.measure_signal()
        if not callable(self.calibration_function):
            self.fit_calibration_function()

        od = self.calibration_function(signal)
        # self.log_od(od=od)  # logging in the culture class also updates growth rate
        return od

    # def check(self):
    #     assert self.calibration_function is not None
    #     v = self.vial_number
    #     signal = self.device.od_sensors[v].measure_signal()
    #     if signal >= 15:
    #         color = bcolors.OKGREEN
    #     elif 10 < signal < 15:
    #         color = bcolors.WARNING
    #     else:
    #         color = bcolors.FAIL
    #     print("vial %d OD sensor: " % v + color + "%.2f mV" % signal + bcolors.ENDC)

    def test(self):
        signal_wo_laser = self.photodiode.measure()
        self.laser.switch_on()
        signal_w_laser = self.photodiode.measure()
        self.laser.switch_off()
        return signal_wo_laser[0] > signal_w_laser[0]
