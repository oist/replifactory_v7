import logging
import threading
from time import sleep
from typing import Iterable, Optional
from flask_app.replifactory.usb_manager import usbManager

from usb.core import Device as UsbDevice

from flask_app.replifactory.devices import Device
from flask_app.replifactory.devices.laser import Laser
from replifactory.devices.optical_density_sensor import OpticalDensitySensor
from flask_app.replifactory.devices.photodiode import Photodiode
from flask_app.replifactory.devices.pump import Pump
from flask_app.replifactory.devices.step_motor import Motor
from flask_app.replifactory.devices.stirrer import Stirrer
from flask_app.replifactory.devices.stirrers_group import StirrersGroup
from flask_app.replifactory.devices.thermometer import Thermometer
from flask_app.replifactory.devices.valve import Valve
from flask_app.replifactory.devices.valves_group import ValvesGroup
from flask_app.replifactory.drivers.adt75 import REGISTERS_NAMES as ThermometerRegisters
from flask_app.replifactory.drivers.adt75 import ThermometerDriver
from flask_app.replifactory.drivers.ft2232h import FtdiDriver
from flask_app.replifactory.drivers.l6470h import StepMotorDriver
from flask_app.replifactory.drivers.mcp3421 import ADCDriver
from flask_app.replifactory.drivers.pca9555 import ALL_PINS
from flask_app.replifactory.drivers.pca9555 import REGISTERS_NAMES as IORegisters
from flask_app.replifactory.drivers.pca9555 import IOPortDriver
from flask_app.replifactory.drivers.pca9685 import REGISTERS_NAMES as PwmRegisters
from flask_app.replifactory.drivers.pca9685 import PWMDriver
from flask_app.replifactory.events import Events, eventManager

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


class MachineDeviceCallback:
    def on_comm_state_change(self, state):
        pass


class Machine(Device):
    STATE_NONE = 0
    STATE_FINDING_MACHINE = 1
    STATE_CONNECTING = 2
    STATE_SELF_TESTING = 3
    STATE_OPERATIONAL = 4
    STATE_STARTING = 5
    STATE_WORKING = 6
    STATE_PAUSED = 7
    STATE_PAUSING = 8
    STATE_RESUMING = 9
    STATE_FINISHING = 10
    STATE_CLOSED = 11
    STATE_ERROR = 12
    STATE_CLOSED_WITH_ERROR = 13
    STATE_RECONNECTING = 14
    STATE_CANCELLING = 15

    # be sure to add anything here that signifies an operational state
    OPERATIONAL_STATES = (
        STATE_WORKING,
        STATE_STARTING,
        STATE_OPERATIONAL,
        STATE_PAUSED,
        STATE_CANCELLING,
        STATE_PAUSING,
        STATE_RESUMING,
        STATE_FINISHING,
    )

    # be sure to add anything here that signifies a working state
    WORKING_STATES = (
        STATE_STARTING,
        STATE_WORKING,
        STATE_CANCELLING,
        STATE_PAUSING,
        STATE_RESUMING,
        STATE_FINISHING,
    )
    # stirrers: List[Stirrer]
    # valves: List[Valve]
    # pumps: List[Pump]
    # optical_density_sensors: List[OpticalDensitySensor]
    # thermometers: List[Thermometers]
    # od_sensors: List[OpticalDensitySensor]
    # _pwm_driver: PWMDriver

    def __init__(
        self,
        usb_device: Optional[UsbDevice] = None,
        callback: Optional[MachineDeviceCallback] = None,
        reconnect: bool = True,
        **kwargs,
    ):
        self._state = None
        self._errorValue = ""
        self._logger = logging.getLogger(__name__)
        self._connection_closing = False
        self._callback = callback or MachineDeviceCallback()
        self._usb_device = usb_device
        self._serial = usb_device.serial_number if usb_device else None
        self._reconnect = reconnect
        self.log = logging.getLogger(__name__)

        # monitoring thread
        self._monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitor, name="machine._monitor"
        )
        self.monitoring_thread.daemon = True

    def _monitor(self):
        self.connect()
        self._say_hello()
        while self._monitoring_active:
            try:
                if (
                    self._state in self.OPERATIONAL_STATES
                    and not self._ftdi_driver._ftdi.is_connected
                ):
                    if self._state in self.WORKING_STATES:
                        self.close(is_error=True)
                    else:
                        self.close()
                sleep(1)
            except Exception:
                self._logger.exception(
                    "Something crashed inside the serial connection loop, please report this in Replifactory's bug tracker:"
                )

                errorMsg = "See octoprint.log for details"
                self._logger.error(errorMsg)
                self._errorValue = errorMsg
                eventManager().fire(
                    Events.ERROR, {"error": self.get_error_string(), "reason": "crash"}
                )
                self.close(is_error=True)
        self._logger.info("Connection closed, closing down monitor")

    def _say_hello(self):
        pass

    def _set_state(self, new_state):
        self._state = new_state
        self._callback.on_comm_state_change(new_state)

    def _changeState(self, newState):
        if self._state == newState:
            return

        oldState = self.get_state_string()
        self._state = newState

        text = 'Changing monitoring state from "{}" to "{}"'.format(
            oldState, self.get_state_string()
        )
        # self._log(text)
        self._logger.info(text)
        self._callback.on_comm_state_change(newState)

    def get_state_id(self, state=None):
        if state is None:
            state = self._state

        possible_states = list(
            filter(lambda x: x.startswith("STATE_"), self.__class__.__dict__.keys())
        )
        for possible_state in possible_states:
            if getattr(self, possible_state) == state:
                return possible_state[len("STATE_") :]

        return "UNKNOWN"

    def get_state_string(self, state=None):
        state = state or self._state
        if state == self.STATE_NONE:
            return "Offline"
        elif state == self.STATE_FINDING_MACHINE:
            return "Finding connected machine"
        elif state == self.STATE_CONNECTING:
            return "Connecting"
        elif state == self.STATE_SELF_TESTING:
            return "Self testing"
        elif state == self.STATE_OPERATIONAL:
            return "Operational"
        elif state == self.STATE_STARTING:
            return "Starting"
        elif state == self.STATE_WORKING:
            return "Working"
        elif state == self.STATE_PAUSED:
            return "Paused"
        elif state == self.STATE_PAUSING:
            return "Pausing"
        elif state == self.STATE_RESUMING:
            return "Resuming"
        elif state == self.STATE_FINISHING:
            return "Finishing"
        elif state == self.STATE_CLOSED:
            return "Closed"
        elif state == self.STATE_ERROR:
            return "Error"
        elif state == self.STATE_CLOSED_WITH_ERROR:
            return "Offline after error"
        elif state == self.STATE_CANCELLING:
            return "Cancelling"
        elif state == self.STATE_RECONNECTING:
            return "Reconnecting"
        return f"Unknown State ({self._state})"

    def get_error_string(self):
        return self._errorValue

    def connect(self):
        self._set_state(self.STATE_CONNECTING)
        self._usb_device = self._usb_device or usbManager().find_device(serial_number=self._serial)
        eventManager().fire(Events.MACHINE_CONNECTING, self)
        self._devices = []

        ftdi_driver = FtdiDriver(
            usb_device=self._usb_device,
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

        self._ftdi_driver.connect()

        eventManager().subscribe(Events.USB_DISCONNECTED, self._on_usb_disconnected)
        eventManager().subscribe(Events.USB_CONNECTED, self._on_usb_connected)
        # self.configure_all()
        self._set_state(self.STATE_OPERATIONAL)
        eventManager().fire(Events.MACHINE_CONNECTED, self)

    def disconnect(self):
        self.close()

    def _on_usb_disconnected(self, event, usb_device):
        if self._serial != usb_device.serial_number:
            return

        if self._reconnect:
            self._terminate_connection()
            self._set_state(self.STATE_RECONNECTING)
        else:
            self.close(is_error=self._state in self.WORKING_STATES)

    def _on_usb_connected(self, event, usb_device):
        if usb_device.serial_number and usb_device.serial_number != self._serial:
            return

        if self._state == self.STATE_RECONNECTING:
            self._usb_device = usb_device
            self.connect()

    def start(self):
        self.connect()

    def close(self, is_error=False, *args, **kwargs):
        """
        Closes the connection to the printer.
        """
        if self._connection_closing:
            return
        self._connection_closing = True

        eventManager().unsubscribe(Events.USB_DISCONNECTED, self._on_usb_disconnected)
        eventManager().unsubscribe(Events.USB_CONNECTED, self._on_usb_connected)

        self._monitoring_active = False
        try:
            self._terminate_connection(raise_exception=True)
        except Exception:
            self._changeState(self.STATE_CLOSED_WITH_ERROR)
        else:
            self._changeState(self.STATE_CLOSED)

    def _terminate_connection(self, raise_exception=False):
        if self._ftdi_driver is not None:
            try:
                self._ftdi_driver.close()
            except Exception as exc:
                self._logger.exception("Error while trying to close serial port")
                if raise_exception:
                    raise exc
            self._ftdi_driver = None
            self._usb_device = None

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

    def isClosedOrError(self):
        return self._state in (
            self.STATE_ERROR,
            self.STATE_CLOSED,
            self.STATE_CLOSED_WITH_ERROR,
        )

    def isOperational(self):
        return self._state in self.OPERATIONAL_STATES

    def isWorking(self):
        return self._state in self.WORKING_STATES

    def isCancelling(self):
        return self._state == self.STATE_CANCELLING

    def isPausing(self):
        return self._state == self.STATE_PAUSING

    def isPaused(self):
        return self._state == self.STATE_PAUSED

    def isResuming(self):
        return self._state == self.STATE_RESUMING

    def isFinishing(self):
        return self._state == self.STATE_FINISHING

    def isError(self):
        return self._state in (self.STATE_ERROR, self.STATE_CLOSED_WITH_ERROR)

    def isBusy(self):
        return (
            self.isWorking()
            or self.isPaused()
            or self._state in (self.STATE_CANCELLING, self.STATE_PAUSING)
        )
