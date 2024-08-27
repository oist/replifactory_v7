import logging
from collections import OrderedDict
from struct import calcsize as scalc
from typing import Union

from replifactory.drivers.at24c256c import EepromDriver


class Eeprom:
    VAR_STRINGS = ("manufacturer", "product", "serial")
    """EEPROM strings with variable length."""

    def __init__(self, eeprom_driver: EepromDriver):
        self.eeprom_driver = eeprom_driver
        self._eeprom = bytearray()
        self._size = EepromDriver.EEPROM_SIZE
        self._config = OrderedDict()
        self._dirty = set()
        self.log = logging.getLogger(__name__)

    def __getattr__(self, name):
        if name in self._config:
            return self._config[name]
        raise AttributeError("No such attribute: %s" % name)

    @property
    def size(self) -> int:
        return self._size

    @property
    def is_empty(self) -> bool:
        """Reports whether the EEPROM has been erased, or no EEPROM is
        connected to the FTDI EEPROM port.

        :return: True if no content is detected
        """
        if len(self._eeprom) != self.size:
            return False
        return all(byte == 255 for byte in self._eeprom)

    def connect(self):
        self._eeprom = self._read_eeprom()
        if self._valid:
            self._decode_eeprom()

    # @property
    # def device_version(self) -> int:
    #     """Report the version of the FTDI device.

    #        :return: the release
    #     """
    #     if not self._dev_ver:
    #         if not self._ftdi.is_connected:
    #             raise FtdiError('Not connected')
    #         self._dev_ver = self._ftdi.device_version
    #     return self._dev_ver

    def erase(self, erase_byte: int = 0xFF) -> None:
        """Erase the whole EEPROM.

        :param erase_byte: Optional erase byte to use. Default to 0xFF
        """
        self._eeprom = bytearray([erase_byte] * self.size)
        self._config.clear()
        self._dirty.add("eeprom")

    # def initialize(self) -> None:
    #     """Initialize the EEPROM with some default sensible values."""
    #     dev_ver = self.device_version
    #     dev_name = Ftdi.DEVICE_NAMES[dev_ver]
    #     vid = Ftdi.FTDI_VENDOR
    #     pid = Ftdi.PRODUCT_IDS[vid][dev_name]
    #     self.set_manufacturer_name("FTDI")
    #     self.set_product_name(dev_name.upper())
    #     sernum = "".join([chr(randint(ord("A"), ord("Z"))) for _ in range(5)])
    #     self.set_serial_number("FT%d%s" % (randint(0, 9), sernum))
    #     self.set_property("vendor_id", vid)
    #     self.set_property("product_id", pid)
    #     self.set_property("type", dev_ver)
    #     self.set_property("power_max", 150)
    #     self._sync_eeprom()

    # def _sync_eeprom(self, no_crc: bool = False):
    #     if not self._dirty:
    #         self.log.debug("No change detected for EEPROM content")
    #         return
    #     if not no_crc:
    #         if any([x in self._dirty for x in self.VAR_STRINGS]):
    #             self._generate_var_strings()
    #             for varstr in self.VAR_STRINGS:
    #                 self._dirty.discard(varstr)
    #         self._update_crc()
    #         self._decode_eeprom()
    #     self._dirty.clear()
    #     self._modified = True
    #     self.log.debug("EEPROM content regenerated (not yet committed)")

    def _read_eeprom(self) -> bytes:
        buf = self.eeprom_driver.read(0, EepromDriver.EEPROM_SIZE)
        eeprom = bytearray(buf)
        crc = self._compute_crc(eeprom, True)[0]
        if crc:
            if self.is_empty:
                self.log.info("No EEPROM or EEPROM erased")
            else:
                self.log.error("Invalid CRC or EEPROM content")
        return eeprom

    def _compute_crc(self, eeprom: Union[bytes, bytearray], check=False):
        mtp = self._ftdi.device_version == 0x1000
        crc_pos = 0x100 if mtp else len(eeprom)
        crc_size = scalc("<H")
        if not check:
            # check mode: add CRC itself, so that result should be zero
            crc_pos -= crc_size
        if self.is_mirroring_enabled:
            mirror_s1_crc_pos = self.mirror_sector
            if not check:
                mirror_s1_crc_pos -= crc_size
            # if mirroring, only calculate the crc for the first sector/half
            #   of the eeprom. Data (including this crc) are duplicated in
            #   the second sector/half
            crc = self._ftdi.calc_eeprom_checksum(eeprom[:mirror_s1_crc_pos])
        else:
            crc = self._ftdi.calc_eeprom_checksum(eeprom[:crc_pos])
        if check:
            self._valid = not bool(crc)
            if not self._valid:
                self.log.debug("CRC is now 0x%04x", crc)
            else:
                self.log.debug("CRC OK")
        return crc, crc_pos, crc_size
