import logging
from enum import Enum
from threading import RLock
from typing import Callable, Iterable, Optional, Union

from pyftdi.i2c import I2cController as FtdiI2cController
from pyftdi.i2c import I2cIOError
from pyftdi.i2c import I2cPort as FtdiI2cPort
from pyftdi.spi import SpiController
from pyftdi.spi import SpiPort as FtdiSpiPort

from flask_app.replifactory.util import ArrayOfBytesAsInt
from flask_app.replifactory.util import BraceMessage as __

HARDWARE_SESSION = RLock()

logger = logging.getLogger(__name__)


class HardwarePort:

    @property
    def session(self):
        return HARDWARE_SESSION

    @property
    def address(self):
        return 0

    def read(self, readlen: int = 0, relax: bool = True, start: bool = True):
        pass

    def exchange(self, out: Union[bytes, bytearray, Iterable[int]] = b'',
                 readlen: int = 0,
                 relax: bool = True, start: bool = True) -> bytes:
        pass

    def write(
        self,
        out: Union[bytes, bytearray, Iterable[int]],
        relax: bool = True,
        start: bool = True,
    ):
        pass

    def read_from(
        self, regaddr: int, readlen: int = 0, relax: bool = True, start: bool = True
    ) -> bytes:
        pass

    def write_to(
        self,
        regaddr: int,
        out: bytes | bytearray | Iterable[int],
        relax: bool = True,
        start: bool = True,
    ):
        pass


class LazyPort(HardwarePort):
    def __init__(self, get_port: Callable[[], HardwarePort]):
        self._get_port = get_port

    @property
    def port(self):
        return self._get_port()

    def exchange(self, out: Union[bytes, bytearray, Iterable[int]] = b'',
                 readlen: int = 0,
                 relax: bool = True, start: bool = True) -> bytes:
        return self.port.exchange(out, readlen, relax, start)

    def read(self, readlen: int = 0, relax: bool = True, start: bool = True):
        return self.port.read(readlen, relax, start)

    def write(
        self,
        out: Union[bytes, bytearray, Iterable[int]],
        relax: bool = True,
        start: bool = True,
    ):
        return self.port.write(out, relax, start)

    def read_from(
        self, regaddr: int, readlen: int = 0, relax: bool = True, start: bool = True
    ) -> bytes:
        return self.port.read_from(regaddr, readlen, relax, start)

    def write_to(
        self,
        regaddr: int,
        out: bytes | bytearray | Iterable[int],
        relax: bool = True,
        start: bool = True,
    ):
        return self.port.write_to(regaddr, out, relax, start)


class I2cPort(FtdiI2cPort, HardwarePort):
    def __init__(
        self,
        controller: "I2cController",
        address: int,
        name: str,
        registers: dict[int, str] = {},
    ):
        super().__init__(controller=controller, address=address)
        self._name = name
        self._registers = registers
        self.log = logging.getLogger(__name__)

    @property
    def address(self):
        return self._address

    def get_register_name(self, regaddr: int) -> str:
        try:
            return self._registers[regaddr]
        except KeyError:
            return "UNKNOWN"

    def read(self, readlen: int = 0, relax: bool = True, start: bool = True):
        result = super().read(readlen, relax, start)
        self.log.debug(
            __(
                "R i2c: {port_name} (0x{port_addr:02X}) len: {readlen} data: [{data}]",
                port_name=self._name,
                port_addr=self._address,
                readlen=readlen,
                data=result.hex(" ").upper(),
            )
        )
        return result

    def write(
        self,
        out: Union[bytes, bytearray, Iterable[int]],
        relax: bool = True,
        start: bool = True,
    ):
        return super().write(out, relax, start)

    def exchange(self, out: Union[bytes, bytearray, Iterable[int]] = b'',
                 readlen: int = 0,
                 relax: bool = True, start: bool = True) -> bytes:
        return super().exchange(out, readlen, relax, start)

    def write_to(
        self,
        regaddr: int,
        out: bytes | bytearray | Iterable[int],
        relax: bool = True,
        start: bool = True,
    ):
        logger.debug(
            __(
                "W i2c: {port_name} (0x{port_addr:02X}) reg: {regname} (0x{regaddr:02X}) data: {int_data} [{data}]",
                port_name=self._name,
                port_addr=self._address,
                regaddr=regaddr,
                regname=self.get_register_name(regaddr),
                int_data=ArrayOfBytesAsInt(out),
                data=bytearray(out).hex(" ").upper(),
            )
        )
        return super().write_to(regaddr, out, relax, start)

    def read_from(
        self, regaddr: int, readlen: int = 0, relax: bool = True, start: bool = True
    ) -> bytes:
        result = super().read_from(regaddr, readlen, relax, start)
        logger.debug(
            __(
                "R i2c: {port_name} (0x{port_addr:02X}) reg: {regname} (0x{regaddr:02X}) len: {readlen} data: {int_data} [{data}]",
                port_name=self._name,
                port_addr=self._address,
                regaddr=regaddr,
                regname=self.get_register_name(regaddr),
                int_data=ArrayOfBytesAsInt(result),
                data=result.hex(" ").upper(),
                readlen=readlen,
            )
        )
        return result


class I2cController(FtdiI2cController):
    def __init__(self):
        super().__init__()

    def get_verbose_port(
        self, address: int, name: str, registers: dict[int, str] = {}
    ) -> I2cPort:
        if not self._ftdi.is_connected:
            raise I2cIOError("FTDI controller not initialized")
        self.validate_address(address)
        if address not in self._slaves:
            self._slaves[address] = I2cPort(self, address, name, registers)
        return self._slaves[address]


class SpiPort(FtdiSpiPort, HardwarePort):
    def __init__(
        self,
        controller: "SpiController",
        cs: int,
        name: str,
        **kwargs,
    ):
        super().__init__(controller=controller, cs=cs, **kwargs)
        self._name = name

    @property
    def address(self):
        return self._cs

    def write(self, data: bytes | bytearray | Iterable[int]):
        logger.debug(
            __(
                "W spi: {port_name} (CS{cs}) data: {int_data} [{data}]",
                port_name=self._name,
                cs=self._cs,
                int_data=ArrayOfBytesAsInt(data),
                data=bytearray(data).hex(" ").upper(),
            )
        )
        return super().write(data)

    def read(self, length: int) -> bytes:
        result = super().read(length)
        logger.debug(
            __(
                "R spi: {port_name} (CS{cs}) len: {length} data: {int_data} [{data}]",
                port_name=self._name,
                cs=self._cs,
                int_data=ArrayOfBytesAsInt(result),
                data=result.hex(" ").upper(),
                length=length,
            )
        )
        return result


class Driver:

    def __init__(self, port: HardwarePort):
        self._port = port

    @property
    def port(self):
        return self._port

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


class StepperDriver(Driver):
    def rotate(
        self,
        n_steps: Optional[int],
        steps_per_second: Optional[int],
        cw: bool = True,
        wait: bool = False,
    ):
        pass

    def stop(self, emergency: bool = False, wait: bool = False):
        pass


class ThermometerDriver(Driver):
    def read(self) -> float:
        pass


class ADCDriver(Driver):
    def read(self) -> float:
        pass


class StirrerDriver(Driver):
    def stirrer(self, speed: float):
        pass

    def stop(self):
        pass


class TogglerState(Enum):
    pass


class ToggleDriver(Driver):

    @property
    def state(self) -> TogglerState:
        pass

    @state.setter
    def state(self, state: TogglerState):
        pass

    def toggle(
        self,
        state: Optional[TogglerState] = None,
        callback: Optional[Callable[[TogglerState], None]] = None,
    ):
        pass


class LaserState(TogglerState):
    ON = True
    OFF = False


class LaserDriver(ToggleDriver):
    def toggle(
        self,
        state: Optional[LaserState] = None,
        callback: Optional[Callable[[LaserState], None]] = None,
    ):
        pass


class EepromDriver(Driver):
    def write(self, address: int, data: bytes | bytearray):
        pass

    def read(self, address: Optional[int] = None, readlen: Optional[int] = None):
        pass
