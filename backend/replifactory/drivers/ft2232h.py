import errno
import logging
import threading
from dataclasses import dataclass
from string import printable as printablechars
from typing import Optional, Union

import usb
from pyftdi.ftdi import Ftdi, FtdiError
from pyftdi.i2c import I2cNackError
from pyftdi.usbtools import UsbTools
from usb.core import Device as UsbDevice

from replifactory.drivers import Driver, I2cController, SpiController, I2cPort, LazyPort, SpiPort
from replifactory.drivers.ftdi import FtdiEeprom
from replifactory.virtual_usb_device import VirtualUsbDevice


@dataclass
class ParsedDescriptor:
    url: str
    ifcount: int
    description: str


class FtdiDriver(Driver):
    _log = logging.getLogger(f"{__name__}.FtdiDriver")

    def __init__(
        self,
        usb_device: Optional[UsbDevice] = None,
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
        self._usb_device = usb_device
        self._spi_controller = None
        self._spi_cs_count = spi_cs_count
        self._spi_default_freq = spi_freq
        self._spi_default_mode = spi_mode
        self._spi_interface = spi_interface
        self._spi_turbo = spi_turbo
        self._i2c_controller = None
        self._i2c_default_freq = i2c_freq
        self._i2c_interface = i2c_interface
        self._i2c_retry_count = i2c_retry_count
        self._ftdi = Ftdi()
        self._opened_ports = {}

    @property
    def is_connected(self):
        return self._usb_device and self._ftdi.is_connected

    def connect(self, usb_device: UsbDevice):
        if self._usb_device is None:
            self._ftdi.open_from_device(usb_device)
            self._usb_device = usb_device
            # self.i2c_controller
            # self.spi_controller

    def close(self):
        self.terminate()

    def reset(self):
        self._ftdi.reset(usb_reset=True)

    def terminate(self):
        with self._lock:
            self._opened_ports = {}
            if self._i2c_controller is not None:
                self._i2c_controller.terminate()
                self._i2c_controller = None
            if self._spi_controller is not None:
                self._spi_controller.terminate()
                self._spi_controller = None
            if self._ftdi is not None:
                self._ftdi.close()
            if self._usb_device is not None:
                UsbTools.release_device(self._usb_device)
                self._usb_device = None
            UsbTools.flush_cache()

    @property
    def i2c_controller(self) -> I2cController:
        if self._i2c_controller is None and self.is_connected:
            with self._lock:
                if self._i2c_controller is None:
                    self._i2c_controller = I2cController()
                    if not isinstance(self._usb_device, VirtualUsbDevice):
                        self._i2c_controller.set_retry_count(self._i2c_retry_count)
                        self._i2c_controller.configure(
                            self._usb_device,
                            frequency=self._i2c_default_freq,
                            interface=self._i2c_interface,
                        )
        return self._i2c_controller

    def get_spi_controller(self) -> SpiController:
        if self._spi_controller is None and self.is_connected:
            with self._lock:
                if self._spi_controller is None:
                    self._spi_controller = SpiController(
                        cs_count=self._spi_cs_count, turbo=self._spi_turbo
                    )
                    if not isinstance(self._usb_device, VirtualUsbDevice):
                        self._spi_controller.configure(
                            self._usb_device,
                            frequency=self._spi_default_freq,
                            interface=self._spi_interface,
                        )
        return self._spi_controller

    def get_i2c_hw_port(self, address: int | list[int], name: str, registers: dict[int, str] = {}):
        if isinstance(address, list):
            return LazyPort(
                get_port=self.get_first_active_i2c_port_callback(address, name, registers)
            )
        return LazyPort(
            get_port=self.get_i2c_port_callback(address, name, registers)
        )

    def get_i2c_port_callback(
        self, address: int, name: str, registers: dict[int, str] = {}
    ):
        def callback():
            return self.get_i2c_port(address, name, registers)

        return callback

    def get_i2c_port(
        self, address: int, name: str, registers: dict[int, str] = {}
    ) -> I2cPort:
        port_id = f"i2c_{address}_{name}"
        if port_id in self._opened_ports:
            return self._opened_ports[port_id]

        port = self.i2c_controller.get_verbose_port(address, name, registers)
        self._opened_ports[port_id] = port
        return port

    def get_spi_hw_port(self, name: str, cs: int, freq: Optional[float] = None, mode: Optional[int] = None):
        return LazyPort(get_port=self.get_spi_port_callback(name, cs, freq, mode))

    def get_spi_port_callback(
        self, name: str, cs: int, freq: Optional[float] = None, mode: Optional[int] = None
    ):
        def callback():
            return self.get_spi_port(name, cs, freq, mode)

        return callback

    def get_spi_port(
        self, name: str, cs: int, freq: Optional[float] = None, mode: Optional[int] = None
    ) -> SpiPort:
        port_id = f"spi_{cs}_{name}"
        if port_id in self._opened_ports:
            return self._opened_ports[port_id]

        port = self.get_spi_controller().get_named_port(
            name=name,
            cs=cs,
            freq=freq or self._spi_default_freq,
            mode=mode or self._spi_default_mode,
        )
        self._opened_ports[port_id] = port
        return port

    # SMB_READ_RANGE = list(range(0x30, 0x38)) + list(range(0x50, 0x60))

    # HIGHEST_I2C_SLAVE_ADDRESS = 0x78

    def get_first_active_i2c_port_callback(
        self, possible_addresses: list[int], name: str, registers: dict[int, str] = {}
    ):
        def callback():
            return self.get_first_active_port(possible_addresses, name, registers)

        return callback

    def get_first_active_port(
        self, possible_addresses: list[int], name: str, registers: dict[int, str] = {}
    ) -> I2cPort:
        """Scan an I2C bus and return first answered port."""
        for addr in possible_addresses:
            port = self.get_i2c_port(addr, name, registers)
            try:
                port.read(4)  # TODO: move to mcp3421 driver
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
                try:
                    cls._update_device_description_from_replifactory(dev)
                    device = dev
                except FtdiError:
                    pass
                except Exception:
                    cls._log.exception("Can't read device serial number")
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
        devices_with_serial_number = []
        for dev in devs:
            try:
                cls._update_device_description_from_replifactory(dev)
            except FtdiError:
                pass
            except Exception:
                cls._log.exception("Can't read device serial number")
            else:
                devices_with_serial_number.append(dev)
        return devices_with_serial_number

    @classmethod
    def read_device_config(cls, device: Union[str, UsbDevice]):
        eeprom = FtdiEeprom()
        try:
            eeprom.open(device)
            return {
                "serial": eeprom.serial,
                "manufacturer": eeprom.manufacturer,
                "product": eeprom.product,
            }
        except FtdiError as exc:
            if exc.errno == errno.EBUSY or [
                True for arg in exc.args if f"Errno {errno.EBUSY}" in arg
            ]:
                cls._log.info(f"Device {device._str()} is busy")
            else:
                cls._log.exception("Read usb device configuration failed")
            raise exc
        finally:
            eeprom.close()

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
