import copy
import logging
import threading
import time
from collections import deque

import replifactory.devices.machine as comm
from replifactory import settings
from replifactory.drivers.ft2232h import FtdiDriver
from replifactory.events import Events, eventManager
from replifactory.machine import MachineCallback, MachineInterface
from replifactory.util import InvariantContainer
from replifactory.util import get_fully_qualified_classname as fqcn


logger = logging.getLogger(__name__)


class Machine(MachineInterface, comm.MachineDeviceCallback):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

        self._dict = dict

        self._temps = DataHistory(cutoff=settings().temperature.cutoff * 60)

        self._messages = deque([], 300)
        self._log = deque([], 300)

        self._state = None

        self._firmware_info = None

        self._comm = None

        self._callbacks: list[MachineCallback] = []

        self._stateMonitor = StateMonitor(
            interval=0.5,
            on_update=self._sendCurrentDataCallbacks,
            on_add_temperature=self._sendAddTemperatureCallbacks,
            on_add_optical_density=self._sendAddOpticalDensityCallbacks,
            on_change_stirrer_speed=self._updateStirrerSpeedCallback,
            on_change_environment=self._updateEnvironmentCallback,
        )
        self._stateMonitor.reset(
            state=self._dict(
                text=self.get_state_string(),
                flags=self._getStateFlags(),
                error=self.get_error(),
            ),
            experiment_data=self._dict(),
        )

        eventManager().subscribe(Events.CHART_MARKED, self._on_event_ChartMarked)

    def register_callback(self, callback, *args, **kwargs):
        if not isinstance(callback, MachineCallback):
            self._logger.warning(
                "Registering an object as printer callback which doesn't implement the PrinterCallback interface"
            )
        self._callbacks.append(callback)

    def unregister_callback(self, callback, *args, **kwargs):
        try:
            self._callbacks.remove(callback)
        except ValueError:
            # not registered
            pass

    def _sendCurrentDataCallbacks(self, data):
        for callback in self._callbacks:
            try:
                data_copy = copy.deepcopy(data)
                callback.on_machine_send_current_data(data_copy)
            except Exception:
                self._logger.exception(
                    "Exception while pushing current data to callback {}".format(
                        callback
                    ),
                    extra={"callback": fqcn(callback)},
                )

    def _sendAddTemperatureCallbacks(self, data):
        for callback in self._callbacks:
            try:
                callback.on_machine_add_temperature(data)
            except Exception:
                self._logger.exception(
                    "Exception while adding temperature data point to callback {}".format(
                        callback
                    ),
                    extra={"callback": fqcn(callback)},
                )

    def _sendAddOpticalDensityCallbacks(self, data):
        for callback in self._callbacks:
            try:
                callback.on_machine_add_optical_density(data)
            except Exception:
                self._logger.exception(
                    "Exception while adding temperature data point to callback {}".format(
                        callback
                    ),
                    extra={"callback": fqcn(callback)},
                )

    def _updateStirrerSpeedCallback(self, data):
        pass

    def _updateEnvironmentCallback(self, data):
        pass

    def _getStateFlags(self):
        return self._dict(
            operational=self.is_operational(),
            printing=self.is_running(),
            cancelling=self.is_cancelling(),
            pausing=self.is_pausing(),
            resuming=self.is_resuming(),
            finishing=self.is_finishing(),
            closedOrError=self.is_closed_or_error(),
            error=self.is_error(),
            paused=self.is_paused(),
            ready=self.is_ready(),
        )

    def _on_event_ChartMarked(self, event, data):
        pass

    @classmethod
    def get_connection_options(cls):
        dev_dscs = FtdiDriver.get_devices_descriptions()
        # ftdi_devices = FtdiDriver.list_devices()
        device_address_options = {}
        for dev_dsc in dev_dscs:
            if dev_dsc["is_busy"]:
                parsed_descriptor = FtdiDriver.parse_device_descriptor((dev_dsc["device"], 2))
                logger.warning("Device %s is busy", parsed_descriptor.url)
                continue
            if dev_dsc["error"]:
                logger.warning(dev_dsc["error"])
                continue
            address = f"{dev_dsc['config']['serial']}"
            device_address_options[
                address
            ] = f"{dev_dsc['config']['product']} [{address}]"
        return {
            "device_address": device_address_options,
            "autoconnect": settings().connection.autoconnect,
        }

    # def _parse_device_address(self, device_address: str):
    #     parts = device_address.split(":")
    #     if len(parts) == 2:
    #         try:
    #             num1 = int(parts[0])
    #             num2 = int(parts[1])
    #             return (num1, num2)
    #         except ValueError:
    #             return None
    #     else:
    #         return None

    def connect(self, device_address: str, *args, **kwargs):
        """
        Connects to the machine. If port and/or baudrate is provided, uses these settings, otherwise autodetection
        will be attempted.
        """
        if self._comm is not None:
            return
        # bus, address = self._parse_device_address(device_address) or (None, None)
        eventManager().fire(Events.CONNECTING)
        # self._printerProfileManager.select(profile)

        # if not logging.getLogger("SERIAL").isEnabledFor(logging.DEBUG):
        #     # if serial.log is not enabled, log a line to explain that to reduce "serial.log is empty" in tickets...
        #     logging.getLogger("SERIAL").info(
        #         "serial.log is currently not enabled, you can enable it via Settings > Serial Connection > Log communication to serial.log"
        #     )
        usb_device = FtdiDriver.find_device(serial=device_address)
        self._comm = comm.Machine(usb_device=usb_device, callback=self)
        self._comm.start()

    def disconnect(self, *args, **kwargs):
        """
        Closes the connection to the printer.
        """
        eventManager().fire(Events.DISCONNECTING)
        if self._comm is not None:
            self._comm.close()
        else:
            eventManager().fire(Events.DISCONNECTED)
        self._firmware_info = None

    def is_closed_or_error(self, *args, **kwargs):
        return self._comm is None or self._comm.isClosedOrError()

    def is_operational(self, *args, **kwargs):
        return self._comm is not None and self._comm.isOperational()

    def is_working(self, *args, **kwargs):
        return self._comm is not None and self._comm.isWorking()

    def is_cancelling(self, *args, **kwargs):
        return self._comm is not None and self._comm.isCancelling()

    def is_pausing(self, *args, **kwargs):
        return self._comm is not None and self._comm.isPausing()

    def is_paused(self, *args, **kwargs):
        return self._comm is not None and self._comm.isPaused()

    def is_resuming(self, *args, **kwargs):
        return self._comm is not None and self._comm.isResuming()

    def is_finishing(self, *args, **kwargs):
        return self._comm is not None and self._comm.isFinishing()

    def is_error(self, *args, **kwargs):
        return self._comm is not None and self._comm.isError()

    def is_ready(self, *args, **kwargs):
        return (
            self.is_operational()
            and not self._comm.isBusy()
            # isBusy is true when paused
        )

    def get_error(self):
        if self._comm is None:
            return ""
        else:
            return self._comm.get_error_string()

    def get_state_id(self, state=None, *args, **kwargs):
        if self._comm is None:
            return "OFFLINE"
        else:
            return self._comm.get_state_id(state=state)

    def get_state_string(self, state=None, *args, **kwargs):
        if self._comm is None:
            return "Offline"
        else:
            return self._comm.get_state_string(state=state)

    def _set_state(self, state, state_string, error_string):
        state_string = state_string or self.get_state_string()
        error_string = error_string or self.get_error()

        self._state = state
        self._stateMonitor.set_state(
            self._dict(
                text=state_string, flags=self._getStateFlags(), error=error_string
            )
        )

        payload = {
            "state_id": self.get_state_id(self._state),
            "state_string": self.get_state_string(self._state),
        }
        eventManager().fire(Events.MACHINE_STATE_CHANGED, payload)

    def on_comm_state_change(self, state):
        oldState = self._state

        state_string = None
        error_string = None
        if self._comm is not None:
            state_string = self._comm.get_state_string()
            error_string = self._comm.get_error_string()

        if oldState in (comm.Machine.STATE_WORKING,):
            if state in (
                comm.Machine.STATE_CLOSED,
                comm.Machine.STATE_ERROR,
                comm.Machine.STATE_CLOSED_WITH_ERROR,
            ):
                self._logger.error("Work failed: %s", error_string)

        if (
            state == comm.Machine.STATE_CLOSED
            or state == comm.Machine.STATE_CLOSED_WITH_ERROR
        ):
            if self._comm is not None:
                self._comm = None
            eventManager().fire(Events.DISCONNECTED)

        self._set_state(state, state_string=state_string, error_string=error_string)


class StateMonitor:
    def __init__(
        self,
        interval=0.5,
        on_update=None,
        on_add_temperature=None,
        on_add_optical_density=None,
        on_change_stirrer_speed=None,
        on_change_environment=None,
    ) -> None:
        self._interval = interval
        self._update_callback = on_update
        self._on_add_temperature = on_add_temperature
        self._on_add_optical_density = on_add_optical_density
        self._on_change_stirrer_speed = on_change_stirrer_speed
        self._on_change_environment = on_change_environment

        self._state = None
        self._experiment_data = None

        self._change_event = threading.Event()
        self._state_lock = threading.Lock()

        self._last_update = time.monotonic()
        self._worker = threading.Thread(target=self._work)
        self._worker.daemon = True
        self._worker.start()

    def reset(
        self,
        state=None,
        experiment_data=None,
    ):
        self.set_state(state)
        self.set_experiment_data(experiment_data)

    def add_temperature(self, temperature):
        self._on_add_temperature(temperature)
        self._change_event.set()

    def add_optical_density(self, optical_density):
        self._on_add_optical_density(optical_density)
        self._change_event.set()

    def set_state(self, state):
        with self._state_lock:
            self._state = state
            self._change_event.set()

    def set_experiment_data(self, experiment_data):
        self._experiment_data = experiment_data
        self._change_event.set()

    def _work(self):
        try:
            while True:
                self._change_event.wait()

                now = time.monotonic()
                delta = now - self._last_update
                additional_wait_time = self._interval - delta
                if additional_wait_time > 0:
                    time.sleep(additional_wait_time)

                with self._state_lock:
                    data = self.get_current_data()
                    self._update_callback(data)
                    self._last_update = time.monotonic()
                    self._change_event.clear()
        except Exception:
            logging.getLogger(__name__).exception(
                "Looks like something crashed inside the state update worker. "
                "Please report this on the Replifactory issue tracker (make sure "
                "to include logs!)"
            )

    def get_current_data(self):
        return {
            "state": self._state,
            "experiment": self._experiment_data,
        }


class DataHistory(InvariantContainer):
    def __init__(self, cutoff=30 * 60):
        def data_invariant(data):
            data.sort(key=lambda x: x["time"])
            now = int(time.time())
            return [item for item in data if item["time"] >= now - cutoff]

        InvariantContainer.__init__(self, guarantee_invariant=data_invariant)
        self._last = None

    @property
    def last(self):
        return self._last

    def append(self, item):
        try:
            return super().append(item)
        finally:
            self._last = self._data[-1] if len(self._data) else None
