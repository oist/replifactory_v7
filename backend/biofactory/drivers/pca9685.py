import time
from typing import Union

from biofactory.drivers import Driver, HardwarePort
from biofactory.util import BraceMessage as __

REGISTER_MODE_1 = 0x00
REGISTER_MODE_2 = 0x01
REGISTER_PRE_SCALE = 0xFE
REGISTER_ALL_LED_ON_L = 0xFA
REGISTER_ALL_LED_ON_H = 0xFB
LED_STRIP_START_REGADR = 0x06  # LED0 ON Low Byte
LED_STRIP_COUNT = 16

MODE1_RESTART_BIT = 1 << 7
MODE1_EXTCLK_BIT = 1 << 6
MODE1_AI_BIT = 1 << 5
MODE1_SLEEP_BIT = 1 << 4
MODE1_SUB1_BIT = 1 << 3
MODE1_SUB2_BIT = 1 << 2
MODE1_SUB3_BIT = 1 << 1
MODE1_ALLCALL_BIT = 1 << 0

OSCILLATOR_STABILIZE_TIME = 0.0005  # 500us
OSCILLATOR_CLOCK_FREQUENCY = 25000000  # 25MHz
LED_TOTAL_VALUES = 4096

LED_MAX_VALUE = LED_TOTAL_VALUES - 1
RANGE_PWM_FREQUENCY = (24, 1526)
RANGE_LED_NUMBER = (0, 15)
RANGE_LED_VALUE = (0, LED_MAX_VALUE)
RANGE_REGISTER_VALUE = (0, 255)

REGISTERS_NAMES = {v: k for k, v in locals().items() if k.startswith("REGISTER_")}
for channel in range(LED_STRIP_COUNT):
    reg_base_addr = LED_STRIP_START_REGADR + channel * 4
    REGISTERS_NAMES[reg_base_addr] = f"REGISTER_LED{channel}_ON_L"
    REGISTERS_NAMES[reg_base_addr + 1] = f"REGISTER_LED{channel}_ON_H"
    REGISTERS_NAMES[reg_base_addr + 2] = f"REGISTER_LED{channel}_OFF_L"
    REGISTERS_NAMES[reg_base_addr + 3] = f"REGISTER_LED{channel}_OFF_H"


def get_register_name(regaddr: int) -> str:
    try:
        return REGISTERS_NAMES[regaddr]
    except KeyError:
        return "UNKNOWN"


def check_range(range: tuple[int | float, int | float], value: int | float):
    if value < range[0]:
        raise ValueError(f"Value must be greater than {range[0]}, got {value}")
    if value > range[1]:
        raise ValueError(f"Value must be less than {range[1]}, got {value}")


def value_low(value):
    return value & 0xFF


def value_high(value):
    return (value >> 8) & 0xFF


def get_led_off_registers(led_num: int) -> tuple[int, int]:
    """Calculate register number for LED pin
    :param led_num: the led number, typically 0-15
    """
    led_off_start = LED_STRIP_START_REGADR + 2
    low_address = led_off_start + (led_num * 4)
    return low_address, low_address + 1


class PWMDriver(Driver):
    registers = REGISTERS_NAMES

    def __init__(self, port: HardwarePort) -> None:
        super().__init__(port=port)

    def init(self):
        self.reset()

    def reset(self, frequency: float = 50):
        with self.port.session:
            self._log.debug(
                __("enter reset(frequency={frequency})", frequency=frequency)
            )
            self.set_frequency(frequency)
            self._write_to_register(REGISTER_ALL_LED_ON_L, [0])
            self._write_to_register(REGISTER_ALL_LED_ON_H, [0])
            self.start_all()
            self._log.debug("exit reset")

    def software_reset(self):
        with self.port.session:
            self._log.debug("enter software_reset")
            self._write_to_register(REGISTER_MODE_1, [0])  # reset
            self._log.debug("exit software_reset")

    def sleep_mode(self):
        with self.port.session:
            self._log.debug("enter sleep_mode")
            self._write_to_register(
                REGISTER_MODE_1, [MODE1_SLEEP_BIT | MODE1_ALLCALL_BIT]
            )
            self._log.debug("exit sleep_mode")

    def restart_mode(self):
        with self.port.session:
            self._log.debug("enter restart_mode")
            self._write_to_register(
                REGISTER_MODE_1, [MODE1_RESTART_BIT | MODE1_ALLCALL_BIT]
            )
            self._log.debug("exit restart_mode")

    def set_frequency(self, frequency: float):
        """Set the PWM frequency.

        Args:
            frequency (float): in Hz
        """
        with self.port.session:
            self._log.debug(
                __("enter set_frequency(frequency={frequency})", frequency=frequency)
            )
            check_range(RANGE_PWM_FREQUENCY, frequency)
            pre_scale = (
                round(OSCILLATOR_CLOCK_FREQUENCY / (LED_TOTAL_VALUES * frequency)) - 1
            )
            current_pre_scale = self._read_from_register(REGISTER_PRE_SCALE, 1)[0]
            if current_pre_scale != pre_scale:
                self.sleep_mode()
                self._write_to_register(REGISTER_PRE_SCALE, [pre_scale])
                self.restart_mode()
            self._log.debug("exit set_frequency")

    def get_duty_cycle(self, led_number: int) -> float:
        """
        Get the duty cycle of a given pin number.
        :param led_number:
        :return:
        """
        with self.port.session:
            self._log.debug(
                __(
                    "enter get_duty_cycle(led_number={led_number})",
                    led_number=led_number,
                )
            )
            check_range(RANGE_LED_NUMBER, led_number)
            led_off_l, led_off_h = get_led_off_registers(led_number)
            lsbr = self._read_from_register(led_off_l, 1)[0]
            msbr = self._read_from_register(led_off_h, 1)[0]
            duty_cycle_read = (
                (msbr & 0xF) << 8 | lsbr
            ) / LED_MAX_VALUE  # keep only first 4 bits of MSBR
            self._log.debug("exit get_duty_cycle")
            return duty_cycle_read

    def set_duty_cycle(self, led_number: int, duty_cycle: float):
        """Set the duty cycle of a given pin number.

        Args:
            led_number (int): Number of PWM channel from 0 to 15
            duty_cycle (float): Duty cycle from 0 to 1
        """
        with self.port.session:
            self._log.debug(
                __(
                    "enter set_duty_cycle(led_number={led_number}, duty_cycle={duty_cycle})",
                    led_number=led_number,
                    duty_cycle=duty_cycle,
                )
            )
            check_range(RANGE_LED_NUMBER, led_number)
            check_range((0, 1), duty_cycle)
            value = round(LED_MAX_VALUE * duty_cycle)
            led_off_l, led_off_h = get_led_off_registers(led_number)
            self._write_to_register(led_off_l, [value_low(value)])
            self._write_to_register(led_off_h, [value_high(value)])
            self._log.debug("exit set_duty_cycle")

    def stop_all(self):
        """
        Stop all PWM signals.
        """
        with self.port.session:
            self._write_to_register(
                REGISTER_MODE_1, [MODE1_SLEEP_BIT | MODE1_ALLCALL_BIT]
            )

    def start_all(self):
        """
        Start all PWM signals.
        """
        with self.port.session:
            self._log.debug("enter start_all")
            self._write_to_register(
                REGISTER_MODE_1, [MODE1_ALLCALL_BIT]
            )  # sleep mode off
            time.sleep(OSCILLATOR_STABILIZE_TIME)
            self._write_to_register(
                REGISTER_MODE_1, [MODE1_RESTART_BIT | MODE1_ALLCALL_BIT]
            )
            self._log.debug("exit start_all")

    def is_sleeping(self) -> bool:
        """Check if the PWM controller is sleeping.

        Returns:
            bool: True - if controller in sleep mode
        """
        with self.port.session:
            mode1_register = self._read_from_register(REGISTER_MODE_1, 1)[0]
            return mode1_register & MODE1_SLEEP_BIT > 0

    def _write_to_register(
        self, regaddr: int, data: Union[bytes, bytearray, list[int]]
    ):
        self.port.write_to(regaddr=regaddr, out=data)

    def _read_from_register(self, regaddr: int, readlen: int = 0) -> bytes:
        result = self.port.read_from(regaddr=regaddr, readlen=readlen)
        return result
