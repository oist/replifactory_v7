import errno
import logging
import threading
from dataclasses import dataclass
from string import printable as printablechars
from typing import Iterable, Optional, Union

import usb
from pyftdi.ftdi import Ftdi, UsbDeviceDescriptor, FtdiError
from pyftdi.i2c import I2cController as FtdiI2cController
from pyftdi.i2c import I2cIOError, I2cNackError
from pyftdi.i2c import I2cPort as FtdiI2cPort
from pyftdi.spi import SpiController, SpiPort
from pyftdi.usbtools import UsbTools
from usb.core import Device as UsbDevice

from replifactory.drivers.ftdi import FtdiEeprom
from replifactory.util import ArrayOfBytesAsInt
from replifactory.util import BraceMessage as __

logger = logging.getLogger(__name__)


class I2cPort(FtdiI2cPort):
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

    @property
    def address(self):
        return self._address

    def get_register_name(self, regaddr: int) -> str:
        try:
            return self._registers[regaddr]
        except KeyError:
            return "UNKNOWN"

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


@dataclass
class ParsedDescriptor:
    url: str
    ifcount: int
    description: str


class FtdiDriver:
    # usb_device: UsbDevice
    # i2c_controller: I2cController
    # spi_controller: SpiController

    def __init__(
        self,
        usb_device: UsbDevice,
        spi_cs_count: int = 1,
        spi_freq: Optional[float] = None,
        spi_mode: int = 0,
        spi_turbo: bool = True,
        i2c_freq: Optional[float] = None,
        i2c_retry_count: int = 1,
        spi_interface: int = 1,
        i2c_interface: int = 2,
    ):
        self._lock = threading.RLock()
        self.usb_device = usb_device
        self.spi_controller = None
        self.spi_cs_count = spi_cs_count
        self.spi_default_freq = spi_freq
        self.spi_default_mode = spi_mode
        self.spi_interface = spi_interface
        self.spi_turbo = spi_turbo
        self._i2c_controller = None
        self.i2c_default_freq = i2c_freq
        self.i2c_interface = i2c_interface
        self.i2c_retry_count = i2c_retry_count
        self._ftdi = Ftdi()

    def is_connected(self):
        return self._ftdi.is_connected

    def connect(self):
        self._ftdi.open_from_device(self.usb_device)

    def close(self):
        self.terminate()

    def terminate(self):
        with self._lock:
            if self._i2c_controller is not None:
                self._i2c_controller.terminate()
            if self.spi_controller is not None:
                self.spi_controller.terminate()
            if self._ftdi is not None:
                self._ftdi.close()
            UsbTools.release_device(self.usb_device)
            UsbTools.flush_cache()

    @property
    def i2c_controller(self) -> I2cController:
        if self._i2c_controller is None:
            with self._lock:
                if self._i2c_controller is None:
                    self._i2c_controller = I2cController()
                    self._i2c_controller.set_retry_count(self.i2c_retry_count)
                    self._i2c_controller.configure(
                        self.usb_device,
                        frequency=self.i2c_default_freq,
                        interface=self.i2c_interface,
                    )
        return self._i2c_controller

    def get_i2c_port(
        self, address: int, name: str, registers: dict[int, str] = {}
    ) -> I2cPort:
        port = self.i2c_controller.get_verbose_port(address, name, registers)
        return port

    def get_spi_port(
        self, cs: int, freq: Optional[float] = None, mode: int = None
    ) -> SpiPort:
        with self._lock:
            if not self.spi_controller:
                self.spi_controller = SpiController(
                    cs_count=self.spi_cs_count, turbo=self.spi_turbo
                )
                self.spi_controller.configure(
                    self.usb_device,
                    frequency=self.spi_default_freq,
                    interface=self.spi_interface,
                )
        return self.spi_controller.get_port(
            cs=cs,
            freq=freq or self.spi_default_freq,
            mode=mode or self.spi_default_mode,
        )

    # SMB_READ_RANGE = list(range(0x30, 0x38)) + list(range(0x50, 0x60))

    # HIGHEST_I2C_SLAVE_ADDRESS = 0x78

    def get_first_active_port(
        self, possible_addresses: list[int], name: str, registers: dict[int, str] = {}
    ) -> I2cPort:
        """Scan an I2C bus and return first answered port."""
        i2c = self.i2c_controller
        for addr in possible_addresses:
            port = i2c.get_verbose_port(addr, name, registers)
            try:
                port.read(0)
                return port
            except I2cNackError:
                pass
            try:
                port.write([])
                return port
            except I2cNackError:
                pass
        raise ConnectionError(f"No answer from {possible_addresses}")

    @classmethod
    def find_device(cls, **kwargs):
        device = None
        if "serial" in kwargs:
            serial = kwargs["serial"]
            devices = cls.list_devices()
            for dev in devices:
                if dev.serial == serial:
                    device = dev
        else:
            dev = usb.core.find(**kwargs)
            if dev:
                cls._update_device_description_from_replifactory(dev)
                device = dev
        return device

    @classmethod
    def _update_device_description_from_replifactory(cls, device: UsbDevice):
        config = cls.read_device_config(device)
        device._serial_number = config["serial"]
        device._manufacturer = config["manufacturer"]
        device._product = config["product"]
        return device

    @classmethod
    def list_devices(cls, vdict=Ftdi.VENDOR_IDS, pdict=Ftdi.PRODUCT_IDS):
        vps = set()
        vendors = set(vdict.values())
        for vid in vendors:
            products = pdict.get(vid, [])
            for pid in products:
                vps.add((vid, products[pid]))
        devs = set()
        for vid, pid in vps:
            devs.update(UsbTools._find_devices(vid, pid, True))
        for dev in devs:
            try:
                cls._update_device_description_from_replifactory(dev)
            except FtdiError:
                pass
        return devs

    # @classmethod
    # def get_devices_descriptions(cls):
    #     devices = cls.list_devices()
    #     return [cls.read_device_description(device) for device in devices]

    # @classmethod
    # def read_device_description(cls, device_with_inum: Tuple[UsbDeviceDescriptor, int]):
    #     parsed_descriptor = cls.parse_device_descriptor(device_with_inum)
    #     device_descriptor, _ = device_with_inum
    #     device_description = {
    #         "device": device_descriptor,
    #         "config": {},
    #         "is_busy": False,
    #         "error": "",
    #     }
    #     try:
    #         device_description["config"] = cls.read_device_config(f"{parsed_descriptor.url}/2")
    #     except FtdiError as exc:
    #         if exc.errno == errno.EBUSY or [True for arg in exc.args if f"Errno {errno.EBUSY}" in arg]:
    #             device_description["is_busy"] = True
    #         else:
    #             device_description["error"] = exc.strerror if exc.strerror else str(exc.args)
    #     return device_description

    @classmethod
    def read_device_config(cls, device: Union[str, UsbDevice]):
        try:
            eeprom = FtdiEeprom()
            eeprom.open(device)
            return eeprom._config
        except FtdiError as exc:
            if exc.errno == errno.EBUSY or [True for arg in exc.args if f"Errno {errno.EBUSY}" in arg]:
                logger.info(f"Device {device} is busy")
            else:
                logger.exception("Read usb device configuration failed")
            raise exc

    @classmethod
    def parse_device_descriptor(cls, descriptor):
        scheme = "ftdi"
        vdict = Ftdi.VENDOR_IDS
        pdict = Ftdi.PRODUCT_IDS
        indices = {}  # Dict[Tuple[int, int], int]
        desc, ifcount = descriptor
        ikey = (desc.vid, desc.pid)
        indices[ikey] = indices.get(ikey, 0) + 1
        # try to find a matching string for the current vendor
        vendors = []
        # fallback if no matching string for the current vendor is found
        vendor = "%04x" % desc.vid
        for vidc in vdict:
            if vdict[vidc] == desc.vid:
                vendors.append(vidc)
        if vendors:
            vendors.sort(key=len)
            vendor = vendors[0]
        # try to find a matching string for the current vendor
        # fallback if no matching string for the current product is found
        product = "%04x" % desc.pid
        try:
            products = []
            productids = pdict[desc.vid]
            for prdc in productids:
                if productids[prdc] == desc.pid:
                    products.append(prdc)
            if products:
                product = products[0]
        except KeyError:
            pass
        fmt = "%s://%s"
        parts = [vendor, product]
        sernum = desc.sn
        if not sernum:
            sernum = ""
        if [c for c in sernum if c not in printablechars or c == "?"]:
            serial = "%d" % indices[ikey]
        else:
            serial = sernum
        if serial:
            parts.append(serial)
        elif desc.bus is not None and desc.address is not None:
            parts.append("%x" % desc.bus)
            parts.append("%x" % desc.address)
        # the description may contain characters that cannot be
        # emitted in the output stream encoding format
        try:
            url = fmt % (scheme, ":".join(parts))
        except Exception:
            url = fmt % (scheme, ":".join([vendor, product, "???"]))
        try:
            if desc.description:
                description = "%s" % desc.description
            else:
                description = ""
        except Exception:
            description = ""
        return ParsedDescriptor(url, ifcount, description)
