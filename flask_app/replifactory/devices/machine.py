import logging
import queue
import threading
from collections import OrderedDict
from time import sleep
import time
from typing import Callable, Dict, List, Optional, Tuple, Type, Union
from flask_app.replifactory.devices.vial import Vial

from usb.core import Device as UsbDevice

from flask_app.replifactory.devices import Device, DeviceCallback
from flask_app.replifactory.devices.laser import Laser
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
from flask_app.replifactory.drivers.pca9555 import REGISTERS_NAMES as IORegisters
from flask_app.replifactory.drivers.pca9555 import IOPortDriver
from flask_app.replifactory.drivers.pca9685 import REGISTERS_NAMES as PwmRegisters
from flask_app.replifactory.drivers.pca9685 import PWMDriver
from flask_app.replifactory.events import Events, eventManager
from flask_app.replifactory.usb_manager import usbManager
from replifactory.devices.optical_density_sensor import OpticalDensitySensor
from replifactory.drivers import Driver
from replifactory.util import CountedEvent, JobQueue, TypeAlreadyInQueue
from replifactory.util.comm import (
    AwaitConditionQueueMarker,
    CommandQueue,
    QueueMarker,
    SendQueue,
    SendQueueMarker,
)

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
VALVE_CHANGE_STATE_TIME = 0.5


class MachineCallback:
    def on_comm_state_change(self, state):
        pass

    def on_change_device_data(self, data):
        pass


class LongtimeMachineCommand(AwaitConditionQueueMarker):
    pass


class MachineCommand(SendQueueMarker):
    pass


class Machine(Device, DeviceCallback):
    # stirrers: List[Stirrer]
    # valves: List[Valve]
    # pumps: List[Pump]
    # optical_density_sensors: List[OpticalDensitySensor]
    # thermometers: List[Thermometers]
    # od_sensors: List[OpticalDensitySensor]
    # _pwm_driver: PWMDriver

    def __init__(
        self,
        # usb_device: Optional[UsbDevice] = None,
        callback: Optional[MachineCallback] = None,
        reconnect: bool = True,
        start: bool = True,
        **kwargs,
    ):
        self._lock = threading.RLock()
        self._state = None
        self._errorValue = ""
        self._logger = logging.getLogger(__name__)
        self._connection_closing = False
        self._machine_callback: MachineCallback = callback or MachineCallback()
        # self._usb_device = usb_device
        # self._serial = usb_device.serial_number if usb_device else None
        self._usb_device = None
        self._serial = None
        self._reconnect = reconnect
        self.log = logging.getLogger(__name__)

        self._job_queue = JobQueue()
        self._command_queue = CommandQueue()
        self._send_queue = SendQueue()

        self._sendingLock = threading.RLock()

        self._job_on_hold = CountedEvent()

        # monitoring thread
        self._monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitor, name="machine._monitor"
        )
        self.monitoring_thread.daemon = True
        self._devices: Dict[str, Device] = OrderedDict()
        self._drivers: list[Driver] = []

        self._ack_max = 1  # settings().getInt(["serial", "ackMax"])
        self._clear_to_send = CountedEvent(
            name="comm.clear_to_send", minimum=None, maximum=self._ack_max
        )
        # sending thread
        self._cancel_await_condition = False
        self._send_queue_active = True
        self.sending_thread = threading.Thread(
            target=self._send_loop, name="comm.sending_thread"
        )
        self.sending_thread.daemon = True

        self._ftdi_driver = FtdiDriver(
            spi_interface=SPI_INTERFACE,
            spi_cs_count=SPI_CS_COUNT,
            spi_freq=SPI_FREQ,
            spi_mode=SPI_MODE,
            spi_turbo=SPI_TURBO,
            i2c_interface=I2C_INTERFACE,
            i2c_freq=I2C_FREQ,
        )

        self._pumps: list[Pump] = []
        # it's important to init pump drivers before valves
        for cs in range(PUMPS_COUNT):
            spi_port_callback = self._ftdi_driver.get_spi_port_callback(cs=cs)
            step_motor_driver = StepMotorDriver(get_port=spi_port_callback)
            motor = Motor(step_motor_driver)
            pump = Pump(motor, name=f"Pump {cs + 1}", callback=self)
            self._pumps.append(pump)
            self._devices[pump.id] = pump
            self._drivers += [step_motor_driver]

        pwm_port_callback = self._ftdi_driver.get_i2c_port_callback(
            I2C_PORT_PWM, "PWM", PwmRegisters
        )
        pwm_driver = PWMDriver(get_port=pwm_port_callback)
        self._drivers += [pwm_driver]
        stirrers = [
            Stirrer(
                pwm_channel=pwm_channel,
                driver=pwm_driver,
                name=f"Stirrer {i+1}",
                callback=self,
            )
            for i, pwm_channel in enumerate(
                reversed(
                    range(
                        STIRRER_PWM_CHANNEL_START_ADDR,
                        STIRRER_PWM_CHANNEL_START_ADDR + STIRRERS_COUNT,
                    )
                )
            )
        ]
        for stirrer in stirrers:
            self._devices[stirrer.id] = stirrer

        stirrers_group = StirrersGroup(stirrers)
        self._devices[stirrers_group.id] = stirrers_group

        valves = [
            Valve(
                pwm_channel=pwm_channel,
                driver=pwm_driver,
                open_duty_cycle=VALVE_OPEN_DUTY_CYCLE,
                closed_duty_cycle=VALVE_CLOSED_DUTY_CYCLE,
                change_state_delay=VALVE_CHANGE_STATE_TIME,
                name=f"Valve {pwm_channel - VAVLE_PWM_CHANNEL_START_ADDR + 1}",
                callback=self,
                init_state=Valve.States.STATE_CLOSE,
            )
            for pwm_channel in range(
                VAVLE_PWM_CHANNEL_START_ADDR,
                VAVLE_PWM_CHANNEL_START_ADDR + VALVES_COUNT,
            )
        ]
        self._valves = valves
        for valve in valves:
            self._devices[valve.id] = valve

        valves_group = ValvesGroup(valves)
        self._devices[valves_group.id] = valves_group

        laser_port_callback = self._ftdi_driver.get_i2c_port_callback(
            I2C_PORT_IO_LASER, "IO_LASERS", IORegisters
        )
        io_driver_laser = IOPortDriver(get_port=laser_port_callback)
        self._drivers += [io_driver_laser]
        lasers = [
            Laser(laser_cs=cs, io_driver=io_driver_laser)
            for cs in range(1, VIALS_COUNT * 2, 2)
        ]
        for laser in lasers:
            self._devices[laser.id] = laser

        adc_port_callback = self._ftdi_driver.get_first_active_i2c_port_callback(
            I2C_PORT_ADC, "ADC"
        )
        # if isinstance(I2C_PORT_ADC, Iterable):
        #     try:
        #         i2c_adc_port = ftdi_driver.get_first_active_port(I2C_PORT_ADC, "ADC")
        #     except ConnectionError as e:
        #         self.log.error("Failed connection to ADC", exc_info=e)
        #         i2c_adc_port = None
        # else:
        #     i2c_adc_port = ftdi_driver.get_i2c_port(I2C_PORT_ADC, "ADC")
        # if i2c_adc_port:
        io_port_callback = self._ftdi_driver.get_i2c_port_callback(
            I2C_PORT_IO_ADC, "IO_ADC", IORegisters
        )
        adc_driver = ADCDriver(get_port=adc_port_callback)
        self._drivers += [adc_driver]
        io_driver_adc = IOPortDriver(get_port=io_port_callback)
        self._drivers += [io_driver_adc]
        photodiodes = [
            Photodiode(
                diode_cs=cs,
                adc_driver=adc_driver,
                io_driver=io_driver_adc,
            )
            for cs in reversed(range(VIALS_COUNT))
        ]
        od_sensors = [
            OpticalDensitySensor(
                photodiode=photodiodes[i],
                laser=lasers[i],
                callback=self,
                name=f"Optical Density Sensor {i+1}",
            )
            for i in range(VIALS_COUNT)
        ]
        for od_sensor in od_sensors:
            self._devices[od_sensor.id] = od_sensor

        self._vials = []
        for i in range(VIALS_COUNT):
            num = i + 1
            vial = Vial(
                name=f"Vial {num}",
                valve=self._get_valve(f"valve-{num}"),
                stirrer=self._get_stirrer(f"stirrer-{num}"),
                od_sensor=self._get_od_sensor(f"optical-density-sensor-{num}"),
                media_pump=self._get_pump("pump-1"),
                drug_pump=self._get_pump("pump-2"),
                waste_pump=self._get_pump("pump-4"),
                callback=self,
            )
            self._devices[vial.id] = vial
            self._vials.append(vial)

        thermometers = []
        for address, name in {
            I2C_PORT_THERMOMETER_1: "THERMOMETER_1 (MB)",
            I2C_PORT_THERMOMETER_2: "THERMOMETER_2",
            I2C_PORT_THERMOMETER_3: "THERMOMETER_3",
        }.items():
            thermometer_driver = ThermometerDriver(
                get_port=self._ftdi_driver.get_i2c_port_callback(
                    address, name, ThermometerRegisters
                )
            )
            self._drivers += [thermometer_driver]
            thermometers += [
                Thermometer(
                    driver=thermometer_driver,
                    name=f"Thermometer 0x{address:02X}",
                    callback=self,
                )
            ]
        for thermometer in thermometers:
            self._devices[thermometer.id] = thermometer

        if start:
            self.start()

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

    def _send_loop(self):
        """
        The send loop is responsible of sending commands in ``self._send_queue`` over the line, if it is cleared for
        sending
        """

        self._clear_to_send.wait()

        while self._send_queue_active:
            try:
                # wait until we have something in the queue
                try:
                    entry = self._send_queue.get()
                except queue.Empty:
                    # I haven't yet been able to figure out *why* this can happen but according to #3096 and SERVER-2H
                    # an Empty exception can fly here due to resend_active being True but nothing being in the resend
                    # queue of the send queue. So we protect against this possibility...
                    continue

                try:
                    # make sure we are still active
                    if not self._send_queue_active:
                        break

                    # fetch command, command type and optional linenumber and sent callback from queue
                    command, linenumber, command_type, on_sent, processed, tags = entry

                    if isinstance(command, AwaitConditionQueueMarker):
                        command.run()
                        timeout_time = (
                            time.monotonic() + command.timeout if command.timeout else 0
                        )
                        wait_time = command.interval

                        while self._send_queue_active and not command.done():
                            if self._cancel_await_condition:
                                self._cancel_await_condition = False
                                command.cancel()
                                continue
                            if command.timeout:
                                now = time.monotonic()
                                if now > timeout_time:
                                    command.on_timeout()
                                    break
                                if now + command.interval > timeout_time:
                                    wait_time = timeout_time - now
                            time.sleep(wait_time)
                        self._continue_sending()
                        continue

                    elif isinstance(command, SendQueueMarker):
                        command.run()
                        self._continue_sending()
                        continue

                    # trigger "sent" phase and use up one "ok"
                    if on_sent is not None and callable(on_sent):
                        # we have a sent callback for this specific command, let's execute it now
                        on_sent()
                finally:
                    # no matter _how_ we exit this block, we signal that we
                    # are done processing the last fetched queue entry
                    self._send_queue.task_done()

                # now we just wait for the next clear and then start again
                self._clear_to_send.wait()
            except Exception:
                self._logger.exception("Caught an exception in the send loop")
        self._logger.info("Closing down send loop")

    @property
    def _active(self):
        return self._monitoring_active and self._send_queue_active

    @property
    def job_on_hold(self):
        return self._job_on_hold.counter > 0

    def _continue_sending(self):
        # Ensure we have at least one line in the send queue, but don't spam it
        while self._active and not self._send_queue.qsize():
            job_active = self._state in (
                self.States.STATE_STARTING,
                self.States.STATE_WORKING,
            )

            if self._send_from_command_queue():
                # we found something in the command queue to send
                return True

            elif self.job_on_hold:
                # job is on hold, that means we must not send from either job queue or file
                return False

            elif self._send_from_job_queue():
                # we found something in the job queue to send
                return True

            # elif job_active and self._send_from_job():
            #     # we sent the next line from the file
            #     return True

            elif not job_active:
                # nothing sent but also no job active, so we can just return false
                return False

            self._logger.debug(
                "No command enqueued on ok while working, doing another iteration"
            )

    def _send_from_job_queue(self):
        try:
            line, cmd_type, on_sent, tags = self._job_queue.get_nowait()
            result = self._sendCommand(
                line, cmd_type=cmd_type, on_sent=on_sent, tags=tags
            )
            if result:
                # line from script sent, return true
                return True
        except queue.Empty:
            pass

        return False

    def _send_from_command_queue(self):
        # We loop here to make sure that if we do NOT send the first command
        # from the queue, we'll send the second (if there is one). We do not
        # want to get stuck here by throwing away commands.
        while True:
            # if self.isStreaming():
            #     # command queue irrelevant
            #     return False

            try:
                entry = self._command_queue.get(block=False)
            except queue.Empty:
                # nothing in command queue
                return False

            try:
                if isinstance(entry, tuple):
                    if not len(entry) == 4:
                        # something with that entry is broken, ignore it and fetch
                        # the next one
                        continue
                    cmd, cmd_type, callback, tags = entry
                else:
                    cmd = entry
                    cmd_type = None
                    callback = None
                    tags = None

                if self._sendCommand(
                    cmd, cmd_type=cmd_type, on_sent=callback, tags=tags
                ):
                    # we actually did add this cmd to the send queue, so let's
                    # return, we are done here
                    return True
            finally:
                self._command_queue.task_done()

    # def _process_registered_message(
    #     self, line, feedback_matcher, feedback_controls, feedback_errors
    # ):
    #     feedback_match = feedback_matcher.search(line)
    #     if feedback_match is None:
    #         return

    #     for match_key in feedback_match.groupdict():
    #         try:
    #             feedback_key = match_key[len("group") :]
    #             if (
    #                 feedback_key not in feedback_controls
    #                 or feedback_key in feedback_errors
    #                 or feedback_match.group(match_key) is None
    #             ):
    #                 continue
    #             matched_part = feedback_match.group(match_key)

    #             if feedback_controls[feedback_key]["matcher"] is None:
    #                 continue

    #             match = feedback_controls[feedback_key]["matcher"].search(matched_part)
    #             if match is None:
    #                 continue

    #             outputs = {}
    #             for template_key, template in feedback_controls[feedback_key][
    #                 "templates"
    #             ].items():
    #                 try:
    #                     output = template.format(*match.groups())
    #                 except KeyError:
    #                     output = template.format(**match.groupdict())
    #                 except Exception:
    #                     self._logger.debug(
    #                         "Could not process template {}: {}".format(
    #                             template_key, template
    #                         ),
    #                         exc_info=1,
    #                     )
    #                     output = None

    #                 if output is not None:
    #                     outputs[template_key] = output
    #             eventManager().fire(
    #                 Events.REGISTERED_MESSAGE_RECEIVED,
    #                 {"key": feedback_key, "matched": matched_part, "outputs": outputs},
    #             )
    #         except Exception:
    #             self._logger.exception(
    #                 "Error while trying to match feedback control output, disabling key {key}".format(
    #                     key=match_key
    #                 )
    #             )
    #             feedback_errors.append(match_key)

    def _say_hello(self):
        pass

    def _set_state(self, new_state):
        self._state = new_state
        self._machine_callback.on_comm_state_change(new_state)

    def _changeState(self, newState):
        if self._state == newState:
            return

        oldState = self.get_state_string()
        self._state = newState

        text = 'Changing monitoring state from "{}" to "{}"'.format(
            oldState, self.get_state_string()
        )
        self._logger.info(text)
        self._machine_callback.on_comm_state_change(newState)

    def get_error_string(self):
        return self._errorValue

    def connect(self, usb_device: Optional[UsbDevice] = None):
        with self._lock:
            if self._usb_device is not None:
                return

            self._set_state(self.States.STATE_CONNECTING)
            usb_device = usb_device or usbManager().find_device(
                serial_number=self._serial
            )
            if usb_device is None:
                return

            eventManager().fire(Events.MACHINE_CONNECTING, self)

            self._ftdi_driver.connect(usb_device)
            self._usb_device = usb_device
            self._serial = usb_device.serial_number
            eventManager().subscribe(Events.USB_DISCONNECTED, self._on_usb_disconnected)
            eventManager().subscribe(Events.USB_CONNECTED, self._on_usb_connected)

            for driver in self._drivers:
                driver.init()

            for device in self._devices.values():
                device.connect()

            self._set_state(self.States.STATE_OPERATIONAL)
            eventManager().fire(Events.MACHINE_CONNECTED, self)
            self._clear_to_send.set()

    def disconnect(self):
        self.close()

    def on_device_state_change(self, device: Device, state):
        self._machine_callback.on_change_device_data(device.get_data())
        eventManager().fire(Events.DEVICE_STATE_CHANGED, (device, state))

    def _on_usb_disconnected(self, event, usb_device):
        if self._serial != usb_device.serial_number:
            return

        if self._reconnect:
            self._terminate_connection()
            self._set_state(self.States.STATE_RECONNECTING)
        else:
            self.close(is_error=self._state in self.WORKING_STATES)

    def _on_usb_connected(self, event, usb_device):
        if usb_device.serial_number and usb_device.serial_number != self._serial:
            return

        if self._state == self.States.STATE_RECONNECTING:
            self.connect(usb_device=usb_device)

    def start(self):
        self.sending_thread.start()

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
            self._changeState(self.States.STATE_CLOSED_WITH_ERROR)
        else:
            self._changeState(self.States.STATE_CLOSED)

    def _terminate_connection(self, raise_exception=False):
        if self._usb_device is not None:
            try:
                self._ftdi_driver.close()
            except Exception as exc:
                self._logger.exception("Error while trying to close serial port")
                if raise_exception:
                    raise exc
            # self._ftdi_driver = None
            self._usb_device = None

    # def configure_all(self):
    #     self.configure_pwm()
    #     # self.configure_pumps()
    #     self.configure_adc()
    #     self.configure_laser()

    # def configure_pumps(self):
    #     # for pump in self.pumps:
    #     #     pump.motor.read_state()
    #     pass

    # def configure_pwm(self):
    #     self._pwm_driver.reset()

    # def configure_adc(self):
    #     self._io_driver_adc.set_output_mode(ALL_PINS)

    # def configure_laser(self):
    #     self._io_driver_laser.set_output_mode(ALL_PINS)

    # def get_pump(self, index: int) -> Pump:
    #     # return self.pumps[index]
    #     pass

    # def get_valve(self, index: int) -> Valve:
    #     return self.valves[index]

    # def get_stirrer(self, index: int) -> Stirrer:
    #     return self.stirrers[index]

    # def get_od_sensor(self, index: int) -> OpticalDensitySensor:
    #     return self.od_sensors[index]

    # def get_thermometer(self, index: int) -> Thermometer:
    #     return self.thermometers[index]

    def test(self):
        for device in self._devices.values():
            try:
                test_result = "Ok" if device.test() else "Fail"
                self.log.info(f"Test {device.name}: {test_result}")
            except Exception as e:
                self.log.error(f"Test {device.name}: Fail", exc_info=e)

    def sendCommand(
        self,
        cmd: QueueMarker,
        cmd_type=None,
        part_of_experiment=False,
        processed=False,
        force=False,
        on_sent=None,
        tags=None,
    ):
        if tags is None:
            tags = set()

        if part_of_experiment:
            self._job_queue.put((cmd, cmd_type, on_sent, tags | {"source:experiment"}))
            return True
        elif (
            self.isWorking()
            # and not self.job_on_hold
            and not force
        ):
            try:
                self._command_queue.put(
                    (cmd, cmd_type, on_sent, tags), item_type=cmd_type
                )
                return True
            except TypeAlreadyInQueue as e:
                self._logger.debug("Type already in command queue: " + e.type)
                return False
        elif self.isOperational() or force:
            return self._sendCommand(cmd, cmd_type=cmd_type, on_sent=on_sent, tags=tags)

    def _sendCommand(self, cmd: QueueMarker, cmd_type=None, on_sent=None, tags=None):
        # Make sure we are only handling one sending job at a time
        with self._sendingLock:
            if self._usb_device is None:
                return False

            self._enqueue_for_sending(
                cmd, command_type=cmd_type, on_sent=on_sent, tags=tags
            )
            return True

    def _sendCommands(
        self,
        commands: List[
            Tuple[QueueMarker, Optional[str], Optional[Callable[..., None]], Dict[str, str]]
        ],
    ):
        # Make sure we are only handling one sending job at a time
        with self._sendingLock:
            if self._usb_device is None:
                return False

            for cmd, cmd_type, on_sent, tags in commands:
                self._enqueue_for_sending(
                    cmd, command_type=cmd_type, on_sent=on_sent, tags=tags
                )
            return True

    def _enqueue_for_sending(
        self,
        command,
        linenumber=None,
        command_type=None,
        on_sent=None,
        resend=False,
        tags=None,
    ):
        """
        Enqueues a command and optional linenumber to use for it in the send queue.

        Arguments:
            command (str or SendQueueMarker): The command to send.
            linenumber (int): The line number with which to send the command. May be ``None`` in which case the command
                will be sent without a line number and checksum.
            command_type (str): Optional command type, if set and command type is already in the queue the
                command won't be enqueued
            on_sent (callable): Optional callable to call after command has been sent to printer.
            resend (bool): Whether this is a resent command
            tags (set of str or None): Tags to attach to this command
        """

        try:
            target = "send"
            if resend:
                target = "resend"

            self._send_queue.put(
                (command, linenumber, command_type, on_sent, False, tags),
                item_type=command_type,
                target=target,
            )
            return True
        except TypeAlreadyInQueue as e:
            self._logger.debug("Type already in send queue: " + e.type)
            return False

    def reset(self):
        for device in self._devices.values():
            device.reset()

    def read_state(self):
        # self.configure_all()
        pass

    def isClosedOrError(self):
        return self._state in (
            self.States.STATE_ERROR,
            self.States.STATE_CLOSED,
            self.States.STATE_CLOSED_WITH_ERROR,
        )

    def isOperational(self):
        return self._state in self.OPERATIONAL_STATES

    def isWorking(self):
        return self._state in self.WORKING_STATES

    def isCancelling(self):
        return self._state == self.States.STATE_CANCELLING

    def isPausing(self):
        return self._state == self.States.STATE_PAUSING

    def isPaused(self):
        return self._state == self.States.STATE_PAUSED

    def isResuming(self):
        return self._state == self.States.STATE_RESUMING

    def isFinishing(self):
        return self._state == self.States.STATE_FINISHING

    def isError(self):
        return self._state in (
            self.States.STATE_ERROR,
            self.States.STATE_CLOSED_WITH_ERROR,
        )

    def isBusy(self):
        return (
            self.isWorking()
            or self.isPaused()
            or self._state in (self.States.STATE_CANCELLING, self.States.STATE_PAUSING)
        )

    def isManualControl(self):
        return self._state in (self.States.STATE_OPERATIONAL, self.States.STATE_PAUSED)

    def _get_device(self, device_id: str, device_type: Type[Device]) -> Type:
        device = self._devices.get(device_id)
        if device is None:
            raise ValueError(f"Device {device_id} not found")
        if not isinstance(device, device_type):
            raise ValueError(f"Device {device_id} is not {device_type.__name__}")
        return device

    def _get_valve(self, device_id: str) -> Valve:
        return self._get_device(device_id, Valve)

    def _get_stirrer(self, device_id: str) -> Stirrer:
        return self._get_device(device_id, Stirrer)

    def _get_thermometer(self, device_id: str) -> Thermometer:
        return self._get_device(device_id, Thermometer)

    def _get_od_sensor(self, device_id: str) -> OpticalDensitySensor:
        return self._get_device(device_id, OpticalDensitySensor)

    def _get_pump(self, device_id: str) -> Pump:
        return self._get_device(device_id, Pump)

    def _get_vial(self, device_id: str) -> Vial:
        return self._get_device(device_id, Vial)

    def open_valve(self, device_id: str, *args, **kwargs):
        def command():
            self._get_valve(device_id).open()

        self._sendCommand(MachineCommand(command), *args, **kwargs)

    def close_valve(self, device_id: str, *args, **kwargs):
        def command():
            self._get_valve(device_id).close()

        self._sendCommand(MachineCommand(command), *args, **kwargs)

    def set_stirrer_speed(
        self, device_id: str, speed: Union[int, float], *args, **kwargs
    ):
        def command():
            self._get_stirrer(device_id).set_speed(speed)

        self._sendCommand(MachineCommand(command), *args, **kwargs)

    def measure_temperature(self, device_id: str, *args, **kwargs):
        def command():
            self._get_thermometer(device_id).measure()

        self._sendCommand(MachineCommand(command), *args, **kwargs)

    def measure_od(self, device_id: str, *args, **kwargs):
        def command():
            self._get_od_sensor(device_id).measure_od()

        self._sendCommand(MachineCommand(command), *args, **kwargs)

    def pump_command(self, device_id: str, command: Callable, *args, **kwargs):
        pump = self._get_pump(device_id)

        def condition():
            return pump.is_idle

        def cancel():
            pump.stop()

        return LongtimeMachineCommand(
            callback=command,
            condition=kwargs["condition"] if "condition" in kwargs else condition,
            cancel=kwargs["cancel"] if "cancel" in kwargs else cancel,
            *args,
            **kwargs,
        )

    def pump_command_entry(
        self, device_id: str, command: Callable, *args, **kwargs
    ) -> Tuple[QueueMarker, Optional[str], Optional[Callable[..., None]], Dict[str, str]]:
        return (
            self.pump_command(device_id, command, *args, **kwargs),  # command
            None,  # command_type
            None,  # on_sent
            kwargs["tags"],  # tags
        )

    def machine_command_entry(
        self, command: Callable, *args, **kwargs
    ) -> Tuple[QueueMarker, Optional[str], Optional[Callable[..., None]], Dict[str, str]]:
        return (
            MachineCommand(command),  # command
            None,  # command_type
            None,  # on_sent
            kwargs["tags"],  # tags
        )

    def create_stop_command(self, pump: Pump):
        return lambda: pump.stop()

    def pump_pump(self, device_id: str, volume: float, speed: float, *args, **kwargs):
        # stop other pumps
        commands = []

        for pump in self._pumps:
            stop_command = self.create_stop_command(pump)
            command_entry = self.pump_command_entry(pump.id, stop_command, *args, **kwargs)
            commands += [command_entry]

        if volume:
            commands += [
                self.pump_command_entry(
                    device_id, lambda: self._get_pump(device_id).pump(volume, speed), *args, **kwargs
                ),
            ]
        else:
            commands += [
                self.machine_command_entry(lambda: self._get_pump(device_id).run(rot_per_sec=speed), *args, **kwargs),
            ]
        self._sendCommands(commands)

    def _vial_pump(
        self, vial: Vial, vial_pump: Pump, volume: float, speed: float, *args, **kwargs
    ):
        vial_valve = vial._valve

        # stop all pumps
        commands = [
            self.pump_command_entry(pump.id, self.create_stop_command(pump), *args, **kwargs)
            for pump in self._pumps
        ]
        # open vial valve
        commands += [self.machine_command_entry(lambda: vial_valve.open(), *args, **kwargs)]
        # close all valves except vial valve
        commands += [
            (
                self.machine_command_entry(lambda: valve.close(), *args, **kwargs)
                for valve in self._valves
                if valve.id != vial_valve.id
            )
        ]
        # run media pump
        commands += [
            self.pump_command_entry(vial_pump.id, lambda: vial_pump.pump(volume, speed), *args, **kwargs)
        ]

        self._sendCommands(commands)

    def vial_add_media(
        self, device_id: str, volume: float, speed: float, *args, **kwargs
    ):
        vial = self._get_vial(device_id)
        media_pump = vial._media_pump
        return self._vial_pump(vial, media_pump, volume, speed, *args, **kwargs)

    def vial_add_drug(
        self, device_id: str, volume: float, speed: float, *args, **kwargs
    ):
        vial = self._get_vial(device_id)
        drug_pump = vial._drug_pump
        return self._vial_pump(vial, drug_pump, volume, speed, *args, **kwargs)

    def vial_waste(self, device_id: str, volume: float, speed: float, *args, **kwargs):
        vial = self._get_vial(device_id)
        waste_pump = vial._waste_pump
        return self._vial_pump(vial, waste_pump, volume, speed, *args, **kwargs)

    def pump_stop(self, device_id: str, *args, **kwargs):
        def command():
            self._get_pump(device_id).stop()

        self._sendCommand(self.pump_command(device_id, command), *args, **kwargs)

    def command_queue_clear(self):
        self._job_queue.queue.clear()
        self._command_queue.clear()
        self._send_queue.clear()
        self._cancel_await_condition = True
