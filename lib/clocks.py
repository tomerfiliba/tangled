import time
from .common import singleton


@singleton
class WallClock(object):
    __slots__ = []
    def get_time(self):
        return time.time()


class SimulatedClock(object):
    def __init__(self, inittime = None):
        self.time = time.time() if inittime is None else inittime
    def get_time(self):
        return self.time
    def set_time(self, newtime):
        self.time = newtime
    def advance(self, delta):
        self.time += delta


