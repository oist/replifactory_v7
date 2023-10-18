import logging
from typing import Iterable
from replifactory.devices.stirrers_group import StirrersGroup

from usb.core import Device as UsbDevice

from replifactory.devices import Device
from replifactory.devices.laser import Laser
from replifactory.devices.optical_desity_sensor import OpticalDensitySensor
from replifactory.devices.photodiode import Photodiode
from replifactory.devices.pump import Pump
from replifactory.devices.step_motor import Motor
from replifactory.devices.stirrer import Stirrer
from replifactory.devices.thermometer import Thermometer
from replifactory.devices.valve import Valve
from replifactory.devices.valves_group import ValvesGroup
from replifactory.drivers.adt75 import REGISTERS_NAMES as ThermometerRegisters
from replifactory.drivers.adt75 import ThermometerDriver
from replifactory.drivers.ft2232h import FtdiDriver
from replifactory.drivers.l6470h import StepMotorDriver
from replifactory.drivers.mcp3421 import ADCDriver
from replifactory.drivers.pca9555 import ALL_PINS
from replifactory.drivers.pca9555 import REGISTERS_NAMES as IORegisters
from replifactory.drivers.pca9555 import IOPortDriver
from replifactory.drivers.pca9685 import REGISTERS_NAMES as PwmRegisters
from replifactory.drivers.pca9685 import PWMDriver

VAVLE_PWM_CHANNEL_START_ADDR = 8
VALVES_COUNT = 7
STIRRER_PWM_CHANNEL_START_ADDR = 0
STIRRERS_COUNT = VALVES_COUNT
PUMPS_COUNT = 4
SPI_FREQ = 1e4  # 10KHz
SPI_MODE = 3
SPI_INTERFACE = 1
SPI_TURBO = True
SPI_CS_COUNT = 4
I2C_FREQ = 5e4  # try 100e3
# I2C_FREQ = 100e3  # 100kHz
I2C_INTERFACE = 2
# MCP3421A0  1101 000
# MCP3421A0  1101 001
VIALS_COUNT = 7
I2C_PORT_PWM = 0x70  # PCA9685 [1110000]
# I2C_PORT_ADC = 0x6F
I2C_PORT_ADC = [*range(0x68, 0x70)]  # it could be in range from 0x68 to 0x6F
I2C_PORT_IO_ADC = 0x21  # PCA 9555
I2C_PORT_IO_LASER = 0x20  # PCA 9555
I2C_PORT_IO_STIRRERS = 0x25  # PCA 9555
I2C_PORT_THERMOMETER_1 = 0x48  # ADT75
I2C_PORT_THERMOMETER_2 = 0x49  # ADT75
I2C_PORT_THERMOMETER_3 = 0x4A  # ADT75

VALVE_OPEN_DUTY_CYCLE = 0.03
VALVE_CLOSED_DUTY_CYCLE = 0.12
VALVE_CHANGE_STATE_TIME = 1.5


class Machine(Device):
    # stirrers: List[Stirrer]
    # valves: List[Valve]
    # pumps: List[Pump]
    # optical_density_sensors: List[OpticalDensitySensor]
    # thermometers: List[Thermometers]
    # od_sensors: List[OpticalDensitySensor]
    # _pwm_driver: PWMDriver

    def __init__(self, usb_device: UsbDevice):
        self.log = logging.getLogger(__name__)
        self._devices = []
        ftdi_driver = FtdiDriver(
            usb_device=usb_device,
            spi_interface=SPI_INTERFACE,
            spi_cs_count=SPI_CS_COUNT,
            spi_freq=SPI_FREQ,
            spi_mode=SPI_MODE,
            spi_turbo=SPI_TURBO,
            i2c_interface=I2C_INTERFACE,
            i2c_freq=I2C_FREQ,
        )
        self._ftdi_driver = ftdi_driver
        self._pwm_driver = PWMDriver(
            ftdi_driver.get_i2c_port(I2C_PORT_PWM, "PWM", PwmRegisters)
        )
        stirrers = [
            Stirrer(pwm_channel=pwm_channel, driver=self._pwm_driver)
            for pwm_channel in reversed(
                range(
                    STIRRER_PWM_CHANNEL_START_ADDR,
                    STIRRER_PWM_CHANNEL_START_ADDR + STIRRERS_COUNT,
                )
            )
        ]
        self.stirrers = StirrersGroup(stirrers)
        self._devices += self.stirrers
        valves = [
            Valve(
                pwm_channel=pwm_channel,
                driver=self._pwm_driver,
                open_duty_cycle=VALVE_OPEN_DUTY_CYCLE,
                closed_duty_cycle=VALVE_CLOSED_DUTY_CYCLE,
                change_state_delay=VALVE_CHANGE_STATE_TIME,
                name=f"Valve {pwm_channel - VAVLE_PWM_CHANNEL_START_ADDR}",
            )
            for pwm_channel in range(
                VAVLE_PWM_CHANNEL_START_ADDR,
                VAVLE_PWM_CHANNEL_START_ADDR + VALVES_COUNT,
            )
        ]
        self.valves = ValvesGroup(valves)
        self._devices += self.valves
        self.pumps = [
            Pump(Motor(StepMotorDriver(ftdi_driver.get_spi_port(cs=cs))))
            for cs in range(PUMPS_COUNT)
        ]
        self._devices += self.pumps
        if isinstance(I2C_PORT_ADC, Iterable):
            try:
                i2c_adc_port = ftdi_driver.get_first_active_port(I2C_PORT_ADC, "ADC")
            except ConnectionError as e:
                self.log.error("Failed connection to ADC", exc_info=e)
                i2c_adc_port = None
        else:
            i2c_adc_port = ftdi_driver.get_i2c_port(I2C_PORT_ADC, "ADC")
        self._adc_driver = ADCDriver(i2c_adc_port)
        self._io_driver_adc = IOPortDriver(
            ftdi_driver.get_i2c_port(I2C_PORT_IO_ADC, "IO_ADC", IORegisters)
        )
        photodiodes = [
            Photodiode(
                diode_cs=cs,
                adc_driver=self._adc_driver,
                io_driver=self._io_driver_adc,
            )
            for cs in reversed(range(VIALS_COUNT))
        ]
        self._io_driver_laser = IOPortDriver(
            ftdi_driver.get_i2c_port(I2C_PORT_IO_LASER, "IO_LASERS", IORegisters)
        )
        lasers = [
            Laser(laser_cs=cs, io_driver=self._io_driver_laser)
            for cs in range(1, VIALS_COUNT * 2, 2)
        ]
        self.od_sensors = [
            OpticalDensitySensor(photodiode=photodiodes[i], laser=lasers[i])
            for i in range(VIALS_COUNT)
        ]
        self._devices += self.od_sensors
        # self._io_driver_stirrer = IOPortDriver(
        #     ftdi_driver.get_i2c_port(I2C_PORT_IO_STIRRERS, "IO_STIRRERS", IORegisters)
        # )
        self.thermometers = [
            Thermometer(
                driver=ThermometerDriver(
                    ftdi_driver.get_i2c_port(address, name, ThermometerRegisters)
                )
            )
            for address, name in {
                I2C_PORT_THERMOMETER_1: "THERMOMETER_1 (MB)",
                I2C_PORT_THERMOMETER_2: "THERMOMETER_2",
                I2C_PORT_THERMOMETER_3: "THERMOMETER_3",
            }.items()
        ]
        self._devices += self.thermometers

    def connect(self):
        self.configure_all()

    def disconnect(self):
        self._ftdi_driver.terminate()

    def configure_all(self):
        self.configure_pwm()
        # self.configure_pumps()
        self.configure_adc()
        self.configure_laser()

    def configure_pumps(self):
        for pump in self.pumps:
            pump.motor.configure()

    def configure_pwm(self):
        self._pwm_driver.reset()

    def configure_adc(self):
        self._io_driver_adc.set_output_mode(ALL_PINS)

    def configure_laser(self):
        self._io_driver_laser.set_output_mode(ALL_PINS)

    def get_pump(self, index: int) -> Pump:
        return self.pumps[index]

    def get_valve(self, index: int) -> Valve:
        return self.valves[index]

    def get_stirrer(self, index: int) -> Stirrer:
        return self.stirrers[index]

    def get_od_sensor(self, index: int) -> OpticalDensitySensor:
        return self.od_sensors[index]

    def get_thermometer(self, index: int) -> Thermometer:
        return self.thermometers[index]

    def test(self):
        for device in self._devices:
            try:
                test_result = "Ok" if device.test() else "Fail"
                self.log.info(f"Test {device.name}: {test_result}")
            except Exception as e:
                self.log.error(f"Test {device.name}: Fail", exc_info=e)

    def reset(self):
        for device in self._devices:
            device.reset()

    def configure(self):
        self.configure_all()
