import time

from replifactory.drivers import HardwarePort, ThermometerDriver

REGISTER_TEMPERATURE_VALUE = 0x00
REGISTER_CONFIGURATION = 0x01
REGISTER_T_HYST_SETPOINT = 0x02
REGISTER_T_OS_SETPOINT = 0x03
REGISTER_ONE_SHOT = 0x04

TEMPERATURE_DATA_SIZE = 2
TEMPERATURE_RESOLUTION = 0.0625
TEMPERATURE_CONVERSION_TIME = 0.06  # 60ms
NOT_A_VALUE_BITS = 4

REGISTERS_NAMES = {
    value: name.removeprefix("REGISTER_")
    for name, value in locals().items()
    if name.startswith("REGISTER_")
}


class ADT75Driver(ThermometerDriver):
    registers = REGISTERS_NAMES

    def __init__(
        self,
        port: HardwarePort,
        one_shot_delay: float = TEMPERATURE_CONVERSION_TIME,
    ):
        super().__init__(port)
        self.one_shot_delay = one_shot_delay

    def read(self):
        with self.port.session:
            self.port.write([REGISTER_ONE_SHOT])
            time.sleep(self.one_shot_delay)
            data = self.port.read_from(REGISTER_ONE_SHOT, TEMPERATURE_DATA_SIZE)
            digital_temp = int.from_bytes(data, "big", signed=True) >> NOT_A_VALUE_BITS
            celsius_temp = digital_temp * TEMPERATURE_RESOLUTION
            return celsius_temp
