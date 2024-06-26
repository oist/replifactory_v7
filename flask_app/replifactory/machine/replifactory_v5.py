from dataclasses import dataclass
import logging
import time
from typing import Optional

from flask_app.replifactory.devices.laser import Laser
from flask_app.replifactory.devices.optical_density_sensor import OpticalDensitySensor
from flask_app.replifactory.devices.photodiode import Photodiode
from flask_app.replifactory.devices.pump import Pump
from flask_app.replifactory.devices.step_motor import (
    Motor,
    MotorProfile_17HS15_1504S_X1,
    MotorProfile_XY42STH34_0354A,
)
from flask_app.replifactory.devices.stirrer import Stirrer
from flask_app.replifactory.devices.stirrers_group import StirrersGroup
from flask_app.replifactory.devices.thermometer import Thermometer
from flask_app.replifactory.devices.valve import Valve
from flask_app.replifactory.devices.valves_group import ValvesGroup
from flask_app.replifactory.drivers.adt75 import ADT75Driver
from flask_app.replifactory.drivers.ft2232h import FtdiDriver
from flask_app.replifactory.drivers.l6470h import StepMotorDriver
from flask_app.replifactory.drivers.mcp3421 import ADCDriver
from flask_app.replifactory.drivers.pca9555 import IOPortDriver
from flask_app.replifactory.drivers.pca9685 import PWMDriver
from flask_app.replifactory.machine import (
    BaseMachine,
    FtdiConnectionAdapter,
    Reactor,
    ReactorException,
    ReactorStates,
    machine_command,
    reactor_command,
)

SPI_INTERFACE = 1
SPI_CS_COUNT = 4
SPI_FREQ = 1e4  # 10KHz
SPI_MODE = 3
SPI_TURBO = True
I2C_INTERFACE = 2
I2C_FREQ = 5e4  # try 100e3

USED_PUMPS = [1, 2, 4]

VIALS_COUNT = 7
VAVLE_PWM_CHANNEL_START_ADDR = 8
VALVES_COUNT = VIALS_COUNT
STIRRER_PWM_CHANNEL_START_ADDR = 0
STIRRERS_COUNT = VIALS_COUNT

VALVE_OPEN_DUTY_CYCLE = 0.03
VALVE_CLOSED_DUTY_CYCLE = 0.12
VALVE_CHANGE_STATE_TIME = 0.5

I2C_PORT_PWM = 0x70  # PCA9685 [1110000]
I2C_PORT_ADC = [*range(0x68, 0x70)]  # it could be in range from 0x68 to 0x6F
I2C_PORT_IO_ADC = 0x21  # PCA 9555
I2C_PORT_IO_LASER = 0x20  # PCA 9555
I2C_PORT_THERMOMETER_1 = 0x48  # ADT75
I2C_PORT_THERMOMETER_2 = 0x49  # ADT75
I2C_PORT_THERMOMETER_3 = 0x4A  # ADT75


class ReplifactoryMachine(BaseMachine):

    def __init__(self, *args, **kwargs):
        self._ftdi_adapter = FtdiConnectionAdapter(
            ftdi_driver=FtdiDriver(
                spi_interface=SPI_INTERFACE,
                spi_cs_count=SPI_CS_COUNT,
                spi_freq=SPI_FREQ,
                spi_mode=SPI_MODE,
                spi_turbo=SPI_TURBO,
                i2c_interface=I2C_INTERFACE,
                i2c_freq=I2C_FREQ,
            ),
            callbacks=self,
            reconnect=True,
        )
        super().__init__(reactors_count=7, connection_adapter=self._ftdi_adapter, *args, **kwargs)

        # Replifactory v5 layout

        # it's important to init pump drivers before valves, to stop motors before valves closing
        for pump_num in USED_PUMPS:
            step_motor_driver = StepMotorDriver(
                port=self._ftdi_adapter.get_spi_hw_port(f"Stepper {pump_num}", cs=pump_num - 1)
            )
            profile = (
                MotorProfile_17HS15_1504S_X1()
                if pump_num != 1
                else MotorProfile_XY42STH34_0354A()
            )
            motor = Motor(step_motor_driver, profile=profile, name=f"Motor {pump_num}")
            pump = Pump(motor, name=f"Pump {pump_num}", callback=self)
            self._dev_manager.add_devices(pump)

        # instantiate stirrers and valves
        pwm_driver = PWMDriver(
            port=self._ftdi_adapter.get_i2c_hw_port(
                address=I2C_PORT_PWM, name="PWM", registers=PWMDriver.registers
            )
        )
        stirrers = [
            Stirrer(
                pwm_channel=pwm_channel,
                driver=pwm_driver,
                name=f"Stirrer {i+1}",
                callback=self,
            )
            for i, pwm_channel in enumerate(
                reversed(
                    range(
                        STIRRER_PWM_CHANNEL_START_ADDR,
                        STIRRER_PWM_CHANNEL_START_ADDR + STIRRERS_COUNT,
                    )
                )
            )
        ]
        self._dev_manager.add_devices(*stirrers)
        stirrers_group = StirrersGroup(stirrers)
        self._dev_manager.add_devices(stirrers_group)
        valves = [
            Valve(
                pwm_channel=pwm_channel,
                driver=pwm_driver,
                open_duty_cycle=VALVE_OPEN_DUTY_CYCLE,
                closed_duty_cycle=VALVE_CLOSED_DUTY_CYCLE,
                change_state_delay=VALVE_CHANGE_STATE_TIME,
                name=f"Valve {pwm_channel - VAVLE_PWM_CHANNEL_START_ADDR + 1}",
                callback=self,
                init_state=Valve.States.STATE_CLOSE,
            )
            for pwm_channel in range(
                VAVLE_PWM_CHANNEL_START_ADDR,
                VAVLE_PWM_CHANNEL_START_ADDR + VALVES_COUNT,
            )
        ]
        self._dev_manager.add_devices(*valves)
        valves_group = ValvesGroup(valves)
        self._dev_manager.add_devices(valves_group)

        # instantiate optical density sensors
        adc_driver = ADCDriver(
            port=self._ftdi_adapter.get_i2c_hw_port(I2C_PORT_ADC, "ADC")
        )
        io_driver_laser = IOPortDriver(
            port=self._ftdi_adapter.get_i2c_hw_port(
                I2C_PORT_IO_LASER, "IO_LASERS", IOPortDriver.registers
            )
        )
        lasers = [
            Laser(
                laser_cs=cs,
                io_driver=io_driver_laser,
                name=f"Laser {cs // 2 + 1}",
                callback=self,
            )
            for cs in range(1, VIALS_COUNT * 2, 2)
        ]
        self._dev_manager.add_devices(*lasers)

        io_driver_adc = IOPortDriver(
            port=self._ftdi_adapter.get_i2c_hw_port(
                I2C_PORT_IO_ADC, "IO_ADC", IOPortDriver.registers
            )
        )
        photodiodes = [
            Photodiode(
                diode_cs=cs,
                adc_driver=adc_driver,
                io_driver=io_driver_adc,
                name=f"Photodiode {VIALS_COUNT - cs}",
            )
            for cs in reversed(range(VIALS_COUNT))
        ]
        od_sensors = [
            OpticalDensitySensor(
                photodiode=photodiodes[i],
                laser=lasers[i],
                callback=self,
                name=f"Optical Density Sensor {i+1}",
            )
            for i in range(VIALS_COUNT)
        ]
        self._dev_manager.add_devices(*od_sensors)

        # instantiate thermometers
        thermometers = []
        for address, name in {
            I2C_PORT_THERMOMETER_1: "THERMOMETER_1 (MB)",
            I2C_PORT_THERMOMETER_2: "THERMOMETER_2",
            I2C_PORT_THERMOMETER_3: "THERMOMETER_3",
        }.items():
            thermometer_driver = ADT75Driver(
                port=self._ftdi_adapter.get_i2c_hw_port(
                    address, name, ADT75Driver.registers
                )
            )
            thermometers += [
                Thermometer(
                    driver=thermometer_driver,
                    name=f"Thermometer 0x{address:02X}",
                    callback=self,
                )
            ]
        self._dev_manager.add_devices(*thermometers)

    def cmd_home(self, num, *args, **kwargs):
        self.close_valve(num)
        self.stirrer_off(num)

    @machine_command
    def home(self):
        self._log.debug("Homing all reactors")
        self.stop_pumps()
        self.disconnect_reactors_from_pumps()
        for reactor in self._reactors:
            self.stirrer_off(reactor._num, wait_time=None)

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
        if self._log.isEnabledFor(logging.DEBUG):
            method_params = locals()
            self._log.debug(f"Diluting with args: {method_params}")
        else:
            self._log.info(f"Diluting reactor {num} to OD {target_od}")
        reactor = self.get_reactor(num)
        if feed_drug_ratio < 0.0:
            feed_drug_ratio = 0.0
        if feed_drug_ratio > 1.0:
            feed_drug_ratio = 1.0
        feed_volume = dilution_volume * (1 - feed_drug_ratio)
        dose_volume = dilution_volume * feed_drug_ratio
        current_od = self.measure_od(num)
        if current_od is None:
            reactor._set_state(ReactorStates.ERROR)
            raise ReactorException("Failed to measure OD")
        changed_volume = 0.0
        while current_od > target_od:
            if self._cancel_long_operation_event.is_set():
                # reactor._set_state(ReactorStates.READY)
                self._cancel_long_operation_event.clear()
                self._log.info(f"Cancelled dilution of reactor {num}")
                break;
            changed_volume += dilution_volume
            if changed_volume > reactor_volume:
                reactor._set_state(ReactorStates.ERROR)
                self._log.warning(f"Reactor {num} dilution volume exceeded reactor volume")
                raise ReactorException("Dilution volume exceeded reactor volume")
            self.discharge(num, dilution_volume, disconnect_reactors=False)
            self.feed(num, feed_volume, disconnect_reactors=False)
            self.dose(num, dose_volume, disconnect_reactors=False)
            self.stirrer(num, stirrer_speed, stirrer_time)
            self.stirrer_off(num, stirrer_cooldown_time)
            previous_od = current_od
            current_od = self.measure_od(num)
            if current_od - od_measurment_error > previous_od:
                reactor._set_state(ReactorStates.ERROR)
                self._log.warning(f"Reactor {num} OD increased after dilution")
                raise ReactorException("OD increased after dilution")
        self.disconnect_reactors_from_pumps()
        self._log.info(f"Reactor {num} diluted to OD {current_od}")

    @machine_command
    def close_valve(self, num: int, wait=True):
        self._log.debug(f"Closing valve {num}")
        device_id = self._get_valve_id(num)
        return self.execute_device_command(device_id, "close", wait=wait)

    @machine_command
    def open_valve(self, num: int):
        self._log.debug(f"Opening valve {num}")
        device_id = self._get_valve_id(num)
        return self.execute_device_command(device_id, "open")

    @machine_command
    def stirrer(self, num: int, speed_ratio: float, wait_time: Optional[float] = None):
        self._log.debug(f"Setting stirrer {num} speed to {speed_ratio}")
        device_id = self._get_stirrer_id(num)
        self.execute_device_command(device_id, "set_speed", speed_ratio)
        if wait_time:
            time.sleep(wait_time)

    @machine_command
    def stirrer_off(self, num: int, wait_time: Optional[float] = None):
        self._log.debug(f"Turning off stirrer {num}")
        return self.stirrer(num, 0.0, wait_time)

    @machine_command
    def measure_od(self, num: int):
        self._log.debug(f"Measuring OD of reactor {num}")
        device_id = self._get_od_sensor_id(num)
        return self.execute_device_command(device_id, "measure_od")

    @machine_command
    def stop_pumps(self):
        self._log.debug("Stopping all pumps")
        for pump_num in USED_PUMPS:
            self.stop_pump(f"pump-{pump_num}")

    @machine_command
    def stop_pump(self, device_id: str):
        self._log.debug(f"Stopping pump {device_id}")
        self.execute_device_command(device_id, "stop")
        while self.execute_device_command(device_id, "read_state") == Pump.States.STATE_WORKING:
            time.sleep(0.1)

    @machine_command
    def connect_reactor_to_pumps(self, reactor_num: int):
        self._log.debug(f"Connecting reactor {reactor_num} to pumps")
        for reactor in self._reactors:
            if reactor._num != reactor_num:
                self.close_valve(reactor._num, wait=False)
        self.open_valve(reactor_num)

    @machine_command
    def disconnect_reactors_from_pumps(self):
        self._log.debug("Disconnecting reactors from pumps")
        for reactor in self._reactors:
            wait = False if reactor._num != self._reactors[-1]._num else True
            self.close_valve(reactor._num, wait=wait)

    @machine_command
    def feed(self, num: int, volume: float, disconnect_reactors=True):
        self._log.debug(f"Feeding reactor {num} with {volume} mL")
        self.stop_pumps()
        self.connect_reactor_to_pumps(num)
        device_id = self._get_feed_pump_id()
        self.execute_device_command(device_id, "pump", volume)
        if disconnect_reactors:
            self.disconnect_reactors_from_pumps()

    @machine_command
    def dose(self, num: int, volume: float, disconnect_reactors=True):
        self._log.debug(f"Dosing reactor {num} with {volume} mL")
        self.stop_pumps()
        self.connect_reactor_to_pumps(num)
        device_id = self._get_dose_pump_id()
        self.execute_device_command(device_id, "pump", volume)
        if disconnect_reactors:
            self.disconnect_reactors_from_pumps()

    @machine_command
    def discharge(self, num: int, volume: float, disconnect_reactors=True):
        self._log.debug(f"Discharging reactor {num} with {volume} mL")
        self.stop_pumps()
        self.connect_reactor_to_pumps(num)
        device_id = self._get_discharge_pump_id()
        self.execute_device_command(device_id, "pump", volume)
        if disconnect_reactors:
            self.disconnect_reactors_from_pumps()

    @machine_command
    def laser_on(self, num: int):
        self._log.debug(f"Turning on laser {num}")
        device_id = self._get_laser_id(num)
        return self.execute_device_command(device_id, "switch_on")

    @machine_command
    def laser_off(self, num: int):
        self._log.debug(f"Turning off laser {num}")
        device_id = self._get_laser_id(num)
        return self.execute_device_command(device_id, "switch_off")

    def _get_stirrer_id(self, num: int):
        return f"stirrer-{num}"

    def _get_valve_id(self, num: int):
        return f"valve-{num}"

    def _get_laser_id(self, num: int):
        return f"laser-{num}"

    def _get_od_sensor_id(self, num: int):
        return f"optical-density-sensor-{num}"

    def _get_feed_pump_id(self):
        return "pump-1"

    def _get_dose_pump_id(self):
        return "pump-2"

    def _get_discharge_pump_id(self):
        return "pump-4"


@dataclass(frozen=True)
class ReplifactoryReactorParams:
    volume = 40.0  # in mL
    dilution_volume = 1.0  # in mL
    stirrer_slow_speed = 0.1
    stirrer_high_speed = 0.8
    stirrer_time = 2.0  # in seconds
    stirrer_cooldown_time = 4.0  # in seconds


class ReplifactoryReactor(Reactor):

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
        super().__init__(reactor_num=reactor_num, *args, **kwargs)
        self._machine: ReplifactoryMachine = kwargs.pop("machine", None)
        if self._machine is None or not isinstance(self._machine, ReplifactoryMachine):
            raise ValueError("Invalid machine")
        self._params = ReplifactoryReactorParams(**kwargs)

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
            (self._machine.stirrer, (self._num, speed_ratio, wait_time), {}), *args, **kwargs
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


ReplifactoryMachine.reactor_class = ReplifactoryReactor


def check_compatible(*args, **kwargs):
    serial_number = kwargs.get("serial_number", "")
    return serial_number.startswith("FT05")
