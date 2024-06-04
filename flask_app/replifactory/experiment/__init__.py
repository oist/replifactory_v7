

from datetime import datetime
from threading import Thread
import threading
import time

from flask_app.replifactory.events import Events, eventManager


class Experiment:

    def __init__(self):
        self._thread = None
        self._abort = False
        self._startTime = None
        self._cycles = 0
        self._cycleTime = 60.0
        self._warmupEnabled = True
        self._lock = threading.RLock()

    def start(self):
        with self._lock:
            if self._thread is not None:
                raise Exception("Experiment is already running")
            self._startTime = datetime.now()
            self._thread = Thread(target=self.run, args=({},), daemon=True)
            eventManager().fire(Events.EXPERIMENT_STARTED, payload={"time": self._startTime})
            self._thread.start()

    def restore(self, cycle_num: int):
        """Run main cycle without warming up"""
        with self._lock:
            if self._thread is not None:
                raise Exception("Experiment is already running")
            self._cycles = cycle_num
            self._warmupEnabled = False
            self._thread = Thread(target=self.run, args=({},), daemon=True)
            eventManager().fire(Events.EXPERIMENT_RESTORED, payload={"time": datetime.now()})
            self._thread.start()

    def stop(self):
        with self._lock:
            if self._thread is not None:
                self._abort = True
                eventManager().fire(Events.EXPERIMENT_CANCELLING, payload={"time": datetime.now()})
                self._thread.join()
                self._thread = None
                eventManager().fire(Events.EXPERIMENT_CANCELLED, payload={"time": datetime.now()})

    def run(self, *args, **kwargs):
        if self._warmupEnabled:
            self.warmup()
        while self._abort is False:
            start_cycle_time = datetime.now()
            self._cycles += 1
            eventManager().fire(Events.EXPERIMENT_NEW_CYCLE, payload={"time": start_cycle_time, "cycle": self._cycles})
            self.routine()
            error_happend, error_message = self.error_condition()
            if error_happend:
                eventManager().fire(Events.EXPERIMENT_FAILED, payload={"time": datetime.now(), "message": error_message})
                break
            if self.success_condition():
                break
            end_cycle_time = datetime.now()
            elapsed_time = end_cycle_time - start_cycle_time
            sleep_time = self._cycleTime - elapsed_time.total_seconds()
            if sleep_time < 0:
                eventManager().fire(Events.EXPERIMENT_CYCLE_TOO_LONG_WARNING, payload={"time": end_cycle_time, "cycle": self._cycles, "elapsed_time": elapsed_time})
            else:
                time.sleep(sleep_time)
            eventManager().fire(Events.EXPERIMENT_CYCLE_COMPLETE, payload={"time": datetime.now(), "cycle": self._cycles})

        self.cooldown()
        eventManager().fire(Events.EXPERIMENT_DONE, payload={"time": datetime.now()})
        self._thread = None

    def routine(self):
        pass

    def success_condition(self):
        return self._cycles > 10

    def error_condition(self):
        return (False, 'No errors')

    def warmup(self):
        pass

    def cooldown(self):
        pass

    def compatible(self, reactor):
        """Check if the experiment is compatible with the given reactor"""
        return True
