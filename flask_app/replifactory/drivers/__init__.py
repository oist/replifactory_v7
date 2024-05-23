import logging
from enum import Enum
from threading import RLock
from typing import Callable, Iterable, Optional, Union

from pyftdi.i2c import I2cController as FtdiI2cController
from pyftdi.i2c import I2cIOError
from pyftdi.i2c import I2cPort as FtdiI2cPort
from pyftdi.spi import SpiController as FtdiSpiController
from pyftdi.spi import SpiPort as FtdiSpiPort

from flask_app.replifactory.util import ArrayOfBytesAsInt
from flask_app.replifactory.util import BraceMessage as __

HARDWARE_SESSION = RLock()


class HardwarePort:

    @property
    def session(self):
        return HARDWARE_SESSION

    @property
    def address(self):
        return 0

    def read(self, readlen: int = 0, *args, **kwargs) -> bytes:
        pass

    def exchange(
        self,
        out: Union[bytes, bytearray, Iterable[int]] = b"",
        readlen: int = 0,
        *args,
        **kwargs,
    ) -> bytes:
        pass

    def write(self, out: Union[bytes, bytearray, Iterable[int]], *args, **kwargs):
        pass

    def read_from(self, regaddr: int, readlen: int = 0, *args, **kwargs) -> bytes:
        pass

    def write_to(
        self, regaddr: int, out: bytes | bytearray | Iterable[int], *args, **kwargs
    ):
        pass


class LazyPort(HardwarePort):
    def __init__(self, get_port: Callable[[], HardwarePort]):
        self._get_port = get_port
        self._port = None

    @property
    def port(self):
        if self._port is None:
            self._port = self._get_port()
        return self._port

    @property
    def address(self):
        return self.port.address

    def exchange(
        self,
        out: Union[bytes, bytearray, Iterable[int]] = b"",
        readlen: int = 0,
        *args,
        **kwargs,
    ) -> bytes:
        with self.session:
            return self.port.exchange(out, readlen, *args, **kwargs)

    def read(self, readlen: int = 0, *args, **kwargs):
        with self.session:
            return self.port.read(readlen, *args, **kwargs)

    def write(self, out: Union[bytes, bytearray, Iterable[int]], *args, **kwargs):
        with self.session:
            return self.port.write(out, *args, **kwargs)

    def read_from(self, regaddr: int, readlen: int = 0, *args, **kwargs) -> bytes:
        with self.session:
            return self.port.read_from(regaddr, readlen, *args, **kwargs)

    def write_to(
        self, regaddr: int, out: bytes | bytearray | Iterable[int], *args, **kwargs
    ):
        with self.session:
            return self.port.write_to(regaddr, out, *args, **kwargs)


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
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    def address(self):
        return self._address

    def get_register_name(self, regaddr: int) -> str:
        try:
            return self._registers[regaddr]
        except KeyError:
            return "UNKNOWN"

    def read(self, readlen: int = 0, *args, **kwargs):
        with self.session:
            result = super().read(readlen, *args, **kwargs)
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

    def write(self, out: Union[bytes, bytearray, Iterable[int]], *args, **kwargs):
        with self.session:
            return super().write(out, *args, **kwargs)

    def exchange(
        self,
        out: Union[bytes, bytearray, Iterable[int]] = b"",
        readlen: int = 0,
        *args,
        **kwargs,
    ) -> bytes:
        with self.session:
            return super().exchange(out, readlen, *args, **kwargs)

    def write_to(
        self, regaddr: int, out: bytes | bytearray | Iterable[int], *args, **kwargs
    ):
        with self.session:
            self.log.debug(
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
            return super().write_to(regaddr, out, *args, **kwargs)

    def read_from(self, regaddr: int, readlen: int = 0, *args, **kwargs) -> bytes:
        with self.session:
            result = super().read_from(regaddr, readlen, *args, **kwargs)
            self.log.debug(
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

    def write(self, data: bytes | bytearray | Iterable[int], *args, **kwargs):
        with self.session:
            if kwargs.pop("log", True):
                self.log.debug(
                    __(
                        "W spi: {port_name} (CS{cs}) data: {int_data} [{data}]",
                        port_name=self._name,
                        cs=self._cs,
                        int_data=ArrayOfBytesAsInt(data),
                        data=bytearray(data).hex(" ").upper(),
                    )
                )
            return super().write(data, *args, **kwargs)

    def read(self, length: int, *args, **kwargs) -> bytes:
        with self.session:
            write_log = kwargs.pop("log", True)
            result = super().read(length, *args, **kwargs)
            if write_log:
                self.log.debug(
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

    def exchange(
        self,
        out: Union[bytes, bytearray, Iterable[int]] = b"",
        readlen: int = 0,
        *args,
        **kwargs,
    ) -> bytes:
        with self.session:
            self.log.debug(
                    __(
                        "W spi: {port_name} (CS{cs}) data: {int_data} [{data}]",
                        port_name=self._name,
                        cs=self._cs,
                        int_data=ArrayOfBytesAsInt(out),
                        data=bytearray(out).hex(" ").upper(),
                    )
                )
            if isinstance(out, Iterable):
                for b in out:
                    self.write([b], log=False, *args, **kwargs)
            else:
                for b in range(len(out)):
                    # start = b == 0
                    # stop = readlen <= 0 and b == len(payload) - 1
                    # self.spi_port.write(out=[payload[b]], start=start, stop=stop)
                    self.write(out=[out[b]], log=False, *args, **kwargs)
            res = bytearray()
            if readlen > 0:
                for b in range(readlen):
                    # stop = b == readlen - 1
                    # res += self.spi_port.read(readlen=1, start=False, stop=stop)
                    res += self.read(1, log=False, *args, **kwargs)
                self.log.debug(
                    __(
                        "Read from SPI (cs={cs}) {int_data} {data}",
                        cs=self.address,
                        data=res,
                        int_data=ArrayOfBytesAsInt(res),
                    )
                )
            return res


class SpiController(FtdiSpiController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_named_port(self, name: str, cs: int, freq: float | None = None, mode: int = 0) -> SpiPort:
        origin_port = super().get_port(cs, freq, mode)
        self._spi_ports[cs] = SpiPort(self, cs, name, cs_hold=origin_port._cs_hold, spi_mode=mode)
        self._spi_ports[cs].set_frequency(freq)
        self._flush()
        return self._spi_ports[cs]


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
