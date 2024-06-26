from inspect import signature
import logging
from typing import Optional

from flask_app.replifactory.drivers import Driver
from flask_app.replifactory.util import StateMixin, slugify


class DeviceCallback:
    def _on_device_state_change(self, state, device, *args, **kwargs):
        pass


DUMMY_DEVICE_CALBACK = DeviceCallback()


def device_command(func):
    func.is_device_command = True
    return func


class Device(StateMixin):

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
        self._log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._error = ""
        self._devices = devices or {}
        self.changestate_callback = self._callback._on_device_state_change
        self._commands_info = self._get_commands_info()

    @property
    def id(self):
        return self._id

    @property
    def devices(self):
        return self._devices

    @property
    def name(self):
        return self._name

    def get_commands_info(self):
        return self._commands_info

    def _get_commands_info(self):
        command_info = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and getattr(attr, 'is_device_command', False):
                command_info[attr_name] = list(signature(attr).parameters.keys())
        return command_info

    def get_drivers(self) -> list[Driver]:
        raise NotImplementedError(f"{self.name} has no drivers, it should explicitly return []")

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

    @device_command
    def read_state(self):
        pass

    # raise NotImplementedError(f"{self.name} can not read state")

    def _test(self):
        raise NotImplementedError(f"{self.name} has no self test")

    @device_command
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

    def set_callback(self, callback):
        self._callback = callback
