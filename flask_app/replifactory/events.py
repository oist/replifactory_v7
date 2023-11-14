
# singleton
import collections
import logging
import queue
import re
import threading


_instance = None


def all_events():
    return [
        getattr(Events, name)
        for name in Events.__dict__
        if not name.startswith("_") and name not in ("register_event",)
    ]


class Events:
    # server
    STARTUP = "Startup"
    SHUTDOWN = "Shutdown"
    CONNECTIVITY_CHANGED = "ConnectivityChanged"

    # USB
    USB_CONNECTED = "UsbConnected"
    USB_DISCONNECTED = "UsbDisconnected"
    USB_LIST_UPDATED = "UsbListUpdated"

    # Client
    CLIENT_CONNECTED = "ClientConnected"
    CLIENT_DISCONNECTED = "ClientDisconnected"

    # connect/disconnect to printer
    CONNECTING = "Connecting"
    CONNECTED = "Connected"
    DISCONNECTING = "Disconnecting"
    DISCONNECTED = "Disconnected"
    CONNECTIONS_AUTOREFRESHED = "ConnectionsAutorefreshed"
    CONNECTION_OPTIONS_UPDATED = "ConnectionOptionsUpdated"

    # State changes
    MACHINE_STATE_CHANGED = "MachineStateChanged"
    MACHINE_RESET = "MachineReset"

    # experiment job
    EXPERIMENT_STARTED = "PrintStarted"
    EXPERIMENT_DONE = "PrintDone"
    EXPERIMENT_FAILED = "PrintFailed"
    EXPERIMENT_CANCELLING = "PrintCancelling"
    EXPERIMENT_CANCELLED = "PrintCancelled"
    EXPERIMENT_PAUSED = "PrintPaused"
    EXPERIMENT_RESUMED = "PrintResumed"
    ERROR = "Error"
    CHART_MARKED = "ChartMarked"

    # commands events
    POWER_ON = "PowerOn"
    POWER_OFF = "PowerOff"
    HOME = "Home"
    WAITING = "Waiting"
    ALERT = "Alert"

    DILUTE = "Dilute"
    DILUTING = "Diluting"
    DILUTED = "Diluted"
    FEED = "Feed"
    FEEDING = "Feeding"
    FED = "Fed"
    FLUSH = "Flush"
    FLUSHING = "Flushing"
    FLUSHED = "Flushed"
    VALVE_OPEN = "ValveOpen"
    VALVE_OPENING = "ValveOpengin"
    VALVE_OPENED = "ValveOpened"
    VALVE_CLOSE = "ValveClose"
    VALVE_CLOSING = "ValveClosing"
    VALVE_CLOSED = "ValveClosed"
    STIRING_STARTED = "StiringStart"
    STIRING_SPEED_CHANGED = "Striring"
    STIRING_STOPED = "StiringEnd"
    OPTICAL_DENSITY_MEASURE = "OpticalDensityMeasure"
    OPTICAL_DENSITY_MEASURED = "OpticalDensityMeasured"
    LASER_TURN_ON = "LaserTurnOn"
    LASER_TURNED_ON = "LaserTurnedOn"
    LASER_TURN_OFF = "LaserTurnOff"
    LASER_TURNED_OFF = "LaserTurnedOff"
    PHOTODIODE_READ = "PhotodiodeRead"
    PHOTODIODE_READED = "PhotodiodeReaded"
    THERMOMETER_READ = "ThermometerRead"
    THERMOMETER_READED = "ThermometerReaded"

    # Settings
    SETTINGS_UPDATED = "SettingsUpdated"

    @classmethod
    def register_event(cls, event, prefix=None):
        name = cls._to_identifier(event)
        if prefix:
            event = prefix + event
            name = cls._to_identifier(prefix) + name
        setattr(cls, name, event)
        return name, event

    # based on https://stackoverflow.com/a/1176023
    _first_cap_re = re.compile("([^_])([A-Z][a-z]+)")
    _all_cap_re = re.compile("([a-z0-9])([A-Z])")

    @classmethod
    def _to_identifier(cls, name):
        s1 = cls._first_cap_re.sub(r"\1_\2", name)
        return cls._all_cap_re.sub(r"\1_\2", s1).upper()


def eventManager():
    global _instance
    if _instance is None:
        _instance = EventManager()
    return _instance


class EventManager:
    """
    Handles receiving events and dispatching them to subscribers
    """

    def __init__(self):
        self._registeredListeners = collections.defaultdict(list)
        self._logger = logging.getLogger(__name__)
        self._logger_fire = logging.getLogger(f"{__name__}.fire")

        self._startup_signaled = False
        self._shutdown_signaled = False

        self._queue = queue.Queue()
        self._held_back = queue.Queue()

        self._worker = threading.Thread(target=self._work)
        self._worker.daemon = True
        self._worker.start()

    def _work(self):
        try:
            while not self._shutdown_signaled:
                event, payload = self._queue.get(True)
                if event == Events.SHUTDOWN:
                    # we've got the shutdown event here, stop event loop processing after this has been processed
                    self._logger.info(
                        "Processing shutdown event, this will be our last event"
                    )
                    self._shutdown_signaled = True

                eventListeners = self._registeredListeners[event]
                self._logger_fire.debug(f"Firing event: {event} (Payload: {payload!r})")

                for listener in eventListeners:
                    self._logger.debug(f"Sending action to {listener!r}")
                    try:
                        listener(event, payload)
                    except Exception:
                        self._logger.exception(
                            "Got an exception while sending event {} (Payload: {!r}) to {}".format(
                                event, payload, listener
                            )
                        )
            self._logger.info("Event loop shut down")
        except Exception:
            self._logger.exception("Ooops, the event bus worker loop crashed")

    def fire(self, event, payload=None):
        """
        Fire an event to anyone subscribed to it

        Any object can generate an event and any object can subscribe to the event's name as a string (arbitrary, but
        case sensitive) and any extra payload data that may pertain to the event.

        Callbacks must implement the signature "callback(event, payload)", with "event" being the event's name and
        payload being a payload object specific to the event.
        """

        send_held_back = False
        if event == Events.STARTUP:
            self._logger.info("Processing startup event, this is our first event")
            self._startup_signaled = True
            send_held_back = True

        self._enqueue(event, payload)

        if send_held_back:
            self._logger.info(
                "Adding {} events to queue that "
                "were held back before startup event".format(self._held_back.qsize())
            )
            while True:
                try:
                    self._queue.put(self._held_back.get(block=False))
                except queue.Empty:
                    break

    def _enqueue(self, event, payload):
        if self._startup_signaled:
            q = self._queue
        else:
            q = self._held_back

        q.put((event, payload))

    def subscribe(self, event, callback):
        """
        Subscribe a listener to an event -- pass in the event name (as a string) and the callback object
        """

        if callback in self._registeredListeners[event]:
            # callback is already subscribed to the event
            return

        self._registeredListeners[event].append(callback)
        self._logger.debug(f"Subscribed listener {callback!r} for event {event}")

    def unsubscribe(self, event, callback):
        """
        Unsubscribe a listener from an event -- pass in the event name (as string) and the callback object
        """

        try:
            self._registeredListeners[event].remove(callback)
        except ValueError:
            # not registered
            pass

    def join(self, timeout=None):
        self._worker.join(timeout)
        return self._worker.is_alive()


class GenericEventListener:
    """
    The GenericEventListener can be subclassed to easily create custom event listeners.
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def subscribe(self, events):
        """
        Subscribes the eventCallback method for all events in the given list.
        """

        for event in events:
            eventManager().subscribe(event, self.eventCallback)

    def unsubscribe(self, events):
        """
        Unsubscribes the eventCallback method for all events in the given list
        """

        for event in events:
            eventManager().unsubscribe(event, self.eventCallback)

    def eventCallback(self, event, payload):
        """
        Actual event callback called with name of event and optional payload. Not implemented here, override in
        child classes.
        """
        pass


class DebugEventListener(GenericEventListener):
    def __init__(self):
        GenericEventListener.__init__(self)

        events = list(filter(lambda x: not x.startswith("__"), dir(Events)))
        self.subscribe(events)

    def eventCallback(self, event, payload):
        GenericEventListener.eventCallback(self, event, payload)
        self._logger.debug(f"Received event: {event} (Payload: {payload!r})")
