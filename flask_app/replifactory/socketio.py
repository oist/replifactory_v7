import logging
from typing import Optional, Dict
import flask

from flask_socketio import emit as socketio_emit
from flask_socketio.namespace import Namespace
from replifactory.usb_manager import UsbManager

from flask_app.replifactory.events import Events, eventManager
from flask_app.replifactory.machine import MachineCallback, MachineInterface

log = logging.getLogger(__name__)


class SocketIOSessionMachineCallback(MachineCallback):
    def __init__(self, app, sid, namespace: Optional[str] = None):
        self._app = app
        self._sid = sid
        self._namespace = namespace or "/"
        eventManager().subscribe(
            Events.MACHINE_STATE_CHANGED, self._on_machine_state_changed
        )
        eventManager().subscribe(
            Events.CONNECTION_OPTIONS_UPDATED, self._on_connection_options_updated
        )
        eventManager().subscribe(Events.MACHINE_CONNECTED, self._on_connected)
        eventManager().subscribe(
            Events.DEVICE_STATE_CHANGED, self._on_device_state_changed
        )

    def __del__(self):
        self.unsubscribe()

    def unsubscribe(self):
        eventManager().unsubscribe(
            Events.MACHINE_STATE_CHANGED, self._on_machine_state_changed
        )

    def _emit(self, event, *args, **kwargs):
        if "to" not in kwargs:
            kwargs["to"] = self._sid
        if "namespace" not in kwargs:
            kwargs["namespace"] = self._namespace
        with self._app.app_context():
            socketio_emit(event, *args, **kwargs)

    def _on_machine_state_changed(self, event, payload):
        self._emit(event, payload)

    def _on_connection_options_updated(self, event, payload):
        self._emit(
            Events.CONNECTION_OPTIONS_UPDATED,
            payload,
            namespace="/machine",
            broadcast=True,
        )

    def _on_connected(self, event, comm):
        usb_device = comm._usb_device
        payload = UsbManager.get_device_info(usb_device)
        self._emit(event, payload, namespace="/machine", broadcast=True)

    def _on_device_state_changed(self, event, payload):
        device, state = payload
        data = {
            device.id: {
                "stateId": device.get_state_id(state),
                "stateString": device.get_state_string(state),
            }
        }
        self._emit(event, data, namespace="/machine", broadcast=True)


class MachineNamespace(Namespace):
    def __init__(self, app, machine: MachineInterface, namespace: Optional[str] = None):
        super(Namespace, self).__init__(namespace)
        self._app = app
        self._machine = machine
        self._clients_callbacks: Dict[str, SocketIOSessionMachineCallback] = {}

    def on_connect(self):
        log.debug("socket.io client connecting")
        sid = flask.request.sid
        client_calback = SocketIOSessionMachineCallback(
            app=self._app, sid=sid, namespace=self.namespace
        )
        self._clients_callbacks[sid] = client_calback

        self._machine.register_callback(client_calback)

        payload = {
            "state_id": self._machine.get_state_id(),
            "state_string": self._machine.get_state_string(),
        }
        socketio_emit(Events.MACHINE_STATE_CHANGED, payload)
        eventManager().fire(Events.CLIENT_CONNECTED)

    def on_disconnect(self):
        log.debug("socket.io client disconnecting")
        sid = flask.request.sid
        client_calback = self._clients_callbacks.pop(sid, None)
        if client_calback:
            self._machine.unregister_callback(client_calback)
            client_calback.unsubscribe()
        eventManager().fire(Events.CLIENT_DISCONNECTED)
