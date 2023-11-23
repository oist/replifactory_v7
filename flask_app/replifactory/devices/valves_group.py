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

    def connect(self, reset_state: bool = True):
        for valve in self.valves:
            valve.connect()

    # def sync_is_open_to_pwm(self):
    #     for v in range(1, 8):
    #         status = self.get_is_open(v)
    #         if status == 1:
    #             self.is_open[v] = True
    #         elif status == 0:
    #             self.is_open[v] = False
    #         else:
    #             self.is_open[v] = None

    def get_fully_open_valves(self):
        return [valve for valve in self.valves if valve.is_open]

    def get_fully_closed_valves(self):
        return [valve for valve in self.valves if valve.is_close]

    # def get_is_open(self, valve_number):
    #     return self.get_percent_open_pwm(valve=valve_number)

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
        # assert self.pwm_controller.lock.acquire(timeout=10)
        # try:
        #     self.pwm_controller.stop_all()
        #     for valve in range(1, 9):
        #         led_number = self.led_numbers[valve]
        #         self.pwm_controller.set_duty_cycle(led_number=led_number, duty_cycle=0)
        #     self.pwm_controller.start_all()
        # finally:
        #     self.pwm_controller.lock.release()

    # def set_duty_cycle(self, valve, duty_cycle):
    #     """
    #     sets the duty cycle of the pwm signal for the valve.
    #     Stops pwm controller while changing value, to prevent the motor from
    #     moving after writing the first byte.
    #     """
    #     led_number = self.led_numbers[valve]
    #     assert self.pwm_controller.lock.acquire(timeout=10)
    #     try:
    #         # self.pwm_controller.stop_all()
    #         self.pwm_controller.set_duty_cycle(
    #             led_number=led_number, duty_cycle=duty_cycle
    #         )
    #         # self.pwm_controller.start_all()
    #         time.sleep(0.04)
    #     finally:
    #         self.pwm_controller.lock.release()

    def open(self, index):
        self.valves[index].open()

    def close(self, index):
        self.valves[index].close()

    def set_state(self, index: int, value: bool):
        self.valves[index].set_state(value)

    # def get_percent_open_pwm(self, valve):
    #     return self.valves[valve].
    #     if self.pwm_controller.is_sleeping():
    #         return -1
    #     led_number = self.led_numbers[valve]
    #     duty_cycle = self.pwm_controller.get_duty_cycle(led_number=led_number)
    #     duty_cycle = round(duty_cycle, 3)
    #     op, cl = self.DUTY_CYCLE_OPEN, self.DUTY_CYCLE_CLOSED
    #     percent_closed = (duty_cycle - op) / (cl - op)
    #     percent_open = 1 - percent_closed
    #     return percent_open

    def open_all(self):
        self._batch_open(self.valves)
        # open_valves = self.get_fully_open_valves()
        # for valve in range(1, 8):
        #     if valve not in open_valves:
        #         self.open(valve=valve)

    def close_all(self):
        self._batch_close(self.valves)
        # assert not self.device.is_pumping(), "can't close last valve while pumping"
        # closed_valves = self.get_fully_closed_valves()
        # for valve in range(1, 8):
        #     if valve not in closed_valves:
        #         self.close(valve=valve)

    def close_all_except(self, excluded_index):
        filtered_valves = [
            valve for i, valve in enumerate(self.valves) if i != excluded_index
        ]
        self._batch_close(filtered_valves)
        # for v in range(1, 8):
        #     if v != valve and v not in self.get_fully_closed_valves():
        #         self.close(valve=v)

    def _batch_open(self, valves: list[Valve]):
        for valve in valves:
            valve.open()

    def _batch_close(self, valves: list[Valve]):
        for valve in valves:
            valve.close()
