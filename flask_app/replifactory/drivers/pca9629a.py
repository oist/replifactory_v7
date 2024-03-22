import logging
import signal
from enum import Enum
from time import sleep
from typing import Iterable, Optional, SupportsBytes, SupportsIndex

from flask_app.replifactory.drivers import HardwarePort, StepperDriver

logger = logging.getLogger(__name__)

AUTOINCREMENT_BIT = 1 << 7

REGISTER_MODE = 0x00
REGISTER_WDTOI = 0x01
REGISTER_WDCNTL = 0x02
REGISTER_IO_CFG = 0x03
REGISTER_INTMODE = 0x04
REGISTER_MSK = 0x05
REGISTER_INSTAT = 0x06
REGISTER_IP = 0x07
# motor parameter registers start here
REGISTER_INT_MTR_ACT = 0x08
REGISTER_EXTRASTEPS0 = 0x09
REGISTER_EXTRASTEPS1 = 0x0A
REGISTER_OP_CFG_PHS = 0x0B
REGISTER_OP_STAT_TO = 0x0C
REGISTER_RUNCTL = 0x0D
REGISTER_RDCTL = 0x0E
REGISTER_PMA = 0x0F
REGISTER_LOOPDLY_CW = 0x10
REGISTER_LOOPDLY_CCW = 0x11
REGISTER_CWSCOUNTL = 0x12
REGISTER_CWSCOUNTH = 0x13
REGISTER_CCSWCOUNTL = 0x14
REGISTER_CCSWCOUNTH = 0x15
REGISTER_CWPWL = 0x16
REGISTER_CWPWH = 0x17
REGISTER_CCWPWL = 0x18
REGISTER_CCWPWH = 0x19
# motor parameter registers end here
REGISTER_MCNTL = 0x1A
REGISTER_SUBADR1 = 0x1B
REGISTER_SUBADR2 = 0x1C
REGISTER_SUBADR3 = 0x1D
REGISTER_ALLCALLADR = 0x1E
REGISTER_STEPCOUNT0 = 0x1F
REGISTER_STEPCOUNT1 = 0x20
REGISTER_STEPCOUNT2 = 0x21
REGISTER_STEPCOUNT3 = 0x22

REGISTERS_NAMES = {
    value: name.removeprefix("REGISTER_")
    for name, value in locals().items()
    if name.startswith("REGISTER_")
}
REGISTERS_NAMES |= {
    (regaddr | AUTOINCREMENT_BIT):  f"{name}_AI"
    for regaddr, name in REGISTERS_NAMES.items()
}


def get_register_name(regaddr: int) -> str:
    try:
        return REGISTERS_NAMES[regaddr]
    except KeyError:
        return f"UNKNOWN({regaddr})"


MODE_RESPONDS_ALLCALL = 0b00000001
MODE_NOT_RESPOND_ALLCALL = 0b00000000

MODE_ALLCALL_BIT = 0
MODE_SUBADDR3_BIT = 1
MODE_SUBADDR2_BIT = 2
MODE_SUBADDR1_BIT = 3
MODE_OUTPUTS_BIT = 4
MODE_EN_INT_OUT = 5
MODE_SLEEP_BIT = 6

MCTL_RUN_BIT = 7
MCTL_RESTART_BIT = 6
MCTL_EMERGENCY_STOP_BIT = 5
MCTL_START_IGNORE_P0_BIT = 4
MCTL_P0_POLARITY_BIT = 3


PMA_CONTINUOUSLY = 0x00
PMA_ONCE = 0x01


def is_set(value: int, bit: int) -> bool:
    return (value >> bit) & 1 == 1


class ControllerRegister:
    def __init__(
        self, address: int, value: int | Iterable[SupportsIndex] | SupportsBytes
    ):
        if isinstance(value, (Iterable, SupportsBytes)):
            value = int.from_bytes(bytes(value), "little")
        self._value = value
        self._address = address

    @property
    def value(self) -> int:
        return self._value

    def to_bytes(self) -> bytes:
        return self._value.to_bytes(1, "little")

    def _is_set(self, bit: int) -> bool:
        return is_set(self._value, bit)


class StepperMode(ControllerRegister):
    def __init__(
        self, mode: int | Iterable[SupportsIndex] | SupportsBytes = 0b00000001
    ):
        super().__init__(REGISTER_MODE, mode)

    def __str__(self):
        allcall = (
            "Responds to All Call"
            if self._is_set(MODE_ALLCALL_BIT)
            else "Does not respond to All Call"
        )
        subbaddr3 = (
            "Responds to Subaddress 3"
            if self._is_set(MODE_SUBADDR3_BIT)
            else "Does not respond to Subaddress 3"
        )
        subbaddr2 = (
            "Responds to Subaddress 2"
            if self._is_set(MODE_SUBADDR2_BIT)
            else "Does not respond to Subaddress 2"
        )
        subaddr1 = (
            "Responds to Subaddress 1"
            if self._is_set(MODE_SUBADDR1_BIT)
            else "Does not respond to Subaddress 1"
        )
        outputs = (
            "Outputs change on I2C-bus ACK"
            if self._is_set(MODE_OUTPUTS_BIT)
            else "Outputs change on I2C-bus STOP condition"
        )
        int_out = (
            "Disable INT output pin"
            if self._is_set(MODE_EN_INT_OUT)
            else "Enable INT output pin"
        )
        sleep = (
            "Low-power sleep mode. Oscillator off."
            if self._is_set(MODE_SLEEP_BIT)
            else "Normal mode"
        )
        return f"""
{self._value:08b} {get_register_name(self._address)}
 \u2502\u2502\u2502\u2502\u2502\u2502\u2514{allcall}
 \u2502\u2502\u2502\u2502\u2502\u2514{subbaddr3}
 \u2502\u2502\u2502\u2502\u2514{subbaddr2}
 \u2502\u2502\u2502\u2514{subaddr1}
 \u2502\u2502\u2514{outputs}
 \u2502\u2514{int_out}
 \u2514{sleep}"""
        # return f"{sleep}\n{int_out}\n{outputs}\n{subaddr1}\n{subbaddr2}\n{subbaddr3}\n{allcall}"


class MotorControl(ControllerRegister):

    class Directions(Enum):
        CCW_THEN_CW = 0b11
        CW_THEN_CCW = 0b10
        CCW = 0b01
        CW = 0b00

    def __init__(self, value: int | Iterable[SupportsIndex] | SupportsBytes = 0):
        super().__init__(REGISTER_MCNTL, value)

    @property
    def is_running(self) -> bool:
        return self._is_set(MCTL_RUN_BIT)

    def set_start(self):
        self._value |= 1 << MCTL_RUN_BIT
        return self

    def set_stop(self):
        self._value &= ~(1 << MCTL_RUN_BIT)
        return self

    def set_emergency_stop(self):
        self._value |= 1 << MCTL_EMERGENCY_STOP_BIT
        return self

    def set_restart(self):
        self._value |= 1 << MCTL_RESTART_BIT
        return self

    def enable_start_ignore_p0(self):
        self._value |= 1 << MCTL_START_IGNORE_P0_BIT
        return self

    def disable_start_ignore_p0(self):
        self._value &= ~(1 << MCTL_START_IGNORE_P0_BIT)
        return self

    def set_direction(self, direction: Directions):
        self._value &= ~0b11
        self._value |= direction.value
        return self

    def __str__(self):
        run = "Running" if self._is_set(MCTL_RUN_BIT) else "Stoped"
        restart = (
            "Re-start motor for new speed and operation"
            if self._is_set(MCTL_RESTART_BIT)
            else "Self clear after new speed starts running"
        )
        emergency_stop = (
            "Emergency stop motor"
            if self._is_set(MCTL_EMERGENCY_STOP_BIT)
            else "Self clear after motor stop and bit 7 also clears to 0"
        )
        # ignore_p0 = (
        #     "Enable START (bit 7) ignore caused by P0 state"
        #     if self._is_set(MCTL_START_IGNORE_P0_BIT)
        #     else "Disable START (bit 7) ignore caused by P0 state"
        # )
        # p0_polarity = (
        #     "P0 is active low"
        #     if self._is_set(MCTL_P0_POLARITY_BIT)
        #     else "P0 is active high"
        # )
        match self._value & 0x03:
            case 0b00:
                direction = "Rotate clockwise"
            case 0b01:
                direction = "Rotate counter-clockwise"
            case 0b10:
                direction = "Rotate clockwise first, then counter-clockwise"
            case 0b11:
                direction = "Rotate counter-clockwise first, then clockwise"

        return f"""
{(self._value >> 5 & 0b111):03b}xxx{(self._value & 0b11):b} {get_register_name(self._address)}
\u2502\u2502\u2502   \u2514{direction}
\u2502\u2502\u2514{emergency_stop}
\u2502\u2514{restart}
\u2514{run}"""


class StepMotorDriver(StepperDriver):

    def __init__(self, port: HardwarePort):
        self._port = port
        self._mode = StepperMode()
        self._control = MotorControl()
        self._speed = 0x1000

    def init(self):
        """
        This method is invoked right after connecting to the machine.
        """
        pass

    def terminate(self):
        """
        This method is invoked right before disconnecting from the machine.
        """
        pass

    def reset(self):
        """
        This method is invoked right after reconnecting to the machine.
        """
        pass

    def rotate(
        self,
        n_steps: Optional[int] = None,
        steps_per_second: Optional[int] = None,
        cw: bool = True,
        wait: bool = False,
    ):
        step_count_register = REGISTER_CWSCOUNTL if cw else REGISTER_CCSWCOUNTL
        step_count_register |= AUTOINCREMENT_BIT
        with self._port.session:
            motor_control = MotorControl(self._port.read_from(REGISTER_MCNTL, 1))
            if motor_control.is_running:
                raise ValueError("Motor is already running")
            if n_steps is not None:
                self._port.write_to(step_count_register, n_steps.to_bytes(2, "little"))
                self._port.write_to(REGISTER_PMA, [PMA_ONCE])
            else:
                self._port.write_to(step_count_register, [1, 0])
                self._port.write_to(REGISTER_PMA, [PMA_CONTINUOUSLY])
            if steps_per_second is not None:
                speed = steps_per_second
            else:
                speed = self._speed
            self._port.write_to(REGISTER_CWPWL | AUTOINCREMENT_BIT, speed.to_bytes(2, "little"))
            motor_control.set_start()
            self._port.write_to(REGISTER_MCNTL, motor_control.to_bytes())
            while wait and motor_control.is_running:
                motor_control = MotorControl(self._port.read_from(REGISTER_MCNTL, 1))
                sleep(1)

    def stop(self, emergency: bool = False, wait: bool = False):
        with self._port.session:
            motor_control = MotorControl(self._port.read_from(REGISTER_MCNTL, 1))
            if emergency:
                motor_control.set_emergency_stop()
            else:
                motor_control.set_stop()
            self._port.write_to(REGISTER_MCNTL, motor_control.to_bytes())

    @property
    def port(self):
        return self._port

    @property
    def mode(self) -> StepperMode:
        mode = self.port.read_from(REGISTER_MODE, 1)
        self._mode = StepperMode(mode)
        return self._mode

    @mode.setter
    def mode(self, value: StepperMode):
        self.port.write_to(REGISTER_MODE, value.to_bytes())
        self._mode = value

    @property
    def control(self) -> MotorControl:
        control = self.port.read_from(REGISTER_MCNTL, 1)
        self._control = MotorControl(control)
        return self._control

    @control.setter
    def control(self, value: MotorControl):
        self.port.write_to(REGISTER_MCNTL, value.to_bytes())
        self._control = value

    @property
    def steps_counter(self):
        return int.from_bytes(self.port.read_from(REGISTER_STEPCOUNT0 | AUTOINCREMENT_BIT, 4), "little")


global exit_flag

if __name__ == "__main__":
    from flask_app.replifactory.drivers.ft2232h import FtdiDriver
    from flask_app.replifactory.usb_manager import usbManager

    PORT_ADDR = 0x21
    I2C_INTERFACE = 2
    I2C_FREQ = 5e4

    usb_manager = usbManager()
    usb_device = usb_manager.find_device()
    if usb_device is None:
        print("No devices found")
        exit(1)

    ftdi_driver = FtdiDriver(
        i2c_interface=I2C_INTERFACE,
        i2c_freq=I2C_FREQ,
    )
    stepper_driver = StepMotorDriver(
        port=ftdi_driver.get_i2c_hw_port(PORT_ADDR, "STEPPER_CONTROLLER", registers=REGISTERS_NAMES)
    )

    def terminate():
        stepper_driver.terminate()
        ftdi_driver.terminate()

    def exit_gracefully(signum, frame):
        stepper_driver.stop()
        terminate()
        exit(0)

    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    ftdi_driver.connect(usb_device)
    stepper_driver.init()

    logger.debug(f"{stepper_driver.mode}")
    logger.debug(f"{stepper_driver.control}")
    stepper_driver.rotate()
    logger.debug(f"{stepper_driver.control}")

    while stepper_driver.control.is_running:
        logger.debug(f"steps: {stepper_driver.steps_counter}")
        logger.info("Press Ctrl+C to stop")
        sleep(1)

    logger.debug(f"{stepper_driver.control}")

    terminate()
