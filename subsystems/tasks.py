from ..reactors.base import Subsystem, TaskBase
from functools import partial


class ScheduledTask(TaskBase):
    def __init__(self, reactor, timestamp, callback):
        TaskBase.__init__(self, reactor, callback)
        self.timestamp = timestamp
    def invoke(self):
        TaskBase.invoke(self)
        self.cancel()
    def get_remaining(self):
        return self.timestamp - self.reactor.clock.get_time()

class RepeatingTask(TaskBase):
    def __init__(self, reactor, interval, callback):
        TaskBase.__init__(self, reactor, callback)
        self.starttime = self.reactor.clock.get_time()
        self.interval = interval
    def get_remaining(self):
        now = self.reactor.clock.get_time()
        next = self.starttime + (((now - self.starttime) // self.interval) + 1) * self.interval
        return next - now

class TaskSubsystem(Subsystem):
    NAME = "call"
    
    def at(self, timestamp, func):
        return self._reactor.add_task(ScheduledTask(self._reactor, timestamp, func))
    def within(self, seconds, func, *args, **kwargs):
        return self.at(self._reactor.clock.get_time() + seconds, func, *args, **kwargs)
    def now(self, func, *args, **kwargs):
        return self.within(0, func, *args, **kwargs)
    def repeating(self, interval, func, *args, **kwargs):
        return self._reactor.add_task(RepeatingTask(self._reactor, interval, func))




