import logging

import pandas as pd

import replifactory.drivers.l6470h as l6470h
from flask_app.replifactory.devices import Device
from flask_app.replifactory.util import BraceMessage as __

logger = logging.getLogger(__name__)


class Motor(Device):
    driver: l6470h.StepMotorDriver

    def __init__(self, driver: l6470h.StepMotorDriver = None):
        self.driver = driver
        self.steps_per_revolution: int = 200  # nema-17 step motor datasheet
        self.max_revolution_per_second = (
            driver.max_steps_per_second / self.steps_per_revolution
        )
        self.max_speed_revolution_per_second = 4
        self.full_step_speed = 0b1100110  # legacy 10-bit * 0.1
        self.stall_threshold = 0b100000  # half of max 0b111111
        self.min_speed_rps = 0.01
        self.max_speed_rps = 40
        self.acceleration = round(((1 << 12) - 1) * 0.01)  # legacy
        self.deceleration = round(((1 << 12) - 1) * 0.01)  # legacy
        self.kval_hold = 0
        self.kval_run = round(((1 << 8) - 1) * 1)  # 0.8)  # legacy
        self.kval_acc = round(((1 << 8) - 1) * 1)  # 0.57)  # legacy
        self.kval_dec = round(((1 << 8) - 1) * 1)  # 0.3)  # legacy

    def configure(self):
        logger.debug("Configure")
        self.driver.set_param(l6470h.parameters.FS_SPD, self.full_step_speed)
        self.driver.set_param(l6470h.parameters.STALL_TH, self.stall_threshold)

        self.driver.set_param(l6470h.parameters.KVAL_HOLD, self.kval_hold)
        self.driver.set_param(l6470h.parameters.KVAL_RUN, self.kval_run)
        self.driver.set_param(l6470h.parameters.KVAL_ACC, self.kval_acc)
        self.driver.set_param(l6470h.parameters.KVAL_DEC, self.kval_dec)

        self.set_min_speed(self.min_speed_rps)
        self.set_max_speed(self.max_speed_rps)
        self.driver.set_param(l6470h.parameters.ACC, self.acceleration)
        self.driver.set_param(l6470h.parameters.DEC, self.deceleration)

    def test(self):
        success = False
        logger.debug(f"Start self test for motor {self.driver.spi_port._cs}")
        self.driver.set_param(l6470h.parameters.OCD_TH, 0)
        self.move(1)
        status = self.driver.status
        if status.is_overcurrent:
            success = True
        self.driver.reset_device()
        status = self.driver.status
        if status.is_overcurrent:
            success = False
        return success

    def run(self, forward: bool = True, revolutions_per_second: float = None):
        steps_per_second = self.convert_revolutions_per_second_to_steps_per_second(
            revolutions_per_second
        )
        self.driver.run(forward=forward, steps_per_second=steps_per_second)

    def stop(self):
        self.driver.soft_stop()

    def emergency_stop(self):
        self.driver.hard_stop()

    def move(self, n_revolutions: float = 1, revolution_per_second: float = None):
        """Move the given number of revolutions
        By default uses 1/128 microstepping to minimize noise and vibration.
        If number of required microsteps can not fit in the register (> 2^22),
        the step mode is decreased to 1/64 or lower.

        Args:
            n_revolutions (float, optional): Count of revolutions (can be negative to move backward). Defaults to 1.
            revolution_per_second (float, optional): Move speed. Defaults to None - instance default value.
        """
        logger.debug(
            __(
                "Move motor {num} to {revolutions:.4f} revolution with {speed:.4f} revolutoions per second",
                num=self.driver.spi_port.cs,
                revolutions=n_revolutions,
                speed=revolution_per_second,
            )
        )
        n_microsteps = (
            abs(n_revolutions)
            * self.steps_per_revolution
            * l6470h.STEP_MODE_128.microsteps_per_step
        )
        suitable_step_mode = self.driver.get_suitable_step_mode(n_microsteps)
        n_microsteps = int(
            abs(n_revolutions)
            * self.steps_per_revolution
            * suitable_step_mode.microsteps_per_step
        )

        direction = n_revolutions > 0
        self.set_max_speed(
            revolution_per_second or self.max_speed_revolution_per_second
        )
        self.driver.set_step_mode(suitable_step_mode)
        return self.driver.move(n_microsteps, direction)

    def set_max_speed(self, revolutions_per_second: float):
        if revolutions_per_second > self.max_revolution_per_second:
            raise ValueError(
                f"Maximum speed is {self.max_revolution_per_second} when you try to set {revolutions_per_second}"
            )
        steps_per_tick = self.convert_revolution_per_second_to_steps_per_tick(
            revolutions_per_second
        )
        self.driver.set_max_speed(steps_per_tick)

    def set_min_speed(self, revolutions_per_second: float):
        steps_per_tick = self.convert_revolution_per_second_to_steps_per_tick(
            revolutions_per_second
        )
        self.driver.set_min_speed(steps_per_tick)

    def convert_revolutions_per_second_to_steps_per_second(
        self, revolutions_per_second: float
    ) -> int:
        return round(revolutions_per_second * self.steps_per_revolution)

    def convert_revolution_per_second_to_steps_per_tick(
        self, revolution_per_second: float
    ) -> float:
        steps_per_second = revolution_per_second * self.steps_per_revolution
        return self.driver.convert_steps_per_sec_to_steps_per_tick(steps_per_second)

    def get_status(self):
        return self.driver.get_status()

    def _get_int_param(self, param: l6470h.Param):
        return int.from_bytes(self.driver.get_param(param), "big")

    def _print_param(self, param: l6470h.Param):
        value = self._get_int_param(param)
        print(f"{param.description}: {value}")

    def print_status(self):
        status = self.get_status()
        # df_status = pd.DataFrame(status, index=["STATUS"])
        print(f"Status [{status.value:016b}]:\n{status}")

    def print_registers(self):
        raw_abs_pos = self._get_int_param(l6470h.parameters.ABS_POS)
        raw_el_pos = self._get_int_param(l6470h.parameters.EL_POS)
        raw_mark = self._get_int_param(l6470h.parameters.MARK)
        raw_speed = self._get_int_param(l6470h.parameters.SPEED)
        raw_acc = self._get_int_param(l6470h.parameters.ACC)
        raw_dec = self._get_int_param(l6470h.parameters.DEC)
        raw_max_speed = self._get_int_param(l6470h.parameters.MAX_SPEED)
        raw_min_speed = self._get_int_param(l6470h.parameters.MIN_SPEED)
        raw_kval_hold = self._get_int_param(l6470h.parameters.KVAL_HOLD)
        raw_kval_run = self._get_int_param(l6470h.parameters.KVAL_RUN)
        raw_kval_acc = self._get_int_param(l6470h.parameters.KVAL_ACC)
        raw_kval_dec = self._get_int_param(l6470h.parameters.KVAL_DEC)
        raw_int_speed = self._get_int_param(l6470h.parameters.INT_SPEED)
        raw_st_slp = self._get_int_param(l6470h.parameters.ST_SLP)
        raw_fn_slp_acc = self._get_int_param(l6470h.parameters.FN_SLP_ACC)
        raw_fn_slp_dec = self._get_int_param(l6470h.parameters.FN_SLP_DEC)
        raw_k_therm = self._get_int_param(l6470h.parameters.K_THERM)
        raw_adc_out = self._get_int_param(l6470h.parameters.ADC_OUT)
        raw_ocd_th = self._get_int_param(l6470h.parameters.OCD_TH)
        raw_stall_th = self._get_int_param(l6470h.parameters.STALL_TH)
        raw_fs_spd = self._get_int_param(l6470h.parameters.FS_SPD)
        raw_step_mode = self._get_int_param(l6470h.parameters.STEP_MODE)
        raw_alarm_en = self._get_int_param(l6470h.parameters.ALARM_EN)
        config = self.driver.get_config()
        data = [
            [
                "ABS_POS",
                raw_abs_pos,
                l6470h.parameters.ABS_POS.to_unit(raw_abs_pos),
                l6470h.parameters.ABS_POS.unit_name,
                l6470h.parameters.ABS_POS.description,
            ],
            [
                "EL_POS",
                raw_el_pos,
                l6470h.parameters.EL_POS.to_unit(raw_el_pos),
                l6470h.parameters.EL_POS.unit_name,
                l6470h.parameters.EL_POS.description,
            ],
            [
                "MARK",
                raw_mark,
                l6470h.parameters.MARK.to_unit(raw_mark),
                l6470h.parameters.MARK.unit_name,
                l6470h.parameters.MARK.description,
            ],
            [
                "SPEED",
                raw_speed,
                l6470h.parameters.SPEED.to_unit(raw_speed),
                l6470h.parameters.SPEED.unit_name,
                l6470h.parameters.SPEED.description,
            ],
            [
                "ACC",
                raw_acc,
                l6470h.parameters.ACC.to_unit(raw_acc),
                l6470h.parameters.ACC.unit_name,
                l6470h.parameters.ACC.description,
            ],
            [
                "DEC",
                raw_dec,
                l6470h.parameters.DEC.to_unit(raw_dec),
                l6470h.parameters.DEC.unit_name,
                l6470h.parameters.DEC.description,
            ],
            [
                "MAX_SPEED",
                raw_max_speed,
                l6470h.parameters.MAX_SPEED.to_unit(raw_max_speed),
                l6470h.parameters.MAX_SPEED.unit_name,
                l6470h.parameters.MAX_SPEED.description,
            ],
            [
                "MIN_SPEED",
                raw_min_speed,
                l6470h.parameters.MIN_SPEED.to_unit(raw_min_speed),
                l6470h.parameters.MIN_SPEED.unit_name,
                l6470h.parameters.MIN_SPEED.description,
            ],
            [
                "KVAL_HOLD",
                raw_kval_hold,
                l6470h.parameters.KVAL_HOLD.to_unit(raw_kval_hold),
                l6470h.parameters.KVAL_HOLD.unit_name,
                l6470h.parameters.KVAL_HOLD.description,
            ],
            [
                "KVAL_RUN",
                raw_kval_run,
                l6470h.parameters.KVAL_RUN.to_unit(raw_kval_run),
                l6470h.parameters.KVAL_RUN.unit_name,
                l6470h.parameters.KVAL_RUN.description,
            ],
            [
                "KVAL_ACC",
                raw_kval_acc,
                l6470h.parameters.KVAL_ACC.to_unit(raw_kval_acc),
                l6470h.parameters.KVAL_ACC.unit_name,
                l6470h.parameters.KVAL_ACC.description,
            ],
            [
                "KVAL_DEC",
                raw_kval_dec,
                l6470h.parameters.KVAL_DEC.to_unit(raw_kval_dec),
                l6470h.parameters.KVAL_DEC.unit_name,
                l6470h.parameters.KVAL_DEC.description,
            ],
            [
                "INT_SPEED",
                raw_int_speed,
                l6470h.parameters.INT_SPEED.to_unit(raw_int_speed),
                l6470h.parameters.INT_SPEED.unit_name,
                l6470h.parameters.INT_SPEED.description,
            ],
            [
                "ST_SLP",
                raw_st_slp,
                l6470h.parameters.ST_SLP.to_unit(raw_st_slp),
                l6470h.parameters.ST_SLP.unit_name,
                l6470h.parameters.ST_SLP.description,
            ],
            [
                "FN_SLP_ACC",
                raw_fn_slp_acc,
                l6470h.parameters.FN_SLP_ACC.to_unit(raw_fn_slp_acc),
                l6470h.parameters.FN_SLP_ACC.unit_name,
                l6470h.parameters.FN_SLP_ACC.description,
            ],
            [
                "FN_SLP_DEC",
                raw_fn_slp_dec,
                l6470h.parameters.FN_SLP_DEC.to_unit(raw_fn_slp_dec),
                l6470h.parameters.FN_SLP_DEC.unit_name,
                l6470h.parameters.FN_SLP_DEC.description,
            ],
            [
                "K_THERM",
                raw_k_therm,
                l6470h.parameters.K_THERM.to_unit(raw_k_therm),
                l6470h.parameters.K_THERM.unit_name,
                l6470h.parameters.K_THERM.description,
            ],
            [
                "ADC_OUT",
                raw_adc_out,
                l6470h.parameters.ADC_OUT.to_unit(raw_adc_out),
                l6470h.parameters.ADC_OUT.unit_name,
                l6470h.parameters.ADC_OUT.description,
            ],
            [
                "OCD_TH",
                raw_ocd_th,
                l6470h.parameters.OCD_TH.to_unit(raw_ocd_th),
                l6470h.parameters.OCD_TH.unit_name,
                l6470h.parameters.OCD_TH.description,
            ],
            [
                "STALL_TH",
                raw_stall_th,
                l6470h.parameters.STALL_TH.to_unit(raw_stall_th),
                l6470h.parameters.STALL_TH.unit_name,
                l6470h.parameters.STALL_TH.description,
            ],
            [
                "FS_SPD",
                raw_fs_spd,
                l6470h.parameters.FS_SPD.to_unit(raw_fs_spd),
                l6470h.parameters.FS_SPD.unit_name,
                l6470h.parameters.FS_SPD.description,
            ],
            [
                "STEP_MODE",
                raw_step_mode,
                l6470h.parameters.STEP_MODE.to_unit(raw_step_mode),
                l6470h.parameters.STEP_MODE.unit_name,
                l6470h.parameters.STEP_MODE.description,
            ],
            [
                "ALARM_EN",
                raw_alarm_en,
                l6470h.parameters.ALARM_EN.to_unit(raw_alarm_en),
                l6470h.parameters.ALARM_EN.unit_name,
                l6470h.parameters.ALARM_EN.description,
            ],
        ]
        df_registers = pd.DataFrame(
            data, columns=["Register", "Raw value", "Unit value", "Unit", "Description"]
        )
        formatters = {}
        # last_column_index = len(df_registers.columns) - 1
        len_max = df_registers["Description"].str.len().max()
        formatters["Description"] = lambda _: f"{_:<{len_max}s}"
        print(df_registers.to_string(formatters=formatters, index=False, header=True))
        print(f"Config [{config.value:016b}]:\n{config}")
        # print(df_registers)
