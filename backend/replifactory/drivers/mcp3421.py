import logging
import time

from replifactory.drivers import Driver, HardwarePort
from replifactory.util import ArrayOfBytesAsInt
from replifactory.util import BraceMessage as __


# CONFIGURATION REGISTER
# Bits:                         RDY | C1 | C0 | O/C | S1 | S0 | G1 | G0
# Default after Power-On Reset:  1  | 0  | 0  |  1  | 0  | 0  | 0  | 0
# C1, C0 - These bits are not effected for the MCP3421


class ADCDriver(Driver):
    def __init__(self, port: HardwarePort) -> None:
        super().__init__(port=port)
        self._gain = 1
        self._bitrate = 12
        self._continous_conversion = True

    def measure(self, gain=8, bitrate=16, continuous_conversion=False):
        self._log.debug(
            f"enter measure(gain={gain}, bitrate={bitrate}, continuous_conversion={continuous_conversion})"
        )
        with self.port.session:
            self.configure(
                gain=gain, bitrate=bitrate, continuous_conversion=continuous_conversion
            )

            bitrate_to_samples_per_second = {
                # resolution: data rate (samples per secod)
                12: 240,  # default
                14: 60,
                16: 15,
                18: 3.75,
            }
            new_data_is_ready = False
            data = []
            samples_per_second = bitrate_to_samples_per_second[bitrate]
            seconds_per_sample = 1 / samples_per_second
            for _ in range(100):  # try reading until conversion ready
                self._log.debug(f"wait {seconds_per_sample:2f} seconds to complete sample")
                time.sleep(seconds_per_sample)

                data, config = self.read()

                new_data_is_ready = (
                    config[0] < 128
                )  # if bit 7 (ready bit) is 1: NOT READY YET!
                if new_data_is_ready:
                    break

        assert new_data_is_ready
        # TODO: replace to bit operators
        digital_signal = int.from_bytes(data, "big", signed=True)
        lsb_mv = (
            2 * 2.048 / 2**bitrate * 1000 / gain
        )  # least significant bit millivolts
        millivolts = lsb_mv * digital_signal
        millivolts = round(millivolts, 10)
        self._log.debug(f"exit measure return total: {millivolts} mv, LSB: {lsb_mv} mv")
        return millivolts, lsb_mv

    def configure(self, gain=8, bitrate=16, continuous_conversion=False):
        # RDY bit
        ready_bit = 0b10000000  # start conversion in one-shot mode
        # O/C bit
        if continuous_conversion:
            conversion_mode_bit = 0b00010000  # Continious Conversion Mode (default)
        else:
            conversion_mode_bit = 0b00000000  # One-shot conversion mode
        # S1-S0 bits (Sample Rate Selection)
        bitrate_bits = {
            12: 0b0000,
            14: 0b0100,
            16: 0b1000,
            18: 0b1100,
        }
        # G1-G0 bits (PGA Gain Selection)
        gain_bits = {
            1: 0b00,
            2: 0b01,
            4: 0b10,
            8: 0b11,
        }
        # ADC Configuration byte: <RDY>00<O/C><S1><S0><G1><G0>
        configuration = (
            ready_bit | conversion_mode_bit | bitrate_bits[bitrate] | gain_bits[gain]
        )
        with self.port.session:
            self.write(configuration)
            self._gain = gain
            self._bitrate = bitrate
            self._continous_conversion = continuous_conversion

    def write(self, configuration: int):
        with self.port.session:
            self._log.debug(
                __(
                    "W i2c: ADC 0x{port_addr:02X} configuration: b{config:08b} ({config})",
                    port_addr=self.port.address,
                    config=configuration,
                )
            )
            self.port.write([configuration])

    def read(self):
        with self.port.session:
            response = self.port.read(4)  # read 4 bytes from ADC
            data = response[:3] if self._bitrate == 18 else response[:2]
            config = response[3:]
            self._log.debug(
                __(
                    "R i2c: ADC 0x{port_addr:02X} configuration: b{config:08b} ({config}) value: {value} [{hex_value}] data: [{hex_data}]",
                    port_addr=self.port.address,
                    config=int.from_bytes(config, "little"),
                    value=ArrayOfBytesAsInt(data),
                    hex_value=data.hex(" ").upper(),
                    hex_data=response.hex(" ").upper(),
                )
            )
        return data, config
