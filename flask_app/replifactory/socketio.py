import logging

from flask_socketio import Namespace, emit
from replifactory.events import Events, eventManager
from replifactory.machine import MachineInterface

log = logging.getLogger(__name__)


class MachineEventListener:

    def __init__(self, app):
        self._app = app
        if not hasattr(app, "extensions"):
            app.extensions = {}  # pragma: no cover
        app.extensions["machine_event_listener"] = self
        eventManager().subscribe(Events.USB_LIST_UPDATED, self.on_usb_list_updated)
        eventManager().subscribe(Events.MACHINE_STATE_CHANGED, self.on_machine_state_changed)

    def on_usb_list_updated(self, event, payload):
        with self._app.app_context():
            emit(Events.USB_LIST_UPDATED, payload, namespace="/machine", broadcast=True)

    def on_machine_state_changed(self, event, payload):
        with self._app.app_context():
            emit(event, payload, namespace="/machine", broadcast=True)


class MachineNamespace(Namespace):

    def __init__(self, machine: MachineInterface,  namespace=None):
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

    def on_join(self, data):
        # Join a room specified by the client
        room = data.get("room")
        if room:
            # join_room(room)
            print(f"Joined room {room}")
