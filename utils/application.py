from .deferred import Deferred, monadic


class Application(object):
    def __init__(self):
        self.reactor = None
    
    def main(self):
        yield
    
    def start(self):
        from ..reactors import get_reactor
        self.reactor = get_reactor()
        mmain = monadic(self.main)
        self.reactor.call(mmain)
        self.reactor.start()



