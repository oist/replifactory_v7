import sys
from typing import Union
if "_pyftdi.ftdi" in sys.modules:
    from _pyftdi.ftdi import Ftdi as _Ftdi
    from _pyftdi.ftdi import FtdiError as _FtdiError
else:
    from pyftdi.ftdi import Ftdi as _Ftdi
    from pyftdi.ftdi import FtdiError as _FtdiError
from pyftdi.eeprom import FtdiEeprom as _FtdiEeprom
from replifactory.drivers.at24c256c import EepromDriver
from pyftdi.i2c import I2cPort, I2cController
from usb.core import (USBError, Device as UsbDevice)


I2C_FREQ = 5e4  # try 100e3
# I2C_FREQ = 100e3  # 100kHz
I2C_INTERFACE = 2
EEPROM_ADDRESS = 0x53


class Ftdi(_Ftdi):

    def __init__(self):
        _Ftdi.__init__(self)
        self._i2c_controller = I2cController()
        self._eeprom_driver = EepromDriver(I2cPort(
            controller=self._i2c_controller,
            address=EEPROM_ADDRESS,
        ))
        self._i2c_default_freq = I2C_FREQ
        self._i2c_interface = I2C_INTERFACE
        self._i2c_retry_count = 1

    def open_from_device(self, device: UsbDevice, interface: int = 2) -> None:
        super().open_from_device(device, interface)
        self._i2c_controller.set_retry_count(self._i2c_retry_count)
        self._i2c_controller.configure(
            self._usb_dev,
            frequency=self._i2c_default_freq,
            interface=self._i2c_interface,
        )

    def read_eeprom(self, addr: int = 0, length: int | None = None, eeprom_size: int | None = None) -> bytes:
        # return super().read_eeprom(addr, length, eeprom_size)
        eeprom_size = self._check_eeprom_size(eeprom_size)
        if length is None:
            length = eeprom_size
        if addr < 0 or (addr + length) > eeprom_size:
            raise ValueError('Invalid address/length')
        try:
            return self._eeprom_driver.read(addr, length)
        except USBError as exc:
            raise FtdiError('UsbError: %s' % exc) from exc

    def _write_eeprom_raw(self, addr: int, data: Union[bytes, bytearray],
                          dry_run: bool = True) -> None:
        if self.device_version == 0x0600:
            # FT232R internal EEPROM is unstable and latency timer seems
            # to have a direct impact on EEPROM programming...
            latency = self.get_latency_timer()
        else:
            latency = 0
        try:
            if latency:
                self.set_latency_timer(self.LATENCY_EEPROM_FT232R)
            length = len(data)
            if addr & 0x1 or length & 0x1:
                raise ValueError('Address/length not even')
            self._eeprom_driver.write(addr, data)
        finally:
            if latency:
                self.set_latency_timer(latency)


class FtdiError(_FtdiError):
    """Base class error for all FTDI device"""


class FtdiEepromError(FtdiError):
    """FTDI EEPROM access errors"""


class FtdiEeprom(_FtdiEeprom):
    def __init__(self):
        super().__init__()
        self._ftdi = Ftdi()
