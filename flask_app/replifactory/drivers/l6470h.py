import logging
import math
import threading
from dataclasses import dataclass
from typing import Callable, Union

from pyftdi.spi import SpiPort

from flask_app.replifactory.util import ArrayOfBytesAsInt
from flask_app.replifactory.util import BraceMessage as __
from replifactory.drivers import Driver

logger = logging.getLogger(__name__)


def to_float(x: int, n: int) -> float:
    """Convert fixed point number to float

    Args:
        x (int): Number in fixed point format
        n (int): Count of bits after decimal point (Qm.n)

    Returns:
        float: Number in float point format
    """
    c = abs(x)
    sign = 1
    if x < 0:
        # convert back from two's complement
        c = x - 1
        c = ~c
        sign = -1
    f = (1.0 * c) / (2**n)
    f = f * sign
    return f


def to_fixed(f: float, n: int) -> int:
    """Convert float point number to fixed

    Args:
        f (float): Number in float point format
        n (int): Count of bits after decimal point (Qm.n)

    Returns:
        int: Number in fixed point format (Q0.n)
    """
    a = f * (2**n)
    b = int(round(a))
    if a < 0:
        # next three lines turns b into it's 2's complement.
        b = abs(b)
        b = ~b
        b = b + 1
    return b


@dataclass
class Param:
    address: int
    size: int
    description: str
    mask: bytes
    unsigned_fixed_point_frational_bits: int
    unit_name: str

    def __init__(
        self,
        address: int,
        size: int,
        description: str,
        unit_name: str = "",
        unsigned_fixed_point_frational_bits: int = 0,
    ):
        self.address = address
        self.size = size
        self.description = description
        mask_len = (size + 7) // 8
        self.mask = ((1 << size) - 1).to_bytes(mask_len, "big")
        self.unit_name = unit_name
        self.unsigned_fixed_point_frational_bits = unsigned_fixed_point_frational_bits

    def to_raw(self, value: float | int) -> int:
        if self.unsigned_fixed_point_frational_bits > 0:
            return to_fixed(value, self.unsigned_fixed_point_frational_bits)
        else:
            return int(value)

    def to_unit(self, raw: int) -> float | int:
        if self.unsigned_fixed_point_frational_bits > 0:
            return to_float(raw, self.unsigned_fixed_point_frational_bits)
        else:
            return raw


class Parameters:
    ABS_POS = Param(0x01, 22, "Current position")
    EL_POS = Param(0x02, 9, "Electrical position")
    MARK = Param(0x03, 22, "Mark position")
    SPEED = Param(
        0x04,
        20,
        "Current speed",
        unit_name="step/s",
        unsigned_fixed_point_frational_bits=28,
    )
    ACC = Param(0x05, 12, "Acceleration")
    DEC = Param(0x06, 12, "Deceleration")
    MAX_SPEED = Param(0x07, 10, "Maximum speed")
    MIN_SPEED = Param(0x08, 13, "Minimum speed")
    KVAL_HOLD = Param(0x09, 8, "Holding KVAL")
    KVAL_RUN = Param(0x0A, 8, "Constant speed KVAL")
    KVAL_ACC = Param(0x0B, 8, "Acceleration starting KVAL")
    KVAL_DEC = Param(0x0C, 8, "Deceleration starting KVAL")
    INT_SPEED = Param(0x0D, 14, "Intersect speed")
    ST_SLP = Param(0x0E, 8, "Start slope")
    FN_SLP_ACC = Param(0x0F, 8, "Acceleration final slope")
    FN_SLP_DEC = Param(0x10, 8, "Deceleration final slope")
    K_THERM = Param(0x11, 4, "Thermal compensation factor")
    ADC_OUT = Param(0x12, 5, "ADC output")
    OCD_TH = Param(0x13, 4, "OCD threshold", "mA")
    STALL_TH = Param(0x14, 7, "STALL threshold")
    FS_SPD = Param(0x15, 10, "Full-step speed")
    STEP_MODE = Param(0x16, 8, "Step mode")
    ALARM_EN = Param(0x17, 8, "Alarm enable")
    CONFIG = Param(0x18, 16, "IC configuration")
    STATUS = Param(0x19, 16, "Status")
    UNKNOWN = Param(0x00, 0, "Unknown parameter")

    __ALL__ = {k: v for k, v in locals().items() if not k.startswith("_")}

    def by_code(self, code: int) -> tuple[str, Param]:
        for name, param in self.__ALL__.items():
            if param.address == code:
                return name, param
        return self.__ALL__["UNKNOWN"]


parameters = Parameters()


class ParameterValue:
    def __init__(self, type: Param, value: bytes):
        self._raw_value = value
        self._type = type
        self._value = None

    @property
    def raw_value(self):
        return self._raw_value

    @property
    def value(self):
        if self._value is None:
            self._value = self.raw_to_unit()
        return self._value

    def raw_to_unit(self):
        return int.from_bytes(self._raw_value, "big")

    def __str__(self):
        return f"{self._type.description}: {self.value}{self._type.unit_name}"

    def __eq__(self, other):
        if isinstance(other, ParameterValue):
            return type(self) == type(other) and self._raw_value == other._raw_value
        return False


class AbsPosValue(ParameterValue):
    def __init__(self, value: bytes):
        super().__init__(Parameters.ABS_POS, value)

    def raw_to_unit(self):
        return int.from_bytes(self._raw_value, "big", signed=True)


class OdcThValue(ParameterValue):
    def __init__(self, value: bytes):
        super().__init__(Parameters.OCD_TH, value)

    def raw_to_unit(self):
        return (1 + int.from_bytes(self._raw_value, "big")) * OCD_TH_SCALE


class StepMotorConfigValue(ParameterValue):
    def __init__(self, value: bytes):
        super().__init__(Parameters.CONFIG, value)

    def raw_to_unit(self):
        value = int.from_bytes(self._raw_value, "big")
        return {
            "OSC_SEL": value & 0b111,
            "EXT_CLK": (value >> 3) & 0b1,
            "SW_MODE": (value >> 4) & 0b1,
            "EN_VSCOMP": (value >> 5) & 0b1,
            "OC_SD": (value >> 7) & 0b1,
            "POW_SR": (value >> 8) & 0b11,
            "F_PWM_DEC": (value >> 10) & 0b111,
            "F_PWM_INT": (value >> 13) & 0b111,
        }

    def __str__(self):
        if self.value["OSC_SEL"] & 0b100 == 0:
            clock_source_value = "Internal oscillator 16 MHz"
            oscin_value = "Unused"
            if self.value["EXT_CLK"] == 1:
                if self.value["OSC_SEL"] == 0b000:
                    oscout_value = "Supplies a 2-MHz clock"
                elif self.value["OSC_SEL"] == 0b001:
                    oscout_value = "Supplies a 4-MHz clock"
                elif self.value["OSC_SEL"] == 0b010:
                    oscout_value = "Supplies a 8-MHz clock"
                else:
                    oscout_value = "Supplies a 16-MHz clock"
            else:
                oscout_value = "Unused"
        else:
            if self.value["EXT_CLK"] == 1:
                oscin_value = "Crystal/resonator driving"
                oscout_value = "Crystal/resonator driving"
                if self.value["OSC_SEL"] == 0b100:
                    clock_source_value = "External crystal or resonator 8 MHz"
                elif self.value["OSC_SEL"] == 0b101:
                    clock_source_value = "External crystal or resonator 16 MHz"
                elif self.value["OSC_SEL"] == 0b110:
                    clock_source_value = "External crystal or resonator 24 MHz"
                else:
                    clock_source_value = "External crystal or resonator 32 MHz"
            else:
                oscin_value = "Clock source"
                oscout_value = "Supplies inverted OSCIN signal"
                if self.value["OSC_SEL"] == 0b100:
                    clock_source_value = (
                        "Ext clock source 8 MHz (Crystal/resonator driver disabled)"
                    )
                elif self.value["OSC_SEL"] == 0b101:
                    clock_source_value = (
                        "Ext clock source 16 MHz (Crystal/resonator driver disabled)"
                    )
                elif self.value["OSC_SEL"] == 0b110:
                    clock_source_value = (
                        "Ext clock source 24 MHz (Crystal/resonator driver disabled)"
                    )
                else:
                    clock_source_value = (
                        "Ext clock source 32 MHz (Crystal/resonator driver disabled)"
                    )
        # osc_sel = f"Clock source: {clock_source_value} OSCIN: {oscin_value} OSCOUT: {oscout_value}"
        clock_source = f"Clock source: {clock_source_value}"
        oscin = f"OSCIN: {oscin_value}"
        oscout = f"OSCOUT: {oscout_value}"
        sw_value = (
            "HardStop interrupt" if self.value["SW_MODE"] == 0 else "User disposal"
        )
        sw_mode = f"External switch act as: {sw_value}"
        oc_sd_value = (
            "Bridges shut down"
            if self.value["OC_SD"] == 1
            else "Bridges do not shut down"
        )
        oc_sd = f"On overcurrent: {oc_sd_value}"
        if self.value["POW_SR"] == 0b00:
            pow_sr_value = 320
        elif self.value["POW_SR"] == 0b01:
            pow_sr_value = 75
        elif self.value["POW_SR"] == 0b10:
            pow_sr_value = 110
        else:
            pow_sr_value = 260
        pow_sr = f"Output slew rate: {pow_sr_value} V/us"
        en_vscomp_value = "Disabled" if self.value["EN_VSCOMP"] == 0 else "Enabled"
        en_vscomp = f"Motor supply voltage compensation: {en_vscomp_value}"
        f_pwm_int_value = (
            self.value["F_PWM_INT"] + 1 if self.value["F_PWM_INT"] < 0b111 else ""
        )
        f_pwm_int = f"PWM frequency. Integer division factor: {f_pwm_int_value}"
        if self.value["F_PWM_DEC"] == 0b000:
            f_pwm_dec_value = 0.625
        elif self.value["F_PWM_DEC"] == 0b001:
            f_pwm_dec_value = 0.75
        elif self.value["F_PWM_DEC"] == 0b010:
            f_pwm_dec_value = 0.875
        elif self.value["F_PWM_DEC"] == 0b011:
            f_pwm_dec_value = 1
        elif self.value["F_PWM_DEC"] == 0b100:
            f_pwm_dec_value = 1.25
        elif self.value["F_PWM_DEC"] == 0b101:
            f_pwm_dec_value = 1.5
        elif self.value["F_PWM_DEC"] == 0b110:
            f_pwm_dec_value = 1.75
        else:
            f_pwm_dec_value = 2
        f_pwm_dec = f"PWM frequency. Multiplication factor: {f_pwm_dec_value}"
        if self.value["OSC_SEL"] == 0b100:
            pwm_freq_value = OSCILATOR_FRIQUENCIES_8_MHZ[self.value["F_PWM_INT"]][
                self.value["F_PWM_DEC"]
            ]
        elif self.value["OSC_SEL"] == 0b101 or self.value["OSC_SEL"] & 0b100 == 0:
            pwm_freq_value = OSCILATOR_FRIQUENCIES_16_MHZ[self.value["F_PWM_INT"]][
                self.value["F_PWM_DEC"]
            ]
        elif self.value["OSC_SEL"] == 0b110:
            pwm_freq_value = OSCILATOR_FRIQUENCIES_24_MHZ[self.value["F_PWM_INT"]][
                self.value["F_PWM_DEC"]
            ]
        else:
            pwm_freq_value = OSCILATOR_FRIQUENCIES_32_MHZ[self.value["F_PWM_INT"]][
                self.value["F_PWM_DEC"]
            ]
        pwm_freq = f"PWM frequency: {pwm_freq_value} kHz"
        return f"{clock_source}\n{oscin}\n{oscout}\n{sw_mode}\n{oc_sd}\n{pow_sr}\n{en_vscomp}\n{f_pwm_int}\n{f_pwm_dec}\n{pwm_freq}"


class StepMotorStatusValue(ParameterValue):
    def __init__(self, value: bytes):
        super().__init__(Parameters.STATUS, value)

    def raw_to_unit(self):
        return {
            "HiZ": (0x01 & self._raw_value[1]),
            "BUSY": (0x02 & self._raw_value[1]) >> 1,
            "SW_F": (0x04 & self._raw_value[1]) >> 2,
            "SW_ENV": (0x08 & self._raw_value[1]) >> 3,
            "DIR": (0x10 & self._raw_value[1]) >> 4,
            "MOT_STATUS": (0x60 & self._raw_value[1]) >> 5,
            "NOTPERF_CMD": (0x80 & self._raw_value[1]) >> 7,
            "WRONG_CMD": 0x01 & self._raw_value[0],
            "UVLO": (0x02 & self._raw_value[0]) >> 1,
            "TH_WRN": (0x04 & self._raw_value[0]) >> 2,
            "TH_SD": (0x08 & self._raw_value[0]) >> 3,
            "OCD": (0x10 & self._raw_value[0]) >> 4,
            "STEP_LOSS_A": (0x20 & self._raw_value[0]) >> 5,
            "STEP_LOSS_B": (0x40 & self._raw_value[0]) >> 6,
            "SCK_MOD": (0x80 & self._raw_value[0]) >> 7,
        }

    @property
    def is_busy(self):
        return self.value["BUSY"] == 0

    @property
    def is_overcurrent(self):
        return self.value["OCD"] == 0

    @property
    def is_thermal_shutdown(self):
        return self.value["TH_SD"] == 0

    def __str__(self):
        hiz = "High impedance state\n" if self.value["HiZ"] == 1 else ""
        uvlo = "Undervoltage lockout or reset\n" if self.value["UVLO"] == 0 else ""
        th_wrn = "Thermal warning\n" if self.value["TH_WRN"] == 0 else ""
        th_sd = "Thermal shutdown\n" if self.value["TH_SD"] == 0 else ""
        ocd = "Overcurrent detect\n" if self.is_overcurrent else ""
        loss_a = "Stall on bridge A\n" if self.value["STEP_LOSS_A"] == 0 else ""
        loss_b = "Stall on bridge B\n" if self.value["STEP_LOSS_B"] == 0 else ""
        notpref_cmd = (
            "Command can not be performed\n" if self.value["NOTPERF_CMD"] == 1 else ""
        )
        wrong_cmd = "Wrong command\n" if self.value["WRONG_CMD"] == 1 else ""
        sw_f = "External switch is closed\n" if self.value["SW_F"] == 1 else ""
        sw_evn = "Switch turned on\n" if self.value["SW_ENV"] == 1 else ""
        busy = "Busy\n" if self.is_busy else ""
        sck_mod = "Step-clock mode\n" if self.value["SCK_MOD"] == 1 else ""
        dir = "Forward direction\n" if self.value["DIR"] == 1 else "Reverse direction\n"
        if self.value["MOT_STATUS"] == 0b00:
            mot_status = "Stopped"
        elif self.value["MOT_STATUS"] == 0b01:
            mot_status = "Acceleration"
        elif self.value["MOT_STATUS"] == 0b10:
            mot_status = "Deceleration"
        elif self.value["MOT_STATUS"] == 0b11:
            mot_status = "Constant speed"
        else:
            mot_status = "Unkonwn motor status"
        return f"{hiz}{uvlo}{th_wrn}{th_sd}{ocd}{loss_a}{loss_b}{notpref_cmd}{wrong_cmd}{sw_f}{sw_evn}{busy}{sck_mod}{dir}{mot_status}"


@dataclass
class StepMode:
    value: int
    microsteps_per_step: int
    name: str


STEP_MODE_FS = StepMode(0, 1, "Full-step")
STEP_MODE_HS = StepMode(1, 2, "Half-step")
STEP_MODE_4 = StepMode(2, 4, "1/4 microstep")
STEP_MODE_8 = StepMode(3, 8, "1/8 microstep")
STEP_MODE_16 = StepMode(4, 16, "1/16 microstep")
STEP_MODE_32 = StepMode(5, 32, "1/32 microstep")
STEP_MODE_64 = StepMode(6, 64, "1/64 microstep")
STEP_MODE_128 = StepMode(7, 128, "1/128 microstep")

STEP_MODES = (
    STEP_MODE_FS,
    STEP_MODE_HS,
    STEP_MODE_4,
    STEP_MODE_8,
    STEP_MODE_16,
    STEP_MODE_32,
    STEP_MODE_64,
    STEP_MODE_128,
)


@dataclass
class Command(object):
    address: int
    mask: list[int]


class Commands:
    # SET_PARAM = Command(0x00, [])
    GET_PARAM = Command(0x20, [0x00, 0x00])
    RUN = Command(0x50, [0x0F, 0xFF, 0xFF])
    STEP_CLOCK = Command(0x58, [])
    MOVE_BACK = Command(0x40, [0x3F, 0xFF, 0xFF])
    MOVE_FORWARD = Command(0x41, [0x3F, 0xFF, 0xFF])
    GO_TO = Command(0x60, [0x3F, 0xFF, 0xFF])
    GO_TO_DIR = Command(0x68, [0x3F, 0xFF, 0xFF])
    GO_UNTIL = Command(0x82, [0x0F, 0xFF, 0xFF])
    RELEASE_SW = Command(0x92, [])
    GO_HOME = Command(0x70, [])
    GO_MARK = Command(0x78, [])
    RESET_POS = Command(0xD8, [])
    RESET_DEVICE = Command(0xC0, [])
    SOFT_STOP = Command(0xB0, [])
    HARD_STOP = Command(0xB8, [])
    SOFT_HIZ = Command(0xA0, [])
    HARD_HIZ = Command(0xA8, [])
    GET_STATUS = Command(0xD0, [0x00, 0x00])
    UNKNOWN = Command(0x00, [])

    __ALL__ = {k: v for k, v in locals().items() if not k.startswith("_")}

    def by_code(self, code: int) -> tuple[str, Command | Param]:
        if code & 0xF0 < self.GET_PARAM.address:
            name, param = parameters.by_code(code)
            return f"WRITE_{name}", param
        if code & 0xF0 <= 0x30:
            name, param = parameters.by_code(code & 0x1F)
            return f"READ_{name}", param
        for name, cmd in self.__ALL__.items():
            if cmd.address == code:
                return name, cmd
        return self.__ALL__["UNKNOWN"]


commands = Commands()

OSCILATOR_FRIQUENCIES_8_MHZ = [
    [9.8, 11.7, 13.7, 15.6, 19.5, 23.4, 27.3, 31.3],
    [4.9, 5.9, 6.8, 7.8, 9.8, 11.7, 13.7, 15.6],
    [3.3, 3.9, 4.6, 5.2, 6.5, 7.8, 9.1, 10.4],
    [2.4, 2.9, 3.4, 3.9, 4.9, 5.9, 6.8, 7.8],
    [2.0, 2.3, 2.7, 3.1, 3.9, 4.7, 5.5, 6.3],
    [1.6, 2.0, 2.3, 2.6, 3.3, 3.9, 4.6, 5.2],
    [1.4, 1.7, 2.0, 2.2, 2.8, 3.3, 3.9, 4.5],
]
OSCILATOR_FRIQUENCIES_16_MHZ = [
    [19.5, 23.4, 27.3, 31.3, 39.1, 46.9, 54.7, 62.5],
    [9.8, 11.7, 13.7, 15.6, 19.5, 23.4, 27.3, 31.3],
    [6.5, 7.8, 9.1, 10.4, 13.0, 15.6, 18.2, 20.8],
    [4.9, 5.9, 6.8, 7.8, 9.8, 11.7, 13.7, 15.6],
    [3.9, 4.7, 5.5, 6.3, 7.8, 9.4, 10.9, 12.5],
    [3.3, 3.9, 4.6, 5.2, 6.5, 7.8, 9.1, 10.4],
    [2.8, 3.3, 3.9, 4.5, 5.6, 6.7, 7.8, 8.9],
]
OSCILATOR_FRIQUENCIES_24_MHZ = [
    [29.3, 35.2, 41.0, 46.9, 58.6, 70.3, 82.0, 93.8],
    [14.6, 17.6, 20.5, 23.4, 29.3, 35.2, 41.0, 46.9],
    [9.8, 11.7, 13.7, 15.6, 19.5, 23.4, 27.3, 31.3],
    [7.3, 8.8, 10.3, 11.7, 14.6, 17.6, 20.5, 23.4],
    [5.9, 7.0, 8.2, 9.4, 11.7, 14.1, 16.4, 18.8],
    [4.9, 5.9, 6.8, 7.8, 9.8, 11.7, 13.7, 15.6],
    [4.2, 5.0, 5.9, 6.7, 8.4, 10.0, 11.7, 13.4],
]
OSCILATOR_FRIQUENCIES_32_MHZ = [
    [39.1, 46.9, 54.7, 62.5, 78.1, 93.8, 109.4, 125.0],
    [19.5, 23.4, 27.3, 31.3, 39.1, 46.9, 54.7, 62.5],
    [13.0, 15.6, 18.2, 20.8, 26.0, 31.3, 36.5, 41.7],
    [9.8, 11.7, 13.7, 15.6, 19.5, 23.4, 27.3, 31.3],
    [7.8, 9.4, 10.9, 12.5, 15.6, 18.8, 21.9, 25.0],
    [6.5, 7.8, 9.1, 10.4, 13.0, 15.6, 18.2, 20.8],
    [5.6, 6.7, 7.8, 8.9, 11.2, 13.4, 15.6, 17.9],
]


ABS_POS_MAX = (1 << parameters.ABS_POS.size) - 1

OCD_TH_SCALE = 375

_lock = threading.RLock()


class CommandName:
    def __init__(self, command_code: int):
        self.command_code = command_code

    def __str__(self):
        try:
            name, _ = commands.by_code(self.command_code)
            return name
        except Exception as e:
            return str(e)


class StepMotorDriver(Driver):
    """API for L6470H step motor driver"""

    def __init__(self, get_port: Callable[[], SpiPort]):
        self._get_port = get_port
        # steps_per_revolution: int = 200
        self.max_steps_per_second = 15610  # page 43 from L6470H datasheet
        # max_revolution_per_second = max_steps_per_second / steps_per_revolution
        self.seconds_per_tick = 0.000000250  # 250ns
        # minimal_speed_in_steps_per_tick = 2**-18
        # seconds_per_step = seconds_per_tick / minimal_speed_in_steps_per_tick
        self.max_n_microsteps = 2**22 - 1  # 22 bit

    def get_status(self) -> StepMotorStatusValue:
        return self.status
        # return StepMotorStatusValue(self._get_status())

    def get_config(self) -> ParameterValue:
        return self.config

    @property
    def config(self) -> ParameterValue:
        return StepMotorConfigValue(self.get_param(parameters.CONFIG))

    @property
    def status(self) -> StepMotorStatusValue:
        return StepMotorStatusValue(self.get_param(parameters.STATUS))

    @property
    def absolute_position(self) -> ParameterValue:
        return AbsPosValue(self.get_param(parameters.ABS_POS))

    @property
    def adc_out(self) -> ParameterValue:
        return ParameterValue(Parameters.ADC_OUT, self.get_param(parameters.ADC_OUT))

    @property
    def ocd_th(self) -> ParameterValue:
        return OdcThValue(self.get_param(parameters.OCD_TH))

    def set_param(self, param: Param, value: int | bytearray):
        if isinstance(value, bytearray):
            data_bytes = value
        else:
            data_bytes = self._to_bytes(param, value)
        self._command(param.address, data_bytes)

    def get_param(self, param: Param) -> bytes:
        cmd = commands.GET_PARAM.address | param.address
        mask_len = len(param.mask)
        # return self._command(cmd, [0x00] * mask_len, mask_len)
        return self._command(cmd, [], mask_len)

    def reset_device(self):
        self._command(commands.RESET_DEVICE.address)

    def run(self, forward: bool, steps_per_second: int):
        SPEED_UQ_SIZE = 28
        direction_forward_bit = 1 if forward else 0
        cmd = commands.RUN.address | direction_forward_bit
        steps_per_tick = self.convert_steps_per_sec_to_steps_per_tick(steps_per_second)
        data_bytes = self._to_bytes(
            commands.RUN, to_fixed(steps_per_tick, SPEED_UQ_SIZE)
        )
        self._command(cmd, data_bytes)

    def soft_stop(self, wait: bool = False):
        self._command(commands.SOFT_STOP.address)
        status = self.get_status()
        while wait and status.is_busy:
            status = self.get_status()

    def hard_stop(self):
        self._command(commands.HARD_STOP.address)

    def move(
        self,
        n_steps: int,
        reverse: bool = False,
        wait: bool = False,
    ):
        logger.debug(
            __(
                "Move motor {num} for {steps:d} steps and {direction} direction",
                num=self._get_port().cs,
                steps=n_steps,
                direction=reverse,
            )
        )
        cmd = commands.MOVE_BACK.address if reverse else commands.MOVE_FORWARD.address
        data_bytes = self._to_bytes(commands.MOVE_BACK, n_steps)
        self._command(cmd, data_bytes)
        status = self.get_status()
        while wait and status.is_busy:
            status = self.get_status()
        return status

    def convert_steps_per_sec_to_steps_per_tick(self, steps_per_sec: float) -> float:
        return steps_per_sec * self.seconds_per_tick

    def set_step_mode(self, step_mode: StepMode):
        self.set_param(parameters.STEP_MODE, step_mode.value)

    def set_acceleration(self, steps_per_sec2):
        ACC_UQ_SIZE = 40
        steps_per_tick2 = steps_per_sec2 * (self.seconds_per_tick**2)
        acc_register_value = to_fixed(steps_per_tick2, ACC_UQ_SIZE) - 1
        self.set_param(parameters.ACC, acc_register_value)

    def set_deceleration(self, steps_per_sec2):
        DEC_UQ_SIZE = 40
        steps_per_tick2 = steps_per_sec2 * (self.seconds_per_tick**2)
        dec_register_value = to_fixed(steps_per_tick2, DEC_UQ_SIZE) - 1
        self.set_param(parameters.DEC, dec_register_value)

    def set_max_speed(self, steps_per_tick):
        MAX_SPEED_UQ_SIZE = (
            18  # unsigned fixed point bits after decimal point for MAX_SPEED register
        )
        max_speed_register_value = to_fixed(steps_per_tick, MAX_SPEED_UQ_SIZE)
        self.set_param(parameters.MAX_SPEED, max_speed_register_value)

    def set_min_speed(self, steps_per_tick):
        MIN_SPEED_UQ_SIZE = 24
        min_speed_register_value = to_fixed(steps_per_tick, MIN_SPEED_UQ_SIZE)
        self.set_param(parameters.MIN_SPEED, min_speed_register_value)

    def get_suitable_step_mode(
        self, microsteps: int, step_mode: StepMode = STEP_MODE_128
    ) -> StepMode:
        """Find minimal step mode enought for microsteps count

        Args:
            microsteps (int): Amount of microsteps in microstep mode
            step_mode (StepMode): Microstep mode

        Returns:
            StepMode: Suitable step mode
        """
        if microsteps > self.max_n_microsteps:
            step_mode_index = (
                step_mode.value
                - 1
                - int(math.log(microsteps / self.max_n_microsteps, 2))
            )
            if step_mode_index < 0:
                raise ValueError(
                    f"Value {microsteps} is bigger then maximum {self.max_n_microsteps} for FULL_STEP_MODE"
                )
            return STEP_MODES[step_mode_index]
        return step_mode

    def _get_status(self):
        return self._command(
            commands.GET_STATUS.address, readlen=len(commands.GET_STATUS.mask)
        )

    def _to_bytes(self, param: Param | Command, value: int) -> bytes:
        data_len = len(param.mask)
        data_bytes = bytearray(value.to_bytes(data_len, "big"))
        for i in range(data_len):
            data_bytes[i] = param.mask[i] & data_bytes[i]
        return data_bytes

    def _command(
        self,
        cmd: int,
        data_bytes: Union[list[int], bytes] = [],
        readlen: int = 0,
    ) -> bytearray:
        logger.debug(
            __(
                "Write to SPI (cs={cs}) cmd: {cmd_name} (0x{cmd:02X}) data: {int_data} {data} readlen: {readlen:d}",
                cs=self._get_port().cs,
                cmd=cmd,
                cmd_name=CommandName(cmd),
                data=data_bytes,
                int_data=ArrayOfBytesAsInt(data_bytes),
                readlen=readlen,
            )
        )
        payload = [cmd]
        if data_bytes:
            payload += data_bytes
        # result = self.spi_port.exchange(out=payload, readlen=readlen)
        # return result

        # hack for FTDI SPI mode 3 limitations
        with _lock:
            res = bytearray()
            for b in range(len(payload)):
                # start = b == 0
                # stop = readlen <= 0 and b == len(payload) - 1
                # self.spi_port.write(out=[payload[b]], start=start, stop=stop)
                self._get_port().write([payload[b]])
            if readlen > 0:
                for b in range(readlen):
                    # stop = b == readlen - 1
                    # res += self.spi_port.read(readlen=1, start=False, stop=stop)
                    res += self._get_port().read(1)
                logger.debug(
                    __(
                        "Read from SPI (cs={cs}) {int_data} {data}",
                        cs=self._get_port().cs,
                        data=res,
                        int_data=ArrayOfBytesAsInt(res),
                    )
                )
            return res
