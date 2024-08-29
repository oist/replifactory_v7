from dataclasses import dataclass
from typing import Optional

from usb.core import Device as UsbDevice

from biofactory.machine import (
    BaseMachine,
    ConnectionAdapter,
    Reactor,
    machine_command,
    reactor_command,
)
from biofactory.usb_manager import usbManager


class VirtualConnectionAdapter(ConnectionAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def connect(self, usb_device: Optional[UsbDevice] = None, *args, **kwargs):
        self._set_state(self.States.STATE_CONNECTING)
        self._usb_device = usb_device
        self._callbacks._on_conn_connected()
        self._set_state(self.States.STATE_OPERATIONAL)

    def disconnect(self, *args, **kwargs):
        self._set_state(self.States.STATE_DISCONNECTED)

    def get_device_info(self, *args, **kwargs):
        if self._usb_device is None:
            return {}
        return usbManager().get_device_info(self._usb_device)


class VirtualBiofactoryMachine(BaseMachine):

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            reactors_count=7,
            connection_adapter=VirtualConnectionAdapter(callbacks=self),
            **kwargs,
        )

    def cmd_home(self, num, *args, **kwargs):
        pass

    @machine_command
    def home(self):
        pass

    @machine_command
    def dilute(
        self,
        num: int,
        target_od: float,
        reactor_volume: float,
        dilution_volume: float,
        stirrer_speed: float,
        stirrer_time: float,
        stirrer_cooldown_time: float,
        feed_drug_ratio: float,  # 0 - only feed, 1 - only drug
        od_measurment_error: float = 0.01,
        *args,
        **kwargs,
    ):
        pass

    @machine_command
    def close_valve(self, num: int, wait=True):
        pass

    @machine_command
    def open_valve(self, num: int):
        pass

    @machine_command
    def stirrer(self, num: int, speed_ratio: float, wait_time: Optional[float] = None):
        pass

    @machine_command
    def stirrer_off(self, num: int, wait_time: Optional[float] = None):
        pass

    @machine_command
    def measure_od(self, num: int):
        return 0.0

    @machine_command
    def stop_pumps(self):
        pass

    @machine_command
    def stop_pump(self, device_id: str):
        pass

    @machine_command
    def connect_reactor_to_pumps(self, reactor_num: int):
        pass

    @machine_command
    def disconnect_reactors_from_pumps(self):
        pass

    @machine_command
    def feed(self, num: int, volume: float, disconnect_reactors=True):
        pass

    @machine_command
    def dose(self, num: int, volume: float, disconnect_reactors=True):
        pass

    @machine_command
    def discharge(self, num: int, volume: float, disconnect_reactors=True):
        pass

    @machine_command
    def laser_on(self, num: int):
        pass

    @machine_command
    def laser_off(self, num: int):
        pass


@dataclass(frozen=True)
class BiofactoryReactorParams:
    volume = 40.0  # in mL
    dilution_volume = 1.0  # in mL
    stirrer_slow_speed = 0.1
    stirrer_high_speed = 0.8
    stirrer_time = 2.0  # in seconds
    stirrer_cooldown_time = 4.0  # in seconds


class VirtualBiofactoryReactor(Reactor):

    # Reactor states:
    # Ready - vial is in the reactor ready to work
    # Operation blocking states:
    # Empty - no vial
    # Inoculating - introducing the culture into the vial
    # Mixing - ensuring the culture is homogenously distributed in the vial
    # Measuring - measure the optical density of the culture
    # Sterilizing - cleaning the vial
    # Diluting - reducing the concentration of the culture
    # Concentrating - increase the concentration of the culture
    # Feeding - adding nutrients to the culture
    # Dosing - adding drugs to the culture
    # Discharging - removing the culture from the vial
    # Cooling - cooling the vial
    # Warming - warming the vial
    # Sampling - taking a sample from the vial

    def __init__(self, *args, **kwargs) -> None:
        reactor_num = kwargs.pop("reactor_num", None)
        super().__init__(*args, reactor_num=reactor_num, **kwargs)
        self._machine: VirtualBiofactoryMachine = kwargs.pop("machine", None)
        if self._machine is None or not isinstance(
            self._machine, VirtualBiofactoryMachine
        ):
            raise ValueError("Invalid machine")
        self._params = BiofactoryReactorParams(**kwargs)

    def __str__(self):
        return f"Reactor {self._num}"

    def get_params(self):
        return self._params

    @reactor_command
    def home(self, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.cmd_home, (self._num,), {}), *args, **kwargs
        )

    @reactor_command
    def dilute(
        self,
        target_od: float,
        dilution_volume: Optional[float] = None,
        stirrer_speed: Optional[float] = None,
        stirrer_time: Optional[float] = None,
        stirrer_cooldown_time: Optional[float] = None,
        *args,
        **kwargs,
    ):
        dilution_volume = (
            self._params.dilution_volume if dilution_volume is None else dilution_volume
        )
        stirrer_speed = (
            self._params.stirrer_high_speed if stirrer_speed is None else stirrer_speed
        )
        stirrer_time = (
            self._params.stirrer_time if stirrer_time is None else stirrer_time
        )
        stirrer_cooldown_time = (
            self._params.stirrer_cooldown_time
            if stirrer_cooldown_time is None
            else stirrer_cooldown_time
        )
        return self._machine.add_operation(
            (
                self._machine.dilute,
                (),
                {
                    "num": self._num,
                    "target_od": target_od,
                    "reactor_volume": self._params.volume,
                    "dilution_volume": dilution_volume,
                    "stirrer_speed": stirrer_speed,
                    "stirrer_time": stirrer_time,
                    "stirrer_cooldown_time": stirrer_cooldown_time,
                    "feed_drug_ratio": 0.0,
                },
            ),
            *args,
            **kwargs,
        )

    @reactor_command
    def discharge(self, volume: float, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.discharge, (self._num, volume), {}), *args, **kwargs
        )

    @reactor_command
    def dose(self, volume: float, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.dose, (self._num, volume), {}), *args, **kwargs
        )

    @reactor_command
    def feed(self, volume: float, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.feed, (self._num, volume), {}), *args, **kwargs
        )

    @reactor_command
    def measure_od(self, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.measure_od, (self._num,), {}), *args, **kwargs
        )

    @reactor_command
    def stirrer(
        self, speed_ratio: float, wait_time: Optional[float] = None, *args, **kwargs
    ):
        return self._machine.add_operation(
            (self._machine.stirrer, (self._num, speed_ratio, wait_time), {}),
            *args,
            **kwargs,
        )

    @reactor_command
    def stirrer_off(self, wait_time: Optional[float] = None, *args, **kwargs):
        return self.stirrer(0.0, wait_time)

    @reactor_command
    def open_valve(self, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.open_valve, (self._num,), {}), *args, **kwargs
        )

    @reactor_command
    def close_valve(self, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.close_valve, (self._num,), {}), *args, **kwargs
        )

    @reactor_command
    def laser_on(self, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.laser_on, (self._num,), {}), *args, **kwargs
        )

    @reactor_command
    def laser_off(self, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.laser_off, (self._num,), {}), *args, **kwargs
        )


VirtualBiofactoryMachine.reactor_class = VirtualBiofactoryReactor


def check_compatible(*args, **kwargs):
    serial_number = kwargs.get("serial_number", "")
    return serial_number == "VIRTUAL"
