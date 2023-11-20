import logging

from flask_socketio import emit
from flask_socketio.namespace import Namespace
from replifactory.usb_manager import UsbManager

from flask_app.replifactory.events import Events, eventManager
from flask_app.replifactory.machine import MachineInterface

log = logging.getLogger(__name__)


class MachineEventListener:
    def __init__(self, app):
        self._app = app
        if not hasattr(app, "extensions"):
            app.extensions = {}  # pragma: no cover
        app.extensions["machine_event_listener"] = self
        eventManager().subscribe(Events.CONNECTION_OPTIONS_UPDATED, self._on_connection_options_updated)
        eventManager().subscribe(
            Events.MACHINE_STATE_CHANGED, self._on_machine_state_changed
        )
        eventManager().subscribe(Events.MACHINE_CONNECTED, self._on_connected)

    def _on_connection_options_updated(self, event, payload):
        with self._app.app_context():
            emit(Events.CONNECTION_OPTIONS_UPDATED, payload, namespace="/machine", broadcast=True)

    def _on_machine_state_changed(self, event, payload):
        with self._app.app_context():
            emit(event, payload, namespace="/machine", broadcast=True)

    def _on_connected(self, event, comm):
        usb_device = comm._usb_device
        payload = UsbManager.get_device_info(usb_device)
        with self._app.app_context():
            emit(event, payload, namespace="/machine", broadcast=True)


class MachineNamespace(Namespace):
    def __init__(self, machine: MachineInterface, namespace=None):
        super(Namespace, self).__init__(namespace)
        self._machine = machine

    def on_connect(self):
        log.debug("socket.io client connected")
        payload = {
            "state_id": self._machine.get_state_id(),
            "state_string": self._machine.get_state_string(),
        }
        emit(Events.MACHINE_STATE_CHANGED, payload)
        eventManager().fire(Events.CLIENT_CONNECTED)

    def on_disconnect(self):
        log.debug("socket.io client disconnected")
        eventManager().fire(Events.CLIENT_DISCONNECTED)
