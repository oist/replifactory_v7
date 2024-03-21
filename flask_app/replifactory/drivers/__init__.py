from threading import RLock
from typing import Callable, Iterable, Optional, Union

HARDWARE_SESSION = RLock()


class HardwarePort:

    @property
    def session(self):
        return HARDWARE_SESSION

    def read(self, readlen: int = 0, relax: bool = True, start: bool = True):
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


class Driver:
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
