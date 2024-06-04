from typing import Optional
from flask_app.replifactory.machine import Reactor


class ReplifactoryMachine:

    def close_valve(self, num: int):
        pass

    def open_valve(self, num: int):
        pass

    def stirrer(self, num: int, speed_ratio: float, time: Optional[float] = None):
        pass

    def measure_od(self, num: int):
        pass

    def dilute(self, num: int, volume: float):
        pass

    def waste(self, num: int, volume: float):
        pass

    def laser_on(self, num: int):
        pass

    def laser_off(self, num: int):
        pass


class ReplifactoryReactor(Reactor):

    def __init__(self, num: int, machine: ReplifactoryMachine) -> None:
        super().__init__()
        self._num = num
        self._machine = machine

    def cmd_home(self):
        self._machine.close_valve(self._num)
        self.cmd_stirrer_off()

    def cmd_dilute_to_od(
        self,
        target_od: float,
        dilution_volume: float,
        stirrer_speed: float,
        stirrer_time: float,
        stirrer_cooldown_time: float,
    ):
        current_od = self.cmd_measure_od()
        while current_od > target_od:
            self.cmd_waste(dilution_volume)
            self.cmd_dilute(dilution_volume)
            self.cmd_stirrer(stirrer_speed, stirrer_time)
            self.cmd_stirrer_off(stirrer_cooldown_time)
            current_od = self.cmd_measure_od()

    def cmd_dilute(self, volume: float):
        self._machine.dilute(self._num, volume)

    def cmd_waste(self, volume: float):
        self._machine.waste(self._num, volume)

    def cmd_measure_od(self):
        self._machine.measure_od(self._num)

    def cmd_stirrer(self, speed_ratio: float, time: Optional[float] = None):
        self._machine.stirrer(self._num, speed_ratio, time)

    def cmd_stirrer_off(self, cooldown_time: Optional[float] = None):
        self.cmd_stirrer(0.0, cooldown_time)

    def cmd_open_valve(self):
        self._machine.open_valve(self._num)

    def cmd_close_valve(self):
        self._machine.close_valve(self._num)

    def cmd_laser_on(self):
        self._machine.laser_on(self._num)

    def cmd_laser_off(self):
        self._machine.laser_off(self._num)
