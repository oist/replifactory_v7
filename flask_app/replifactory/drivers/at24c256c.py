import logging
import threading
from collections import OrderedDict
from typing import Optional

from flask_app.replifactory.drivers import EepromDriver, HardwarePort


class AT24C256C_Driver(EepromDriver):
    EEPROM_SIZE = 32768
    PAGE_SIZE = 64
    TOTAL_PAGE = EEPROM_SIZE // PAGE_SIZE + (1 if EEPROM_SIZE % PAGE_SIZE > 0 else 0)

    def __init__(self, port: HardwarePort):
        super().__init__(port=port)
        self.lock = threading.RLock()
        self._eeprom = bytearray()
        self._size = AT24C256C_Driver.EEPROM_SIZE
        self._config = OrderedDict()
        self._dirty = set()
        self.log = logging.getLogger(__name__)

    def write(self, address: int, data: bytes | bytearray):
        if self._is_write_overflow(address, data):
            raise OverflowError(
                f"Trying to write {len(data)} bytes to EEPROM with volume {AT24C256C_Driver.EEPROM_SIZE} bytes."
            )
        start_page = address // AT24C256C_Driver.PAGE_SIZE
        page_count = len(data) // AT24C256C_Driver.PAGE_SIZE + 1
        first_page_offset = address % AT24C256C_Driver.PAGE_SIZE
        next_address = address
        next_data_start = 0
        next_data_length = AT24C256C_Driver.PAGE_SIZE - first_page_offset
        for page_num in range(start_page, start_page + page_count):
            address_words = self._split_address_words(next_address)
            next_data = data[next_data_start:next_data_length]
            # self.log.debug(
            #     __(
            #         "W i2c: {port_name} (0x{port_addr:02X}) address: 0x{regaddr:02X} page: {page_num} of {total_pages} data: [{data}]",
            #         port_name=self.port._name
            #         if hasattr(self.port, "_name")
            #         else "Unknown",
            #         port_addr=self.port._address,
            #         regaddr=next_address,
            #         data=bytearray(next_data).hex(" ").upper(),
            #         page_num=page_num,
            #         total_pages=page_count,
            #     )
            # )
            self.port.write(address_words + next_data)
            next_address = (page_num + 1) * AT24C256C_Driver.PAGE_SIZE
            next_data_start = next_data_length
            next_data_length += AT24C256C_Driver.PAGE_SIZE

    def read(self, address: Optional[int] = None, readlen: Optional[int] = None):
        if address is None and readlen is None:
            result = self.port.read(1)  # Current Address Read
        else:
            address = address or 0
            readlen = readlen or AT24C256C_Driver.EEPROM_SIZE - address  # bytes til end
            address_words = self._split_address_words(address)

            result = self.port.exchange(address_words, readlen)
            # self.port.write(address_words, relax=False)
            # result = self.port.read(readlen)
        # self.log.debug(
        #     __(
        #         "R i2c: {port_name} (0x{port_addr:02X}) address: 0x{regaddr:02X} len: {readlen} data: [{data}]",
        #         port_name=self.port._name if hasattr(self.port, "_name") else "Unknown",
        #         port_addr=self.port._address,
        #         regaddr=address,
        #         readlen=readlen,
        #         data=result.hex(" ").upper(),
        #     )
        # )
        return result

    def _is_write_overflow(self, address: int, data: bytes | bytearray):
        return AT24C256C_Driver.EEPROM_SIZE - address < len(data)

    def _split_address_words(self, address: int):
        first_word_address = (address >> 8) & 0x7F
        second_word_address = address & 0xFF
        return bytearray([first_word_address, second_word_address])
