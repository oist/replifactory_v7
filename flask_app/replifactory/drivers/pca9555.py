import logging
from dataclasses import dataclass
from typing import Union

from flask_app.replifactory.drivers import Driver, HardwarePort

log = logging.getLogger(__name__)


def binary_with_bracket(value: int, pin: int):
    pin += 1  # values from 0 to 15
    binary = bin(value)[2:].zfill(16)
    binary = list(binary)
    binary.insert(8, " ")
    if pin <= 8:
        pin += 1
    selected_pin_index = 16 - pin
    binary.insert(selected_pin_index, '[')
    binary.insert(selected_pin_index + 2, ']')
    return ''.join(binary)


def bitwise_or(items):
    result = items[0]
    for i in range(1, len(items)):
        result = result | items[i]
    return result


@dataclass
class Register:
    def __init__(self, address):
        self.address = address


REGISTER_INPUT_PORT_0 = Register(0x00)
REGISTER_INPUT_PORT_1 = Register(0x01)
REGISTER_OUTPUT_PORT_0 = Register(0x02)
REGISTER_OUTPUT_PORT_1 = Register(0x03)
REGISTER_POLARITY_INVERSION_PORT_0 = Register(0x04)
REGISTER_POLARITY_INVERSION_PORT_1 = Register(0x05)
REGISTER_CONFIGURATION_PORT_0 = Register(0x06)
REGISTER_CONFIGURATION_PORT_1 = Register(0x07)

POLARITY_INVERTED = 1
POLARITY_RETAINED = 0

PIN_INPUT = 1
PIN_OUTPUT = 0

IO0_0 = 1
IO0_1 = 1 << 1
IO0_2 = 1 << 2
IO0_3 = 1 << 3
IO0_4 = 1 << 4
IO0_5 = 1 << 5
IO0_6 = 1 << 6
IO0_7 = 1 << 7
IO1_0 = 1 << 8
IO1_1 = 1 << 9
IO1_2 = 1 << 10
IO1_3 = 1 << 11
IO1_4 = 1 << 12
IO1_5 = 1 << 13
IO1_6 = 1 << 14
IO1_7 = 1 << 15

ALL_PINS = bitwise_or(
    [value for name, value in locals().items() if name.startswith("IO")]
)
ALL_PINS_PORT_0 = bitwise_or(
    [value for name, value in locals().items() if name.startswith("IO0")]
)
ALL_PINS_PORT_1 = bitwise_or(
    [value for name, value in locals().items() if name.startswith("IO1")]
)

REGISTERS_NAMES = {
    value.address: name.removeprefix("REGISTER_")
    for name, value in locals().items()
    if name.startswith("REGISTER_")
}
PIN_MODES = {
    1: "In",
    0: "Out",
}
POLARITIES = {
    1: "Inverted",
    0: "Retained",
}


def get_register_name(regaddr: int) -> str:
    try:
        return REGISTERS_NAMES[regaddr]
    except KeyError:
        return "UNKNOWN"


class IOPortDriver(Driver):
    registers = REGISTERS_NAMES
    NUM_GPIO = 16

    def __init__(self, port: HardwarePort, init_config: int = 0x0000):
        super().__init__(port=port)
        self._input_value = None
        self._output_value = None
        self._config = init_config
        self._polarity = None

    def init(self):
        self.reset()

    def reset(self):
        self.write_config(self._config)

    @property
    def input_value(self):
        with self.port.session:
            if self._input_value is None:
                return self.read()
            return self._input_value

    @input_value.setter
    def input_value(self, value: int):
        self.write_to(REGISTER_INPUT_PORT_0, value.to_bytes(2, "little"))
        self._input_value = value

    @property
    def output_value(self):
        with self.port.session:
            if self._output_value is None:
                data = self.read_from(REGISTER_OUTPUT_PORT_0, 2)
                self._output_value = int.from_bytes(data, "little")
            return self._output_value

    @output_value.setter
    def output_value(self, value):
        self.write(value)

    @property
    def config(self):
        with self.port.session:
            if self._config is None:
                return self.read_config()
            return self._config

    @config.setter
    def config(self, value):
        self.write_config(value)

    def read_config(self):
        with self.port.session:
            config = self.read_from(REGISTER_CONFIGURATION_PORT_0, 2)
            self._config = int.from_bytes(config, "little")
            return self._config

    def write_config(self, value: int):
        if value > 0xFFFF:
            raise ValueError("Configuration value {value} bigger than 0xFFFF")
        with self.port.session:
            self.write_to(REGISTER_CONFIGURATION_PORT_0, value.to_bytes(2, "little"))
            self._config = value

    def set_input_mode(self, mask: int):
        self.write_config(self.config | mask)

    def set_output_mode(self, mask: int):
        self.write_config(self.config & ~mask)

    def read_polarity(self):
        with self.port.session:
            polarity = self.read_from(REGISTER_POLARITY_INVERSION_PORT_0, 2)
            self._polarity = int.from_bytes(polarity, "little")
            return self._polarity

    def write_polarity(self, value: int):
        with self.port.session:
            self.write_to(
                REGISTER_POLARITY_INVERSION_PORT_0, value.to_bytes(2, "little")
            )
            self._polarity = value

    def read(self):
        with self.port.session:
            input = self.read_from(REGISTER_INPUT_PORT_0, 2)
            self._input_value = int.from_bytes(input, "little")
            return self._input_value

    def write(self, value: int):
        with self.port.session:
            self.write_to(REGISTER_OUTPUT_PORT_0, value.to_bytes(2, "little"))
            self._output_value = value

    def write_l(self, value: int):
        with self.port.session:
            value = value & 0xFF
            self.write_to(REGISTER_OUTPUT_PORT_0, value.to_bytes(1, "little"))
            self._output_value = value if self._output_value is None else (self._output_value & 0xFF) + value

    def write_h(self, value: int):
        with self.port.session:
            value = value & 0xFF
            self.write_to(REGISTER_OUTPUT_PORT_1, value.to_bytes(1, "little"))
            self._output_value = (value << 8) if self._output_value is None else (self._output_value & 0xFF00) + (value << 8)

    def _changebit(self, bitmap, bit: int, value: int):
        if value == 0:
            return bitmap & ~(1 << bit)
        if value == 1:
            return bitmap | (1 << bit)
        raise ValueError(f"Value is {value} must be 1 or 0")

    def write_pin(self, pin: int, value: int):
        """
        Args:
            Pin(int): 0-7 = IO0_0 - IO0_7 ; 8-15 = IO1_0-IO1_7
            value(int): 0 = off ; 1 = on
        """
        if self.config >> pin & 1 == PIN_INPUT:
            raise ValueError(
                f"Pin {pin} at i2c address 0x{self.port.address:02X} is configed as INPUT"
            )
        new_value = self._changebit(self.output_value, pin, value)
        if log.isEnabledFor(logging.DEBUG):
            value_with_selected_pin = binary_with_bracket(new_value, pin)
            log.debug(
                f"Write pin {pin} at i2c address 0x{self.port.address:02X} value: {value_with_selected_pin}"
            )
        if pin <= 7:
            self.write_to(REGISTER_OUTPUT_PORT_0, [new_value & 0xFF])
        else:
            self.write_to(REGISTER_OUTPUT_PORT_1, [new_value >> 8])
        self._output_value = new_value

    def read_pin(self, pin: int):
        if self.config >> pin & 1 == PIN_OUTPUT:
            raise ValueError(
                f"Pin {pin} at i2c address 0x{self.port.address:02X} is configed as OUTPUT"
            )
        regaddr = REGISTER_INPUT_PORT_0 if pin <= 7 else REGISTER_INPUT_PORT_1
        input_register_data = self.read_from(regaddr, 1)
        result = (input_register_data[0] >> (pin % 8)) & 1
        return result

    def write_to(self, register: Register, data: Union[bytes, bytearray, list[int]]):
        regaddr = register.address
        with self.port.session:
            self.port.write_to(regaddr, data)

    def read_from(self, register: Register, readlen: int):
        with self.port.session:
            result = self.port.read_from(register.address, readlen)
            return result
