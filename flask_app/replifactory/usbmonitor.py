import logging
from typing import Any

from usbmonitor import USBMonitor
from usbmonitor.__platform_specific_detectors._constants import _SECONDS_BETWEEN_CHECKS
from usbmonitor.attributes import ID_MODEL, ID_MODEL_ID, ID_VENDOR_ID

from replifactory.events import Events, eventManager

log = logging.getLogger(__name__)


class UsbMonitor(USBMonitor):
    def __init__(
        self,
        app,
        filter_devices: list[dict[str, str]] | tuple[dict[str, str]] | None = None,
    ):
        usb_monitor = super().__init__(
            filter_devices
            or (
                {
                    "ID_MODEL_ID": "6010",
                    "ID_VENDOR_ID": "0403",
                },
            )
        )
        if not hasattr(app, "extensions"):
            app.extensions = {}  # pragma: no cover
        app.extensions["usb_monitor"] = usb_monitor

        eventManager().subscribe(Events.CLIENT_CONNECTED, self._update_available_devices)
        eventManager().subscribe(Events.USB_CONNECTED, self._update_available_devices)
        eventManager().subscribe(Events.USB_DISCONNECTED, self._update_available_devices)

    def _update_available_devices(self, event, payload):
        self.get_available_devices()

    def get_available_devices(self):
        available_devices = super().get_available_devices()
        eventManager().fire(Events.USB_LIST_UPDATED, available_devices)
        return available_devices

    def device_info_str(self, device_info):
        return f"{device_info[ID_MODEL]} ({device_info[ID_MODEL_ID]} - {device_info[ID_VENDOR_ID]})"

    def on_connect(self, device_id, device_info):
        log.info(
            f"Connected: {self.device_info_str(device_info=device_info)} [{device_id}]"
        )
        eventManager().fire(Events.USB_CONNECTED, (device_id, device_info))

    def on_disconnect(self, device_id, device_info):
        log.info(
            f"Disconnected: {self.device_info_str(device_info=device_info)} [{device_id}]"
        )
        eventManager().fire(Events.USB_DISCONNECTED, (device_id, device_info))

    def start_monitoring(
        self,
        on_connect: Any | None = None,
        on_disconnect: Any | None = None,
        check_every_seconds: int | float = _SECONDS_BETWEEN_CHECKS,
    ) -> None:
        return super().start_monitoring(
            on_connect or self.on_connect,
            on_disconnect or self.on_disconnect,
            check_every_seconds,
        )
