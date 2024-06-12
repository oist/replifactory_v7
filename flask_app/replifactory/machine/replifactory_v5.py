from dataclasses import dataclass
from typing import Optional

from flask_app.replifactory.devices.laser import Laser
from flask_app.replifactory.devices.optical_density_sensor import OpticalDensitySensor
from flask_app.replifactory.devices.photodiode import Photodiode
from flask_app.replifactory.devices.pump import Pump
from flask_app.replifactory.devices.step_motor import Motor, MotorProfile_17HS15_1504S_X1, MotorProfile_XY42STH34_0354A
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
        super().__init__(
            connection_adapter=self._ftdi_adapter,
            *args, **kwargs
        )

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
        adc_driver = ADCDriver(port=self._ftdi_adapter.get_i2c_hw_port(I2C_PORT_ADC, "ADC"))
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
            Laser(laser_cs=cs, io_driver=io_driver_laser, name=f"Laser {cs // 2 + 1}", callback=self)
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
                port=self._ftdi_adapter.get_i2c_hw_port(address, name, ADT75Driver.registers)
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

    def close_valve(self, num: int):
        pass

    def open_valve(self, num: int):
        pass

    def stirrer(self, num: int, speed_ratio: float, time: Optional[float] = None):
        pass

    def measure_od(self, num: int):
        return 0.0

    def dilute(self, num: int, volume: float):
        pass

    def waste(self, num: int, volume: float):
        pass

    def laser_on(self, num: int):
        pass

    def laser_off(self, num: int):
        pass


@dataclass(frozen=True)
class ReplifactoryReactorParams:
    volume = 40.0  # in mL
    dilution_volume = 1.0  # in mL
    stirrer_slow_speed = 0.1
    stirrer_high_speed = 0.8
    stirrer_time = 2.0  # in seconds
    stirrer_cooldown_time = 4.0  # in seconds


class ReplifactoryReactor(Reactor):

    def __init__(self, num: int, machine: ReplifactoryMachine, **kwargs) -> None:
        super().__init__()
        self._num = num
        self._machine = machine
        self._params = ReplifactoryReactorParams(**kwargs)

    def __str__(self):
        return f"Reactor {self._num}"

    @property
    def params(self):
        return self._params

    def cmd_home(self):
        self._machine.close_valve(self._num)
        self.cmd_stirrer_off()

    def cmd_dilute_to_od(
        self,
        target_od: float,
        dilution_volume: Optional[float] = None,
        stirrer_speed: Optional[float] = None,
        stirrer_time: Optional[float] = None,
        stirrer_cooldown_time: Optional[float] = None,
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

        current_od = self.cmd_measure_od()
        changed_volume = 0.0
        while current_od > target_od:
            changed_volume += dilution_volume
            if changed_volume > self._params.volume:
                self._set_state(ReactorStates.ERROR)
                raise ReactorException("Dilution volume exceeded reactor volume")
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
        return self._machine.measure_od(self._num)

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


def check_compatible(*args, **kwargs):
    serial_number = kwargs.get("serial_number", "")
    return serial_number.startswith("FT05")
