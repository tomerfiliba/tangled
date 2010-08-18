import time
from .common import singleton


def clock():
    return time.time()

class SimulatedClock(object):
    def __init__(self, inittime = None):
        self.time = time.time() if inittime is None else inittime
    def __call__(self):
        return self.time
    def set(self, newtime):
        self.time = newtime
    def advance(self, delta):
        self.time += delta

