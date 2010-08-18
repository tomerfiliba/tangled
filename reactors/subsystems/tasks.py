from tangled.lib import clock
from .base import Subsystem


class TaskBase(object):
    def __init__(self, reactor, callback):
        self.reactor = reactor
        self._callback = callback
        self._active = True
    def cancel(self):
        self._active = False
    def invoke(self):
        if self._active:
            self._callback(self)
        if self._active:
            self.reactor.add_task(self)
    def get_remaining_time(self, now):
        raise NotImplementedError()

class ScheduledTask(TaskBase):
    def __init__(self, reactor, timestamp, callback):
        TaskBase.__init__(self, reactor, callback)
        self.timestamp = timestamp
    def get_remaining_time(self, now):
        return self.timestamp - now

class RepeatingTask(TaskBase):
    def __init__(self, reactor, interval, callback):
        TaskBase.__init__(self, reactor, callback)
        self.starttime = clock()
        self.interval = interval
    def get_remaining_time(self, now):
        next = self.starttime + (((now - self.starttime) // self.interval) + 1) * self.interval
        return next - now


class TaskSubsystem(Subsystem):
    NAME = "schedule"
    
    def at(self, timestamp, func):
        return self._reactor.add_task(ScheduledTask(self._reactor, timestamp, func))
    def within(self, seconds, func, *args, **kwargs):
        return self.at(clock() + seconds, func, *args, **kwargs)
    def repeating(self, interval, func, *args, **kwargs):
        return self._reactor.add_task(RepeatingTask(self._reactor, interval, func))




