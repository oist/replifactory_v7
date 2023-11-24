import logging
import threading
import time
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
        self._logger = logging.getLogger(__name__)

        self._app = app
        self._sid = sid
        self._namespace = namespace or "/"

        self._throttle_factor = 1
        self._last_current = 0
        self._base_rate_limit = 0.5

        self._held_back_current = None
        self._held_back_mutex = threading.RLock()

        self._initial_data_sent = False

        eventManager().subscribe(
            Events.CONNECTION_OPTIONS_UPDATED, self._on_connection_options_updated
        )
        eventManager().subscribe(Events.MACHINE_CONNECTED, self._on_connected)

    def __del__(self):
        self.unsubscribe()

    def unsubscribe(self):
        eventManager().unsubscribe(
            Events.CONNECTION_OPTIONS_UPDATED, self._on_connection_options_updated
        )
        eventManager().unsubscribe(Events.MACHINE_CONNECTED, self._on_connected)

    def _emit(self, event, *args, **kwargs):
        if "to" not in kwargs:
            kwargs["to"] = self._sid
        if "namespace" not in kwargs:
            kwargs["namespace"] = self._namespace
        with self._app.app_context():
            try:
                socketio_emit(event, *args, **kwargs)
            except Exception as e:
                if self._logger.isEnabledFor(logging.DEBUG):
                    self._logger.exception(
                        f"Could not send message to client {self._sid}"
                    )
                else:
                    self._logger.warning(
                        "Could not send message to client %s: %s", self._sid, e
                    )

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

    def on_machine_send_initial_data(self, data):
        self._initial_data_sent = True
        data_to_send = dict(data)
        data_to_send["serverTime"] = time.time()
        self._emit("history", data_to_send)

    def on_machine_send_current_data(self, data):
        if not self._initial_data_sent:
            self._logger.debug("Initial data not yet send, dropping current message")
            return

        # make sure we rate limit the updates according to our throttle factor
        with self._held_back_mutex:
            if self._held_back_current is not None:
                self._held_back_current.cancel()
                self._held_back_current = None

            now = time.time()
            delta = (
                self._last_current + self._base_rate_limit * self._throttle_factor - now
            )
            if delta > 0:
                self._held_back_current = threading.Timer(
                    delta, lambda: self.on_machine_send_current_data(data)
                )
                self._held_back_current.start()
                return

        self._last_current = now

        data.update(
            {
                "serverTime": time.time(),
            }
        )
        self._emit("current", data)


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
        self._machine.send_initial_callback(client_calback)

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
