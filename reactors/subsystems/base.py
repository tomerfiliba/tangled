class Subsystem(object):
    NAME = None
    def __init__(self, reactor):
        assert self.NAME, "must set a name"
        self._reactor = reactor
    def _init(self):
        pass

