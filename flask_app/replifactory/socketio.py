import logging

from flask_socketio import Namespace, emit
from replifactory.events import Events, eventManager

log = logging.getLogger(__name__)


class MachineEventListener:

    def __init__(self, app):
        self._app = app
        if not hasattr(app, "extensions"):
            app.extensions = {}  # pragma: no cover
        app.extensions["machine_event_listener"] = self
        eventManager().subscribe(Events.USB_LIST_UPDATED, self.on_usb_list_updated)

    def on_usb_list_updated(self, event, payload):
        with self._app.app_context():
            emit(Events.USB_LIST_UPDATED, payload, namespace="/machine", broadcast=True)


class MachineNamespace(Namespace):
    def on_connect(self):
        log.debug("socket.io client connected")
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
