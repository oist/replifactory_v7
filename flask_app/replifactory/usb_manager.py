import logging
from collections import OrderedDict
from threading import RLock
from typing import Any

import usb._interop as _interop
from usbmonitor import USBMonitor
from usbmonitor.__platform_specific_detectors._constants import _SECONDS_BETWEEN_CHECKS

from replifactory.drivers.ft2232h import FtdiDriver
from replifactory.events import Events, eventManager

logger = logging.getLogger(__name__)
_instance = None


def usbManager():
    global _instance
    if _instance is None:
        _instance = UsbManager()
    return _instance


class UsbManager:
    def __init__(
        self,
        filter_devices: list[dict[str, str]] | tuple[dict[str, str]] | None = None,
    ):
        self._lock = RLock()
        self._usb_devices = {}
        self._usb_monitor = USBMonitor(
            filter_devices
            or (
                {
                    "ID_MODEL_ID": "6010",
                    "ID_VENDOR_ID": "0403",
                },
            )
        )

    def start_monitoring(
        self,
        on_connect: Any | None = None,
        on_disconnect: Any | None = None,
        check_every_seconds: int | float = _SECONDS_BETWEEN_CHECKS,
    ) -> None:
        self.get_available_devices()
        return self._usb_monitor.start_monitoring(
            on_connect or self._on_connect,
            on_disconnect or self._on_disconnect,
            check_every_seconds,
        )

    def stop_monitoring(self):
        self._usb_monitor.monitor.stop_monitoring()

    def get_device(self, device_id):
        with self._lock:
            return self._usb_devices[device_id]

    def find_device(self, **kwargs):
        with self._lock:
            for device in self._usb_devices:
                tests = (val == getattr(device, key, None) for key, val in kwargs.items())
                if _interop._all(tests):
                    return device
            return None

    def get_available_devices(self):
        with self._lock:
            if not self._usb_devices:
                usb_devices = OrderedDict()
                devices = FtdiDriver.list_devices()
                for device in devices:
                    device_id = f"/dev/bus/usb/{device.bus:03}/{device.address:03}"
                    usb_devices[device_id] = device
                self._usb_devices = usb_devices
                eventManager().fire(Events.USB_LIST_UPDATED, self._usb_devices)
            return self._usb_devices

    def _parse_devname(self, devname: str):
        bus_str, address_str = devname.split("/")[-2:]
        bus = int(bus_str)
        address = int(address_str)
        return (bus, address)

    def _on_connect(self, device_id, device_info):
        logger.info(
            f"Connected: {str(device_info)} [{device_id}]"
        )
        bus, address = self._parse_devname(device_info["DEVNAME"])
        usb_device = FtdiDriver.find_device(bus=bus, address=address)
        with self._lock:
            self._usb_devices[device_id] = usb_device
        eventManager().fire(Events.USB_CONNECTED, usb_device)
        eventManager().fire(Events.USB_LIST_UPDATED, self._usb_devices)

    def _on_disconnect(self, device_id, device_info):
        logger.info(
            f"Disconnected: {str(device_info)} [{device_id}]"
        )
        with self._lock:
            usb_device = self._usb_devices.pop(device_id)
        eventManager().fire(Events.USB_DISCONNECTED, usb_device)
        eventManager().fire(Events.USB_LIST_UPDATED, self._usb_devices)
