import logging
from typing import Optional

from flask_app.replifactory.devices import Device
from flask_app.replifactory.devices.optical_density_sensor import OpticalDensitySensor
from flask_app.replifactory.devices.pump import Pump
from flask_app.replifactory.devices.stirrer import Stirrer
from flask_app.replifactory.devices.valve import Valve


class Vial(Device):
    def __init__(
        self,
        valve: Valve,
        stirrer: Stirrer,
        od_sensor: OpticalDensitySensor,
        media_pump: Pump,
        drug_pump: Pump,
        waste_pump: Pump,
        name: Optional[str] = None,
        min_volume: float = 0.0,
        max_volume: float = 100.0,
        **kwargs,
    ):
        super().__init__(name or "Vial", **kwargs)
        self._min_volume = min_volume
        self._max_volume = max_volume
        self._volume = min_volume
        self._valve = valve
        self._stirrer = stirrer
        self._od_sensor = od_sensor
        self._media_pump = media_pump
        self._drug_pump = drug_pump
        self._waste_pump = waste_pump

    def read_state(self):
        self._set_state(self.States.STATE_OPERATIONAL)

    def get_data(self):
        data = super().get_data()
        data.update(
            {
                "volume": self._volume,
            }
        )
        return data

    def add_volume(self, volume: float):
        # self._set_state(self.States.STATE_WORKING)
        self._volume += volume
        self._set_state(self.States.STATE_OPERATIONAL, force=True)

    def reset(self):
        self._volume = 0.0

    def get_drivers(self):
        return []
