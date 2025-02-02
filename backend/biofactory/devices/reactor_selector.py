import threading
from typing import Optional

from biofactory.devices import Device, DeviceCallback
from biofactory.drivers.pca9555 import IOPortDriver

global_lock = threading.RLock()


class ReactorSelector(Device, DeviceCallback):
    def __init__(
        self,
        io_driver: IOPortDriver,
        lock=global_lock,
        name: str = "Reactor selector",
        callback: Optional[DeviceCallback] = None,
    ):
        super().__init__(name or "Reactor selector", callback)
        self.io_driver = io_driver
        self.lock = lock

    def read_state(self):
        active_reactor_index = self.io_driver.read() & 0xFF
        self._log.debug(f"Active reactor index: {active_reactor_index}")
        self._set_state(active_reactor_index)

    def select(self, reactor_index: int):
        self._log.debug(f"Select reactor {reactor_index}")
        self.io_driver.write_l(reactor_index - 1)

    def get_drivers(self):
        return [self.io_driver]
