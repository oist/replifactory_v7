import logging
import os
from collections import OrderedDict
from threading import RLock
from typing import Any

import usb._interop as _interop
from usb.core import Device as UsbDevice
from usbmonitor import USBMonitor
from usbmonitor.__platform_specific_detectors._constants import _SECONDS_BETWEEN_CHECKS

from replifactory.drivers.ft2232h import FtdiDriver
from replifactory.events import Events, eventManager
from replifactory.virtual_usb_device import VirtualUsbDevice

logger = logging.getLogger(__name__)
_instance = None

REPLIFACTORY_VIRTUAL_MACHINE_ENABLED = os.environ.get(
    "REPLIFACTORY_VIRTUAL_MACHINE_ENABLED", "false"
).lower() in ("true", "1")

VIRTUAL_USB_DEVICE = VirtualUsbDevice()


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
        self._usb_devices = None
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
        logger.info("Stopping usb monitoring...")
        self._usb_monitor.monitor.stop_monitoring()

    @classmethod
    def get_device_id(cls, usb_device: UsbDevice):
        if usb_device:
            bus = usb_device.bus
            address = usb_device.address
            return f"/dev/bus/usb/{bus:03d}/{address:03d}"
        return None

    @classmethod
    def get_device_info(cls, usb_device: UsbDevice):
        device_data = {
            "id": cls.get_device_id(usb_device),
        }
        if usb_device:
            for prop in [
                "address",
                "bus",
                "idProduct",
                "idVendor",
                "manufacturer",
                "product",
                "serial_number",
            ]:
                device_data[prop] = getattr(usb_device, prop, None)
        return device_data

    def get_device(self, device_id):
        with self._lock:
            usb_devices = self._usb_devices
            if usb_devices is None:
                usb_devices = self.get_available_devices()
            return usb_devices[device_id]

    def find_device(self, **kwargs):
        with self._lock:
            usb_devices = self._usb_devices
            if usb_devices is None:
                usb_devices = self.get_available_devices()
            for _, device in usb_devices.items():
                tests = (
                    val == getattr(device, key, None) for key, val in kwargs.items()
                )
                if _interop._all(tests):
                    return device
            return None

    def get_available_devices(self):
        with self._lock:
            if self._usb_devices is None:
                usb_devices = OrderedDict()
                devices = FtdiDriver.list_devices()
                if REPLIFACTORY_VIRTUAL_MACHINE_ENABLED:
                    devices.append(VIRTUAL_USB_DEVICE)
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
        logger.info(f"Connected: {str(device_info)} [{device_id}]")
        bus, address = self._parse_devname(device_info["DEVNAME"])
        usb_device = FtdiDriver.find_device(bus=bus, address=address)
        if usb_device:
            with self._lock:
                self._usb_devices[device_id] = usb_device
                eventManager().fire(Events.USB_LIST_UPDATED, self._usb_devices)
        eventManager().fire(Events.USB_CONNECTED, usb_device)

    def _on_disconnect(self, device_id, device_info):
        logger.info(f"Disconnected: {str(device_info)} [{device_id}]")
        with self._lock:
            try:
                usb_device = self._usb_devices.pop(device_id)
                eventManager().fire(Events.USB_DISCONNECTED, usb_device)
                eventManager().fire(Events.USB_LIST_UPDATED, self._usb_devices)
            except KeyError:
                logger.warning(
                    "Can't disconnect device %s it's not in list: %s",
                    device_id,
                    self._usb_devices.keys(),
                )
