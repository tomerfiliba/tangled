from .base import Subsystem
from ..transports import PipeTransport
from subprocess import Popen, PIPE


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
    
    def on_started(self):
        pass
    
    def on_terminated(self):
        self.protocol.terminated(self.proc.returncode)


class ProcSubsystem(Subsystem):
    NAME = "processes"
    
    def spawn(self, protocol_factory, cmdline, cwd = None, env = None, shell = False):
        def callback():
            proc = Popen(cmdline, stdin = PIPE, stdout = PIPE, stderr = PIPE, cwd = cwd, env = env, shell = shell)
            handler = ProcessHandler(self._reactor, proc, protocol_factory)
            self._reactor.register_process(handler)
            self._reactor.call(handler.on_started)
        self._reactor.call(callback)
    
    def worker(self):
        pass




