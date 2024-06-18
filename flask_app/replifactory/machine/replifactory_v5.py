from dataclasses import dataclass
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
)

SPI_INTERFACE = 1
SPI_CS_COUNT = 4
SPI_FREQ = 1e4  # 10KHz
SPI_MODE = 3
SPI_TURBO = True
I2C_INTERFACE = 2
I2C_FREQ = 5e4  # try 100e3

PUMPS_COUNT = 4

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

        # self._pumps: list[Pump] = []
        # it's important to init pump drivers before valves
        for cs in range(PUMPS_COUNT):
            step_motor_driver = StepMotorDriver(
                port=self._ftdi_adapter.get_spi_hw_port(f"Stepper {cs + 1}", cs=cs)
            )
            profile = (
                MotorProfile_17HS15_1504S_X1()
                if cs != 0
                else MotorProfile_XY42STH34_0354A()
            )
            motor = Motor(step_motor_driver, profile=profile, name=f"Motor {cs + 1}")
            pump = Pump(motor, name=f"Pump {cs + 1}", callback=self)
            # self._pumps.append(pump)
            self._dev_manager.add_devices(pump)
            # self._devices[pump.id] = pump
            # self._drivers += [step_motor_driver]

        pwm_driver = PWMDriver(
            port=self._ftdi_adapter.get_i2c_hw_port(
                address=I2C_PORT_PWM, name="PWM", registers=PWMDriver.registers
            )
        )
        # self._drivers += [pwm_driver]
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
        # self._devices[stirrers_group.id] = stirrers_group

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
        # self._valves = valves
        self._dev_manager.add_devices(*valves)
        # for valve in valves:
        #     self._devices[valve.id] = valve

        valves_group = ValvesGroup(valves)
        self._dev_manager.add_devices(valves_group)
        # self._devices[valves_group.id] = valves_group

        # adc_port_callback = self._ftdi_driver.get_first_active_i2c_port_callback(
        #     I2C_PORT_ADC, "ADC"
        # )
        # if isinstance(I2C_PORT_ADC, Iterable):
        #     try:
        #         i2c_adc_port = ftdi_driver.get_first_active_port(I2C_PORT_ADC, "ADC")
        #     except ConnectionError as e:
        #         self.log.error("Failed connection to ADC", exc_info=e)
        #         i2c_adc_port = None
        # else:
        #     i2c_adc_port = ftdi_driver.get_i2c_port(I2C_PORT_ADC, "ADC")
        # if i2c_adc_port:
        # io_port_callback = self._ftdi_driver.get_i2c_port_callback(
        #     I2C_PORT_IO_ADC, "IO_ADC", IOPortDriver.registers
        # )
        adc_driver = ADCDriver(
            port=self._ftdi_adapter.get_i2c_hw_port(I2C_PORT_ADC, "ADC")
        )
        # self._drivers += [adc_driver]

        # io_driver_reactor = IOPortDriver(port=self._ftdi_adapter.get_i2c_hw_port(I2C_PORT_IO_REACTOR, "IO_REACTOR", IOPortDriver.registers))
        # self._drivers += [io_driver_reactor]
        # reactor_selector = ReactorSelector(io_driver_reactor, callback=self)
        # self._devices[reactor_selector.id] = reactor_selector
        # self._dev_manager.add_devices(reactor_selector)

        # laser_port_callback = self._ftdi_driver.get_i2c_port_callback(
        #     I2C_PORT_IO_LASER, "IO_LASERS", IOPortDriver.registers
        # )
        io_driver_laser = IOPortDriver(
            port=self._ftdi_adapter.get_i2c_hw_port(
                I2C_PORT_IO_LASER, "IO_LASERS", IOPortDriver.registers
            )
        )
        # self._drivers += [io_driver_laser]
        lasers = [
            Laser(
                laser_cs=cs,
                io_driver=io_driver_laser,
                name=f"Laser {cs // 2 + 1}",
                callback=self,
            )
            for cs in range(1, VIALS_COUNT * 2, 2)
        ]
        # for laser in lasers:
        #     self._devices[laser.id] = laser
        self._dev_manager.add_devices(*lasers)

        io_driver_adc = IOPortDriver(
            port=self._ftdi_adapter.get_i2c_hw_port(
                I2C_PORT_IO_ADC, "IO_ADC", IOPortDriver.registers
            )
        )
        # self._drivers += [io_driver_adc]
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
        # for od_sensor in od_sensors:
        #     self._devices[od_sensor.id] = od_sensor
        self._dev_manager.add_devices(*od_sensors)

        # _vials = []
        # for i in range(VIALS_COUNT):
        #     num = i + 1
        #     vial = Vial(
        #         name=f"Vial {num}",
        #         valve=self._get_valve(f"valve-{num}"),
        #         stirrer=self._get_stirrer(f"stirrer-{num}"),
        #         od_sensor=self._get_od_sensor(f"optical-density-sensor-{num}"),
        #         media_pump=self._get_pump("pump-1"),
        #         drug_pump=self._get_pump("pump-2"),
        #         waste_pump=self._get_pump("pump-4"),
        #         callback=self,
        #     )
        #     # self._devices[vial.id] = vial
        #     _vials.append(vial)
        # self._dev_manager.add_devices(*_vials)

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
            # self._drivers += [thermometer_driver]
            thermometers += [
                Thermometer(
                    driver=thermometer_driver,
                    name=f"Thermometer 0x{address:02X}",
                    callback=self,
                )
            ]
        # for thermometer in thermometers:
        #     self._devices[thermometer.id] = thermometer
        self._dev_manager.add_devices(*thermometers)

    def cmd_home(self, num, *args, **kwargs):
        self.close_valve(num)
        self.stirrer_off(num)

    @machine_command
    def home(self):
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
        *args,
        **kwargs,
    ):
        if feed_drug_ratio < 0.0:
            feed_drug_ratio = 0.0
        if feed_drug_ratio > 1.0:
            feed_drug_ratio = 1.0
        feed_volume = dilution_volume * (1 - feed_drug_ratio)
        dose_volume = dilution_volume * feed_drug_ratio
        current_od = self.measure_od(num)
        if current_od is None:
            self._set_state(ReactorStates.ERROR)
            raise ReactorException("Failed to measure OD")
        changed_volume = 0.0
        while current_od > target_od:
            changed_volume += dilution_volume
            if changed_volume > reactor_volume:
                self._set_state(ReactorStates.ERROR)
                raise ReactorException("Dilution volume exceeded reactor volume")
            self.discharge(num, dilution_volume)
            self.feed(num, feed_volume)
            self.dose(num, dose_volume)
            self.stirrer(num, stirrer_speed, stirrer_time)
            self.stirrer_off(num, stirrer_cooldown_time)
            current_od = self.measure_od(num)

    @machine_command
    def close_valve(self, num: int, wait=True):
        device_id = self._get_valve_id(num)
        return self.execute(device_id, "close", wait=wait)

    @machine_command
    def open_valve(self, num: int):
        device_id = self._get_valve_id(num)
        return self.execute(device_id, "open")

    @machine_command
    def stirrer(self, num: int, speed_ratio: float, wait_time: Optional[float] = None):
        device_id = self._get_stirrer_id(num)
        self.execute(device_id, "set_speed", speed_ratio)
        if wait_time:
            time.sleep(wait_time)

    @machine_command
    def stirrer_off(self, num: int, wait_time: Optional[float] = None):
        return self.stirrer(num, 0.0, wait_time)

    @machine_command
    def measure_od(self, num: int):
        device_id = self._get_od_sensor_id(num)
        return self.execute(device_id, "measure_od")

    @machine_command
    def feed(self, num: int, volume: float):
        self.stop_pumps()
        self.connect_reactor_to_pumps(num)
        device_id = self._get_feed_pump_id()
        self.execute(device_id, "pump", volume)
        self.disconnect_reactors_from_pumps()

    @machine_command
    def stop_pumps(self):
        for i in range(PUMPS_COUNT):
            self.execute(f"pump-{i+1}", "stop")

    @machine_command
    def connect_reactor_to_pumps(self, reactor_num: int):
        for reactor in self._reactors:
            if reactor._num != reactor_num:
                self.close_valve(reactor._num, wait=False)
        self.open_valve(reactor_num)

    @machine_command
    def disconnect_reactors_from_pumps(self):
        for reactor in self._reactors:
            wait = False if reactor._num != self._reactors[-1]._num else True
            self.close_valve(reactor._num, wait=wait)

    @machine_command
    def dose(self, num: int, volume: float):
        self.stop_pumps()
        self.connect_reactor_to_pumps(num)
        device_id = self._get_dose_pump_id()
        self.execute(device_id, "pump", volume)
        self.disconnect_reactors_from_pumps()

    @machine_command
    def discharge(self, num: int, volume: float):
        self.stop_pumps()
        self.connect_reactor_to_pumps(num)
        device_id = self._get_discharge_pump_id()
        self.execute(device_id, "pump", volume)
        self.disconnect_reactors_from_pumps()

    @machine_command
    def laser_on(self, num: int):
        device_id = self._get_laser_id(num)
        return self.execute(device_id, "switch_on")

    @machine_command
    def laser_off(self, num: int):
        device_id = self._get_laser_id(num)
        return self.execute(device_id, "switch_off")

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
        self._machine = kwargs.pop("machine", None)
        if self._machine is None or not isinstance(self._machine, ReplifactoryMachine):
            raise ValueError("Invalid machine")
        self._params = ReplifactoryReactorParams(**kwargs)

    def __str__(self):
        return f"Reactor {self._num}"

    @property
    def params(self):
        return self._params

    def cmd_home(self, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.cmd_home, (self._num,), {}), *args, **kwargs
        )

    def cmd_dilute(
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
                self._machine.cmd_dilute_to_od,
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

    def cmd_discharge(self, volume: float, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.waste, (self._num, volume), {}), *args, **kwargs
        )

    def cmd_dose(self, volume: float, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.dose, (self._num, volume), {}), *args, **kwargs
        )

    def cmd_feed(self, volume: float, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.feed, (self._num, volume), {}), *args, **kwargs
        )

    def cmd_measure_od(self, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.measure_od, (self._num,), {}), *args, **kwargs
        )

    def cmd_stirrer(
        self, speed_ratio: float, time: Optional[float] = None, *args, **kwargs
    ):
        return self._machine.add_operation(
            (self._machine.stirrer, (self._num, speed_ratio, time), {}), *args, **kwargs
        )

    def cmd_stirrer_off(self, cooldown_time: Optional[float] = None, *args, **kwargs):
        return self.cmd_stirrer(0.0, cooldown_time)

    def cmd_open_valve(self, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.open_valve, (self._num,), {}), *args, **kwargs
        )

    def cmd_close_valve(self, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.close_valve, (self._num,), {}), *args, **kwargs
        )

    def cmd_laser_on(self, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.laser_on, (self._num,), {}), *args, **kwargs
        )

    def cmd_laser_off(self, *args, **kwargs):
        return self._machine.add_operation(
            (self._machine.laser_off, (self._num,), {}), *args, **kwargs
        )


ReplifactoryMachine.reactor_class = ReplifactoryReactor


def check_compatible(*args, **kwargs):
    serial_number = kwargs.get("serial_number", "")
    return serial_number.startswith("FT05")
