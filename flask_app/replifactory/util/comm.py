import contextlib
import logging
import queue
import threading
from flask_app.replifactory.events import Events, eventManager

from flask_app.replifactory.util import PrependableQueue, TypeAlreadyInQueue, TypedQueue

_logger = logging.getLogger(__name__)


class QueueMarker:
    def __init__(self, callback):
        self.callback = callback

    def run(self):
        if callable(self.callback):
            try:
                self.callback()
            except Exception:
                _logger.exception("Error while running callback of QueueMarker")


class AwaitConditionQueueMarker(QueueMarker):
    def __init__(
        self,
        callback,
        condition,
        cancel=None,
        interval=0.5,
        timeout_callback=None,
        timeout=None,
        *args,
        **kwargs,
    ):
        super().__init__(callback)
        self.timeout = timeout
        self.interval = interval
        self.condition_callback = condition
        self.cancel_callback = cancel
        self.timeout_callback = timeout_callback

    def done(self):
        if callable(self.condition_callback):
            try:
                return self.condition_callback()
            except Exception:
                _logger.exception(
                    "Error while checking condition of AwaitConditionQueueMarker"
                )

    def cancel(self):
        if callable(self.cancel_callback):
            try:
                return self.cancel_callback()
            except Exception:
                _logger.exception("Error while canceling AwaitConditionQueueMarker")

    def on_timeout(self):
        if callable(self.timeout_callback):
            try:
                return self.timeout_callback()
            except Exception:
                _logger.exception(
                    "Error while running timeout callback of AwaitConditionQueueMarker"
                )


class SendQueueMarker(QueueMarker):
    pass


class CommandQueue(TypedQueue):
    def __init__(self, *args, **kwargs):
        TypedQueue.__init__(self, *args, **kwargs)
        self._unblocked = threading.Event()
        self._unblocked.set()

    def block(self):
        self._unblocked.clear()

    def unblock(self):
        self._unblocked.set()

    @contextlib.contextmanager
    def blocked(self):
        self.block()
        try:
            yield
        finally:
            self.unblock()

    def get(self, *args, **kwargs):
        self._unblocked.wait()
        result = TypedQueue.get(self, *args, **kwargs)
        self._queue_changed()
        return result

    def put(self, *args, **kwargs):
        self._unblocked.wait()
        result = TypedQueue.put(self, *args, **kwargs)
        self._queue_changed()
        return result

    def clear(self):
        cleared = []
        while True:
            try:
                cleared.append(TypedQueue.get(self, False))
                TypedQueue.task_done(self)
            except queue.Empty:
                break
        self._queue_changed()
        return cleared

    def _queue_changed(self):
        eventManager().fire(
            Events.COMMAND_QUEUE_UPDATED, {"size": self.qsize()}
        )


class SendQueue(PrependableQueue):
    def __init__(self, maxsize=0):
        PrependableQueue.__init__(self, maxsize=maxsize)

        self._unblocked = threading.Event()
        self._unblocked.set()

        self._resend_queue = PrependableQueue()
        self._send_queue = PrependableQueue()
        self._lookup = set()

        self._resend_active = False

    @property
    def resend_active(self):
        return self._resend_active

    @resend_active.setter
    def resend_active(self, resend_active):
        with self.mutex:
            self._resend_active = resend_active

    def block(self):
        self._unblocked.clear()

    def unblock(self):
        self._unblocked.set()

    @contextlib.contextmanager
    def blocked(self):
        self.block()
        try:
            yield
        finally:
            self.unblock()

    def prepend(self, item, item_type=None, target=None, block=True, timeout=None):
        self._unblocked.wait()
        PrependableQueue.prepend(
            self, (item, item_type, target), block=block, timeout=timeout
        )
        self._queue_changed()

    def put(self, item, item_type=None, target=None, block=True, timeout=None):
        self._unblocked.wait()
        PrependableQueue.put(
            self, (item, item_type, target), block=block, timeout=timeout
        )
        self._queue_changed()

    def get(self, block=True, timeout=None):
        self._unblocked.wait()
        item, _, _ = PrependableQueue.get(self, block=block, timeout=timeout)
        self._queue_changed()
        return item

    def clear(self):
        cleared = []
        while True:
            try:
                cleared.append(PrependableQueue.get(self, False))
                PrependableQueue.task_done(self)
            except queue.Empty:
                break
        self._queue_changed()
        return cleared

    def _queue_changed(self):
        eventManager().fire(
            Events.SEND_QUEUE_UPDATED, {"size": self._qsize()}
        )

    def _put(self, item):
        _, item_type, target = item
        if item_type is not None:
            if item_type in self._lookup:
                raise TypeAlreadyInQueue(
                    item_type, f"Type {item_type} is already in queue"
                )
            else:
                self._lookup.add(item_type)

        if target == "resend":
            self._resend_queue.put(item)
        else:
            self._send_queue.put(item)

        pass

    def _prepend(self, item):
        _, item_type, target = item
        if item_type is not None:
            if item_type in self._lookup:
                raise TypeAlreadyInQueue(
                    item_type, f"Type {item_type} is already in queue"
                )
            else:
                self._lookup.add(item_type)

        if target == "resend":
            self._resend_queue.prepend(item)
        else:
            self._send_queue.prepend(item)

    def _get(self):
        if self.resend_active:
            item = self._resend_queue.get(block=False)
        else:
            try:
                item = self._resend_queue.get(block=False)
            except queue.Empty:
                item = self._send_queue.get(block=False)

        _, item_type, _ = item
        if item_type is not None:
            if item_type in self._lookup:
                self._lookup.remove(item_type)

        return item

    def _qsize(self):
        if self.resend_active:
            return self._resend_queue.qsize()
        else:
            return self._resend_queue.qsize() + self._send_queue.qsize()
