from .transports import PipeTransport


class ProcessHandler(object):
    def __init__(self, reactor, proc, protocol_factory):
        self.proc = proc
        self.reactor = reactor
        self.protocol = protocol_factory(self)
        
        self.stdin = PipeTransport(self.reactor, self.proc.stdin, "w")
        self.reactor.register_write(self.stdin)
        
        self.stdout = PipeTransport(self.reactor, self.proc.stdout, "r")
        self.reactor.register_read(self.stdout)
        
        self.stderr = PipeTransport(self.reactor, self.proc.stderr, "r")
        self.reactor.register_read(self.stderr)
    
    def _poll(self):
        return self.proc.poll()
    
    def on_terminated(self):
        self.protocol.terminated(self.proc.returncode)

