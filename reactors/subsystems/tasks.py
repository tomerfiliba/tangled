from tangled.lib import clock
from .base import Subsystem
from functools import partial


class TaskBase(object):
    def __init__(self, reactor, callback):
        self.reactor = reactor
        self._callback = callback
        self._active = True
    def cancel(self):
        self._active = False
    def invoke(self):
        raise NotImplementedError()
    def get_remaining_time(self, now):
        raise NotImplementedError()

class SingleTask(TaskBase):
    def __init__(self, reactor, timestamp, callback):
        TaskBase.__init__(self, reactor, callback)
        self.timestamp = timestamp
    
    def invoke(self):
        if not self._active:
            return
        self._callback()
        self.cancel()
    
    def get_remaining_time(self, now):
        return self.timestamp - now

class RepeatingTask(TaskBase):
    def __init__(self, reactor, interval, callback):
        TaskBase.__init__(self, reactor, callback)
        self.starttime = clock()
        self.interval = interval
    
    def invoke(self):
        if self._active:
            self._callback(self)
        if self._active:
            self.reactor.register_task(self)

    def get_remaining_time(self, now):
        next = self.starttime + (((now - self.starttime) // self.interval) + 1) * self.interval
        return next - now


class TaskSubsystem(Subsystem):
    NAME = "schedule"
    
    def at(self, timestamp, func, *args, **kwargs):
        return self._reactor.register_task(SingleTask(self._reactor, timestamp, partial(func, *args, **kwargs)))
    
    def within(self, seconds, func, *args, **kwargs):
        return self.at(clock() + seconds, func, *args, **kwargs)
    
    def repeating(self, interval, func):
        return self._reactor.register_task(RepeatingTask(self._reactor, interval, func))

    #def repeating2(self, interval, func, *args, **kwargs):
    #    return self._reactor.register_task(RepeatingTask(self._reactor, interval, lambda task: func(*args, **kwargs)))


