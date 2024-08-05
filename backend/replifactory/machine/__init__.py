import inspect
import logging
import queue
import threading
from collections import OrderedDict
from enum import Enum
from inspect import signature
from typing import Any, Callable, Optional

from usb.core import Device as UsbDevice

from replifactory.devices import Device, DeviceCallback
from replifactory.drivers.ft2232h import FtdiDriver
from replifactory.events import Events, eventManager
from replifactory.usb_manager import usbManager
from replifactory.util import StateMixin, slugify
from replifactory.util.module_loading import import_string

# class ReactorCommand:
#     def __init__(self, name, *args, **kwargs):
#         self.name = name
#         self.args = args
#         self.kwargs = kwargs


class ReactorException(Exception):
    pass


class ReactorStates(Enum):
    READY = 1
    RUNNING = 2
    PAUSED = 3
    CANCELLING = 4
    PAUSING = 5
    ERROR = 6


class Reactor:

    def __init__(self, reactor_num: Optional[int] = None, *args, **kwargs):
        self._state = ReactorStates.READY
        self._log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._num = reactor_num or id(self)
        self._commands_info = self.ls_cmd()

    def __str__(self):
        return f"Reactor {self._num}"

    @property
    def state(self):
        return self._state

    def get_command_info(self):
        return self._commands_info

    def _set_state(self, state: ReactorStates):
        self._state = state

    def home(self):
        """Set reactor to the home state"""
        pass

    def error(self, message):
        """Set reactor to the error state"""
        self._log.warning(f"{self} error: {message}")
        self._set_state(ReactorStates.ERROR)

    def cmd(self, method_name: str, *args, **kwargs):
        """Send a command to the reactor"""
        try:
            method = getattr(self, method_name)
            if self._log.isEnabledFor(logging.DEBUG):
                self._log.debug(f"Executing {method_name} with args: {args} and kwargs: {kwargs}")
            else:
                self._log.info(f"Reactor {self._num} {method_name}")
            return method(*args, **kwargs)
        except AttributeError:
            raise AttributeError(f"No command named {method_name} found")

    def ls_cmd(self):
        """List available commands"""
        command_info = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and getattr(attr, 'is_reactor_command', False):
                args = inspect.getfullargspec(attr).args[1:]
                command_info[attr_name] = args
                # command_info[attr_name] = list(signature(attr).parameters.keys())
        return command_info
        # for method_name in dir(self):
        #     if callable(getattr(self, method_name)) and method_name.startswith(
        #         self.command_method_prefix
        #     ):
        #         method = getattr(self, method_name)
        #         args = inspect.getfullargspec(method).args[1:]
        #         cmd_methods[method_name.removeprefix(self.command_method_prefix)] = args
        # self._commands_info = cmd_methods
        # return self._commands_info


class CommandExecutor:
    def __init__(self, name=None, execute_callback=None):
        self._name = f"{name}" if name else f"{self.__class__.__name__}{id(self)}"
        self._execute_callback = execute_callback or self._execute
        self._command_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(name=f"{self._name}Thread", target=self._command_executor_loop)
        self._thread.start()
        self._log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    def name(self):
        return self._name

    def _command_executor_loop(self):
        while not self._stop_event.is_set():
            try:
                command, result_queue, executed = self._command_queue.get()
                result = self._execute_callback(command)
                if result_queue:
                    result_queue.put(result)
            except queue.Empty:
                continue
            except Exception as exc:
                self._log.exception(exc)
                if result_queue:
                    result_queue.put(exc)
            self._command_queue.task_done()
            if executed:
                executed.set()
        self._log.info(f"Closing {self.name} loop")

    def _execute(self, command):
        raise NotImplementedError()

    def queue_command_and_wait(self, command, timeout=None):
        result_queue = queue.Queue()
        executed = threading.Event()
        self._command_queue.put((command, result_queue, executed))
        executed.wait(timeout=timeout)
        result = result_queue.get()
        return result

    def queue_command_no_wait(self, command):
        self._command_queue.put((command, None, None))

    def stop(self):
        self._stop_event.set()
        self._thread.join()

    def cancel_current_commands(self):
        self._command_queue.queue.clear()


class DeviceManager:
    def __init__(self):
        self._devices = {}
        self._drivers = set()
        self._command_executor = CommandExecutor(
            name="CommandExecutor", execute_callback=self._execute_command
        )
        self._high_priority_executor = CommandExecutor(
            name="HighPriorityExecutor", execute_callback=self._execute_command
        )
        self._log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._commands_info = {}

    @property
    def commands_info(self):
        return self._commands_info

    def add_devices(self, *devices: Device):
        for device in devices:
            if device.id in self._devices:
                raise ValueError(f"Device {device.id} already exists")
            self._devices[device.id] = device
            self._drivers.update(device.get_drivers())
            self._commands_info[device.id] = device.get_commands_info()

    def initialize_devices(self):
        self._log.info("Initializing drivers...")
        for driver in self._drivers:
            driver.init()
        self._log.info("Connecting devices...")
        for device in self._devices.values():
            # self.execute(device.id, "connect", no_wait=True)
            try:
                device.connect()
            except Exception as exc:
                raise ValueError(f"Error while connecting device {device.id}: {exc}")

    def execute(
        self,
        device_id,
        command,
        *args,
        **kwargs,
    ):
        no_wait = kwargs.pop("no_wait", False)
        high_priority = kwargs.pop("high_priority", False)
        timeout = kwargs.pop("timeout", None)
        executor = (
            self._high_priority_executor if high_priority else self._command_executor
        )
        command_tuple = (device_id, command, args, kwargs)
        if no_wait:
            executor.queue_command_no_wait(command_tuple)
            return None
        else:
            return executor.queue_command_and_wait(command_tuple, timeout=timeout)

    def _execute_command(self, command):
        device_id, command, args, kwargs = command
        device = self._devices.get(device_id)
        if device is None:
            raise ValueError(f"Device {device_id} not found")
        method = getattr(device, command)
        return method(*args, **kwargs)


class MachineCallback:
    def _on_machine_state_change(self, state, *args, **kwargs):
        pass

    def _on_change_device_data(self, data, *args, **kwargs):
        pass

    def _on_machine_send_current_data(self, data, *args, **kwargs):
        pass


class ConnectionAdapterCallbacks:
    def _on_conn_state_change(self, state):
        pass

    def _on_conn_connected(self):
        pass

    def _before_conn_disconnected(self):
        pass


class ConnectionAdapter:
    class States(Enum):
        STATE_DISCONNECTED = 1
        STATE_CONNECTING = 2
        STATE_OPERATIONAL = 3
        STATE_RECONNECTING = 4

    def __init__(
        self, callbacks: Optional[ConnectionAdapterCallbacks] = None, *args, **kwargs
    ):
        self._callbacks = callbacks or ConnectionAdapterCallbacks()
        self._state = self.States.STATE_DISCONNECTED

    def connect(self, *args, **kwargs):
        raise NotImplementedError()

    def disconnect(self, *args, **kwargs):
        raise NotImplementedError()

    def get_device_info(self, *args, **kwargs):
        raise NotImplementedError()

    def _set_state(self, state: States):
        self._state = state
        self._callbacks._on_conn_state_change(state)

    @property
    def is_connected(self):
        return self._state == self.States.STATE_OPERATIONAL

    @property
    def is_disconnected(self):
        return self._state == self.States.STATE_DISCONNECTED


class FtdiConnectionAdapter(ConnectionAdapter):
    def __init__(
        self, ftdi_driver: FtdiDriver, reconnect: bool = True, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._lock = threading.RLock()
        self._ftdi_driver = ftdi_driver
        self._usb_device = None
        self._serial = None
        self._state = self.States.STATE_DISCONNECTED
        self._reconnect = reconnect
        self._log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def connect(self, usb_device: Optional[UsbDevice] = None, *args, **kwargs):
        with self._lock:
            if self.is_connected:
                return

            self._set_state(self.States.STATE_CONNECTING)
            usb_device = usb_device or usbManager().find_device(
                serial_number=self._serial
            )
            if usb_device is None:
                return

            # eventManager().fire(Events.MACHINE_CONNECTING, self)

            self._ftdi_driver.connect(usb_device)
            self._usb_device = usb_device
            self._serial = usb_device.serial_number
            eventManager().subscribe(Events.USB_DISCONNECTED, self._on_usb_disconnected)
            eventManager().subscribe(Events.USB_CONNECTED, self._on_usb_connected)

            self._callbacks._on_conn_connected()
            self._set_state(self.States.STATE_OPERATIONAL)
            # for driver in self._drivers:
            #     driver.init()

            # for device in self._devices.values():
            #     device.connect()

            # eventManager().fire(Events.MACHINE_CONNECTED, self)
            # self._clear_to_send.set()

    def disconnect(self, *args, **kwargs):
        with self._lock:
            if self.is_disconnected:
                return

            eventManager().unsubscribe(
                Events.USB_DISCONNECTED, self._on_usb_disconnected
            )
            eventManager().unsubscribe(Events.USB_CONNECTED, self._on_usb_connected)

            self._callbacks._before_conn_disconnected()
            # self._monitoring_active = False
            try:
                self._terminate_connection(raise_exception=True)
            finally:
                self._set_state(self.States.STATE_DISCONNECTED)

    def get_device_info(self, *args, **kwargs):
        if self._usb_device is None:
            return {}
        return usbManager().get_device_info(self._usb_device)

    def get_spi_hw_port(
        self,
        name: str,
        cs: int,
        freq: Optional[float] = None,
        mode: Optional[int] = None,
    ):
        return self._ftdi_driver.get_spi_hw_port(name, cs, freq, mode)

    def get_i2c_hw_port(
        self, address: int | list[int], name: str, registers: dict[int, str] = {}
    ):
        return self._ftdi_driver.get_i2c_hw_port(address, name, registers)

    def _on_usb_disconnected(self, event, usb_device):
        if self._serial != usb_device.serial_number:
            return

        if self._reconnect:
            self._terminate_connection()
            self._set_state(self.States.STATE_RECONNECTING)
        else:
            self.disconnect()

    def _on_usb_connected(self, event, usb_device):
        if usb_device.serial_number and usb_device.serial_number != self._serial:
            return

        if self._state == self.States.STATE_RECONNECTING:
            self.connect(usb_device=usb_device)

    def _terminate_connection(self, raise_exception=False):
        if self._usb_device is not None:
            try:
                self._ftdi_driver.close()
            except Exception as exc:
                self._log.exception("Error while trying to close serial port")
                if raise_exception:
                    raise exc
            # self._ftdi_driver = None
            self._usb_device = None


def machine_command(func):
    func.is_machine_command = True
    return func


def reactor_command(func):
    func.is_reactor_command = True
    return func


class BaseMachine(ConnectionAdapterCallbacks, DeviceCallback, StateMixin):

    reactor_class = Reactor

    def __init__(
        self,
        connection_adapter: ConnectionAdapter,
        dev_manager: Optional[DeviceManager] = None,
        machine_callback: Optional[MachineCallback] = None,
        name: Optional[str] = None,
        reactors_count: int = 1,
        *args,
        **kwargs,
    ):
        self._name = name or f"{__name__}.{self.__class__.__name__}"
        self._id = slugify(self._name)
        self._dev_manager = dev_manager or DeviceManager()
        self._conn_adapter = connection_adapter
        self._machine_callback = machine_callback or MachineCallback()
        self.changestate_callback = self._machine_callback._on_machine_state_change
        self._state = self.States.STATE_OFFLINE
        self._reactors = [
            self.reactor_class(reactor_num=index + 1, machine=self, *args, **kwargs)
            for index in range(reactors_count)
        ]
        self._log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._operation_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._machine_operation_queue_loop)
        self._stop_operation_timeout = 5
        self._commands_info = self._get_command_info()
        # self._experiment = None
        self._lock = threading.RLock()
        self._cancel_long_operation_event = threading.Event()

    @classmethod
    def get_connection_options(cls, *args, **kwargs):
        pass

    def _get_command_info(self):
        command_info = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and getattr(attr, 'is_machine_command', False):
                command_info[attr_name] = list(signature(attr).parameters.keys())
        return command_info

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    def get_commands_info(self):
        return self._commands_info

    def get_devices_commands_info(self):
        return self._dev_manager.commands_info

    def _machine_operation_queue_loop(self):
        while not self._stop_event.is_set():
            try:
                operation, result_queue, executed = self._operation_queue.get()
                command, args, kwargs = operation
                result = command(*args, **kwargs)
                if result_queue:
                    result_queue.put(result)
            except queue.Empty:
                continue
            except Exception as exc:
                self._log.exception(exc)
                if result_queue:
                    result_queue.put(exc)
            self._operation_queue.task_done()
            if executed:
                executed.set()
        self._log.info(f"Closing {self.name} loop")

    def execute_device_command(self, device_id, command, *args, **kwargs):
        return self._dev_manager.execute(device_id, command, *args, **kwargs)

    def cmd(self, method_name: str, no_wait=False, timeout=None, *args, **kwargs):
        """Execute machine command"""
        try:
            method = getattr(self, method_name)
            self.add_operation((method, args, kwargs), no_wait=no_wait, timeout=timeout)
        except AttributeError:
            raise AttributeError(f"No command named {method_name} found")

    def get_connected_device_info(self):
        return self._conn_adapter.get_device_info()

    # def run_experiment(self, experiment: Experiment, *args, **kwargs):
    #     with self._lock:
    #         if self._experiment is not None:
    #             raise ValueError("Experiment already running")
    #         self._experiment = experiment
    #         self._experiment.start()

    # def pause_experiment(self, *args, **kwargs):
    #     with self._lock:
    #         if self._experiment is None:
    #             raise ValueError("No experiment running")
    #         self._experiment.pause()

    # def resume_experiment(self, *args, **kwargs):
    #     pass

    # def stop_experiment(self, *args, **kwargs):
    #     pass

    def add_operation(
        self,
        operation: tuple[Callable[..., Any], tuple[Any, ...], dict[str, Any]],
        no_wait=False,
        timeout=None,
    ):
        if no_wait:
            self._operation_queue.put((operation, None, None))
            return None
        result_queue = queue.Queue()
        executed = threading.Event()
        self._operation_queue.put((operation, result_queue, executed))
        executed.wait(timeout=timeout)
        result = result_queue.get()
        return result

    def cancel_long_operation(self):
        self._cancel_long_operation_event.set()

    def get_reactor(self, reactor_num) -> Reactor:
        return self._reactors[reactor_num - 1]

    def get_reactors(self):
        return self._reactors

    def get_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "state_id": self.get_state_id(),
            "state_string": self.get_state_string(),
            "error": "",
        }

    def connect(self, *args, **kwargs):
        if self._conn_adapter.is_connected:
            return

        # self._set_state(self.States.STATE_CONNECTING)
        self._conn_adapter.connect(*args, **kwargs)
        self._thread.start()

        eventManager().fire(Events.MACHINE_CONNECTED, self)
        # self._clear_to_send.set()

    def get_error_string(self):
        return self._errorValue

    # ConnectionAdapterCallbacks
    def _on_conn_connected(self):
        self._dev_manager.initialize_devices()

    # ConnectionAdapterCallbacks
    def _on_conn_state_change(self, state):
        match state:
            case ConnectionAdapter.States.STATE_RECONNECTING:
                self._set_state(self.States.STATE_RECONNECTING)
            case ConnectionAdapter.States.STATE_CONNECTING:
                self._set_state(self.States.STATE_CONNECTING)
            case ConnectionAdapter.States.STATE_DISCONNECTED:
                self._set_state(self.States.STATE_CLOSED)
            case ConnectionAdapter.States.STATE_OPERATIONAL:
                self._set_state(self.States.STATE_OPERATIONAL)

    # DeviceCallback
    def _on_device_state_change(self, state, device, *args, **kwargs):
        self._machine_callback._on_change_device_data(device.get_data())
        eventManager().fire(Events.DEVICE_STATE_CHANGED, (device, state))

    def disconnect(self, *args, **kwargs):
        try:
            self._conn_adapter.disconnect(*args, **kwargs)
            self._stop_event.set()
            self._thread.join(timeout=self._stop_operation_timeout)
            if self._thread.is_alive():
                self._log.warning("Stop operation timeout")
            self._set_state(self.States.STATE_CLOSED)
        except Exception:
            self._set_state(self.States.STATE_CLOSED_WITH_ERROR)

    def get_transport(self):
        raise NotImplementedError()

    def health_check(self):
        raise NotImplementedError()

    def commands(self, commands, force=False, *args, **kwargs):
        raise NotImplementedError()

    # def experiment(self, experiment, *args, **kwargs):
    #     raise NotImplementedError()

    # def valve_open(self, device_id, *args, **kwargs):
    #     raise NotImplementedError()

    # def valve_close(self, device_id, *args, **kwargs):
    #     raise NotImplementedError()

    # def start_experiment(self):
    #     raise NotImplementedError()

    # def pause_experiment(self):
    #     raise NotImplementedError()

    # def resume_experiment(self):
    #     raise NotImplementedError()

    # def togle_pause_experiment(self):
    #     if self.is_running():
    #         self.pause_experiment()
    #     elif self.is_paused():
    #         self.resume_experiment()

    # def cancel_experiment(self):
    #     raise NotImplementedError()

    # def get_current_data(self, *args, **kwargs):
    #     raise NotImplementedError()

    # def get_current_job(self, *args, **kwargs):
    #     raise NotImplementedError()

    # def get_current_temperatures(self, *args, **kwargs):
    #     """
    #     Returns:
    #         (dict) The current temperatures.
    #     """
    #     raise NotImplementedError()

    # def get_temperature_history(self, *args, **kwargs):
    #     """
    #     Returns:
    #         (list) The temperature history.
    #     """
    #     raise NotImplementedError()

    # def get_current_connection(self, *args, **kwargs):
    #     raise NotImplementedError()

    # def is_closed_or_error(self, *args, **kwargs):
    #     """
    #     Returns:
    #         (boolean) Whether the machine is currently disconnected and/or in an error state.
    #     """
    #     raise NotImplementedError()

    # def is_operational(self, *args, **kwargs):
    #     """
    #     Returns:
    #         (boolean) Whether the machine is currently connected and available.
    #     """
    #     raise NotImplementedError()

    # def is_running(self):
    #     pass

    # def is_cancelling(self, *args, **kwargs):
    #     """
    #     Returns:
    #         (boolean) Whether the machine is currently cancelling an experiment.
    #     """
    #     raise NotImplementedError()

    # def is_pausing(self, *args, **kwargs):
    #     """
    #     Returns:
    #             (boolean) Whether the machine is currently pausing an experiment.
    #     """
    #     raise NotImplementedError()

    # def is_paused(self, *args, **kwargs):
    #     """
    #     Returns:
    #         (boolean) Whether the machine is currently paused.
    #     """
    #     raise NotImplementedError()

    # def is_error(self, *args, **kwargs):
    #     """
    #     Returns:
    #         (boolean) Whether the machine is currently in an error state.
    #     """
    #     raise NotImplementedError()

    # def is_ready(self, *args, **kwargs):
    #     """
    #     Returns:
    #         (boolean) Whether the machine is currently operational and ready for new experiment jobs (not running).
    #     """
    #     raise NotImplementedError()

    def register_callback(self, callback, *args, **kwargs):
        """
        Registers a :class:`MachineCallback` with the instance.

        Arguments:
            callback (MachineCallback): The callback object to register.
        """
        raise NotImplementedError()

    def unregister_callback(self, callback, *args, **kwargs):
        """
        Unregisters a :class:`MachineCallback` from the instance.

        Arguments:
            callback (MachineCallback): The callback object to unregister.
        """
        raise NotImplementedError()

    def send_initial_callback(self, callback):
        """
        Sends the initial printer update to :class:`MachineCallback`.

        Arguments:
                callback (MachineCallback): The callback object to send initial data to.
        """
        raise NotImplementedError()

    def get_firmware_info(self):
        raise NotImplementedError()

    def isClosedOrError(self):
        return self._state in (
            self.States.STATE_ERROR,
            self.States.STATE_CLOSED,
            self.States.STATE_CLOSED_WITH_ERROR,
        )

    def isIdle(self):
        return self._state == self.States.STATE_OPERATIONAL

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


Reactor.machine_class = BaseMachine

# class MachineCallback:
#     def on_machine_add_log(self, data):
#         pass

#     def on_machine_add_temperature(self, data):
#         pass

#     def on_machine_add_optical_density(self, data):
#         pass

#     def on_machine_send_initial_data(self, data):
#         pass

#     def on_machine_send_current_data(self, data):
#         """
#         Called when the internal state of the :class:`MachineInterface` changes, due to changes in the printer state,
#         temperatures, log lines, job progress etc. Updates via this method are guaranteed to be throttled to a maximum
#         of 2 calls per second.

#         ``data`` is a ``dict`` of the following structure::

#             state:
#                 text: <current state string>
#                 flags:
#                     operational: <whether the printer is currently connected and responding>
#                     printing: <whether the printer is currently printing>
#                     closedOrError: <whether the printer is currently disconnected and/or in an error state>
#                     error: <whether the printer is currently in an error state>
#                     paused: <whether the printer is currently paused>
#                     ready: <whether the printer is operational and ready for jobs>
#                     sdReady: <whether an SD card is present>
#             job:
#                 file:
#                     name: <name of the file>,
#                     size: <size of the file in bytes>,
#                     origin: <origin of the file, "local" or "sdcard">,
#                     date: <last modification date of the file>
#                 estimatedPrintTime: <estimated print time of the file in seconds>
#                 lastPrintTime: <last print time of the file in seconds>
#                 filament:
#                     length: <estimated length of filament needed for this file, in mm>
#                     volume: <estimated volume of filament needed for this file, in ccm>
#             progress:
#                 completion: <progress of the print job in percent (0-100)>
#                 filepos: <current position in the file in bytes>
#                 printTime: <current time elapsed for printing, in seconds>
#                 printTimeLeft: <estimated time left to finish printing, in seconds>
#             currentZ: <current position of the z axis, in mm>
#             offsets: <current configured temperature offsets, keys are "bed" or "tool[0-9]+", values the offset in degC>

#         Arguments:
#             data (dict): The current data in the format as specified above.
#         """
#         pass


class CommunicationInterface:
    pass


class MachineRegistry:

    def __init__(self):
        self._machines = OrderedDict()

    def register(self, machine, check_compatible_callback=None):
        machine_name = f"{machine.__module__}.{machine.__name__}"
        if machine_name in self._machines:
            raise ValueError(f"Machine {machine_name} already exists")
        self._machines[machine_name] = (machine, check_compatible_callback)

    def get(self, name):
        machine, _ = self._machines.get(name, (None, None))
        return machine

    def list(self):
        return list(self._machines.keys())

    def find_compatible(self, *args, **kwargs):
        for machine, check_compatible in self._machines.values():
            if check_compatible is not None and check_compatible(*args, **kwargs):
                return machine
        return None


_machineRegistry = None


def machineRegistry():
    global _machineRegistry
    if _machineRegistry is None:
        _machineRegistry = MachineRegistry()
    return _machineRegistry


def register_machine(
    registerable: type[BaseMachine] | str, check_compatible_callback=None
):
    if isinstance(registerable, str):
        registerable = import_string(registerable)
    machineRegistry().register(registerable, check_compatible_callback)
    return registerable
