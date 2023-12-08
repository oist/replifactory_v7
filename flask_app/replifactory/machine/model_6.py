import copy
import logging
import threading
import time
from collections import deque

import replifactory.devices.machine as comm
from flask_app import settings
from flask_app.replifactory.events import Events, eventManager
from flask_app.replifactory.machine import MachineCallback, MachineInterface
from flask_app.replifactory.usb_manager import UsbManager, usbManager
from flask_app.replifactory.util import InvariantContainer
from flask_app.replifactory.util import get_fully_qualified_classname as fqcn

logger = logging.getLogger(__name__)


class Machine(MachineInterface, comm.MachineCallback):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

        self._dict = dict

        self._temps = DataHistory(cutoff=settings().temperature.cutoff * 60)

        self._messages = deque([], 300)
        self._log = deque([], 300)

        self._state = None

        self._firmware_info = None

        self._comm = None
        self._current_connection = {}

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

        eventManager().subscribe(Events.USB_LIST_UPDATED, self._on_usb_list_updated)

    def register_callback(self, callback, *args, **kwargs):
        if not isinstance(callback, MachineCallback):
            self._logger.warning(
                "Registering an object as printer callback which doesn't implement the MachineCallback interface"
            )
        self._callbacks.append(callback)

    def unregister_callback(self, callback, *args, **kwargs):
        try:
            self._callbacks.remove(callback)
        except ValueError:
            # not registered
            pass

    def send_initial_callback(self, callback):
        if callback in self._callbacks:
            self._sendInitialStateUpdate(callback)

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

    def _sendInitialStateUpdate(self, callback: MachineCallback):
        try:
            data = self._stateMonitor.get_current_data()
            data.update(
                temps=list(self._temps),
                logs=list(self._log),
                messages=list(self._messages),
            )
            callback.on_machine_send_initial_data(data)
        except Exception:
            self._logger.exception(
                "Error while pushing initial state update to callback {}".format(
                    callback
                ),
                extra={"callback": fqcn(callback)},
            )

    def _getStateFlags(self):
        return self._dict(
            operational=self.is_operational(),
            working=self.is_running(),
            cancelling=self.is_cancelling(),
            pausing=self.is_pausing(),
            resuming=self.is_resuming(),
            finishing=self.is_finishing(),
            closedOrError=self.is_closed_or_error(),
            error=self.is_error(),
            paused=self.is_paused(),
            ready=self.is_ready(),
            manualControl=self.is_manual_control(),
        )

    def _on_usb_list_updated(self, event, data):
        payload = self.get_connection_options()
        eventManager().fire(Events.CONNECTION_OPTIONS_UPDATED, payload)

    def get_current_connection(self):
        return self._current_connection

    def _set_current_connection(self, usb_device):
        self._current_connection = UsbManager.get_device_info(usb_device)

    @classmethod
    def get_connection_options(cls):
        devices = usbManager().get_available_devices()
        devices_options = {}
        for device_id, device in devices.items():
            devices_options[device_id] = UsbManager.get_device_info(device)
        return {
            "devices": devices_options,
            "autoconnect": settings().connection.autoconnect,
        }

    def connect(self, device_address: str, *args, **kwargs):
        """
        Connects to the machine. If port and/or baudrate is provided, uses these settings, otherwise autodetection
        will be attempted.
        """
        if self._comm is not None:
            return
        eventManager().fire(Events.MACHINE_CONNECTING)
        usb_device = usbManager().get_device(device_id=device_address)
        self._set_current_connection(usb_device)
        self._comm = comm.Machine(callback=self)
        self._comm.connect(usb_device=usb_device)

    def disconnect(self, *args, **kwargs):
        """
        Closes the connection to the printer.
        """
        eventManager().fire(Events.MACHINE_DISCONNECTING)
        self._current_connection = {}
        if self._comm is not None:
            self._comm.close()
        else:
            eventManager().fire(Events.MACHINE_DISCONNECTED)

    def valve_open(self, device_id, *args, **kwargs):
        if self._comm:
            self._comm.open_valve(
                device_id, tags=kwargs.get("tags", set()) | {"trigger:valve.open"}
            )

    def valve_close(self, device_id, *args, **kwargs):
        if self._comm:
            self._comm.close_valve(
                device_id, tags=kwargs.get("tags", set()) | {"trigger:valve.close"}
            )

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

    def is_manual_control(self, *args, **kwargs):
        return self._comm is not None and self._comm.isManualControl()

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

        if oldState in (comm.Machine.States.STATE_WORKING,):
            if state in (
                comm.Machine.States.STATE_CLOSED,
                comm.Machine.States.STATE_ERROR,
                comm.Machine.States.STATE_CLOSED_WITH_ERROR,
            ):
                self._logger.error("Work failed: %s", error_string)

        if (
            state == comm.Machine.States.STATE_CLOSED
            or state == comm.Machine.States.STATE_CLOSED_WITH_ERROR
        ):
            if self._comm is not None:
                self._comm = None
            eventManager().fire(Events.MACHINE_DISCONNECTED)

        self._set_state(state, state_string=state_string, error_string=error_string)

    def on_change_device_data(self, data):
        self._stateMonitor.set_device_data(data["id"], data)


class StateMonitor:
    """
    Machine data to display at UI
    """

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
        self._devices_data = {}
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
        devices_data=None,
        experiment_data=None,
    ):
        self.set_state(state)
        self.set_devices_data(devices_data or {})
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

    def set_devices_data(self, machine_data):
        self._devices_data = machine_data
        self._change_event.set()

    def set_device_data(self, device_id, data):
        self._devices_data[device_id] = data
        self._change_event.set()

    def set_experiment_data(self, experiment_data):
        self._experiment_data = experiment_data
        self._change_event.set()

    def _work(self):
        """
        Every time when something chaged in stateMonitor this worker
        update self._lust_update time and invoke update_callback passing all data
        """
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
            "devices": self._devices_data,
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
