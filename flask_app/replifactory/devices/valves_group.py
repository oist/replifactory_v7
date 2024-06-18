from typing import Optional

from flask_app.replifactory.devices import Device, DeviceCallback
from flask_app.replifactory.devices.valve import Valve


class ValvesGroup(Device):
    def __init__(
        self,
        valves: list[Valve],
        name: Optional[str] = None,
        callback: Optional[DeviceCallback] = None,
    ):
        super().__init__(name or "Valves Group", callback)
        self.valves = valves
        for valve in valves:
            self._devices[valve.name] = valve

    def read_state(self):
        for valve in self.valves:
            valve.read_state()

    def __getitem__(self, key) -> Valve:
        return self.valves[key]

    def __setitem__(self, key: int, value: bool):
        self.valves[key].set_state(value)

    def get_fully_open_valves(self):
        return [valve for valve in self.valves if valve.is_open]

    def get_fully_closed_valves(self):
        return [valve for valve in self.valves if valve.is_close]

    def all_closed(self):
        for valve in self.valves:
            if valve.is_open:
                return False
        return True

    def not_all_closed(self):
        return not self.all_closed()

    def idle_all(self):
        """
        sets 0 duty cycle for all valves fast
        :return:
        """
        self.valves[0]._driver.reset()

    def open(self, index):
        self.valves[index].open()

    def close(self, index):
        self.valves[index].close()

    def set_state(self, index: int, value: bool):
        self.valves[index].set_state(value)

    def open_all(self):
        self._batch_open(self.valves)

    def close_all(self):
        self._batch_close(self.valves)

    def close_all_except(self, excluded_index):
        filtered_valves = [
            valve for i, valve in enumerate(self.valves) if i != excluded_index
        ]
        self._batch_close(filtered_valves)

    def _batch_open(self, valves: list[Valve]):
        for valve in valves:
            valve.open()

    def _batch_close(self, valves: list[Valve]):
        for valve in valves:
            valve.close()

    def get_drivers(self):
        return [valve._driver for valve in self.valves]
