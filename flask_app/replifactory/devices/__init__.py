import logging
from typing import Optional

from replifactory.util import slugify


class DeviceCallback:
    def on_device_state_change(self, device, state):
        pass


DUMMY_DEVICE_CALBACK = DeviceCallback()


class Device:

    class States:
        STATE_UNKNOWN = -1
        STATE_OFFLINE = 0
        STATE_FINDING_DEVICE = 1
        STATE_CONNECTING = 2
        STATE_SELF_TESTING = 3
        STATE_OPERATIONAL = 4
        STATE_STARTING = 5
        STATE_WORKING = 6
        STATE_PAUSING = 8
        STATE_PAUSED = 7
        STATE_RESUMING = 9
        STATE_FINISHING = 10
        STATE_CLOSED = 11
        STATE_ERROR = 12
        STATE_CLOSED_WITH_ERROR = 13
        STATE_RECONNECTING = 14
        STATE_CANCELLING = 15

    # be sure to add anything here that signifies an operational state
    OPERATIONAL_STATES = (
        States.STATE_WORKING,
        States.STATE_STARTING,
        States.STATE_OPERATIONAL,
        States.STATE_PAUSED,
        States.STATE_CANCELLING,
        States.STATE_PAUSING,
        States.STATE_RESUMING,
        States.STATE_FINISHING,
    )

    # be sure to add anything here that signifies a working state
    WORKING_STATES = (
        States.STATE_STARTING,
        States.STATE_WORKING,
        States.STATE_CANCELLING,
        States.STATE_PAUSING,
        States.STATE_RESUMING,
        States.STATE_FINISHING,
    )

    def __init__(
        self,
        name: str,
        callback: Optional[DeviceCallback] = None,
        devices=None,
    ):
        self._name = name
        self._id = slugify(name)
        self._callback = callback or DUMMY_DEVICE_CALBACK
        self._state = self.States.STATE_OFFLINE
        self._log = logging.getLogger(f"Device ({name})")
        self._error = ""
        self._devices = devices or {}

    @property
    def id(self):
        return self._id

    @property
    def devices(self):
        return self._devices

    @property
    def name(self):
        return self._name

    def get_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "state_id": self.get_state_id(),
            "state_string": self.get_state_string(),
            "error": self._error,
        }

    def __str__(self):
        return f"{self._name} ({self.get_state_string()})"

    def connect(self, reset: bool = True):
        if reset:
            self.reset()
        self.read_state()

    def disconnect(self):
        pass

    def reset(self):
        pass

    def read_state(self):
        pass

    # raise NotImplementedError(f"{self.name} can not read state")

    def _test(self):
        raise NotImplementedError(f"{self.name} has no self test")

    def test(self):
        self._set_state(self.States.STATE_SELF_TESTING)
        try:
            self._test()
        except Exception as exc:
            self._log.exception(exc)
            self._error = str(exc)
            self._set_state(self.States.STATE_ERROR)
            return False
        self.read_state()
        return True

    def _set_state(self, new_state, force=False):
        if force or self._state != new_state:
            self._state = new_state
            self._callback.on_device_state_change(self, new_state)

    @property
    def state_id(self):
        return self.get_state_id()

    def get_state_id(self, state=None):
        if state is None:
            state = self._state

        possible_states = list(filter(lambda x: x.startswith("STATE_"), dir(self.States)))
        for possible_state in possible_states:
            if getattr(self.States, possible_state) == state:
                return possible_state[len("STATE_") :]

        return "UNKNOWN"

    @property
    def state_string(self):
        return self.get_state_string()

    def get_state_string(self, state=None):
        state = state or self._state
        if state == self.States.STATE_OFFLINE:
            return "Offline"
        elif state == self.States.STATE_FINDING_DEVICE:
            return "Finding"
        elif state == self.States.STATE_CONNECTING:
            return "Connecting"
        elif state == self.States.STATE_SELF_TESTING:
            return "Self testing"
        elif state == self.States.STATE_OPERATIONAL:
            return "Operational"
        elif state == self.States.STATE_STARTING:
            return "Starting"
        elif state == self.States.STATE_WORKING:
            return "Working"
        elif state == self.States.STATE_PAUSED:
            return "Paused"
        elif state == self.States.STATE_PAUSING:
            return "Pausing"
        elif state == self.States.STATE_RESUMING:
            return "Resuming"
        elif state == self.States.STATE_FINISHING:
            return "Finishing"
        elif state == self.States.STATE_CLOSED:
            return "Closed"
        elif state == self.States.STATE_ERROR:
            return "Error"
        elif state == self.States.STATE_CLOSED_WITH_ERROR:
            return "Offline after error"
        elif state == self.States.STATE_CANCELLING:
            return "Cancelling"
        elif state == self.States.STATE_RECONNECTING:
            return "Reconnecting"
        return f"Unknown State ({self._state})"
