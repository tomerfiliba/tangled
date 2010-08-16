import os
from threading import Lock



class Subsystem(object):
    NAME = None
    def __init__(self, reactor):
        self._reactor = reactor
    def _init(self):
        pass


class TaskBase(object):
    def __init__(self, reactor, callback):
        self.reactor = reactor
        self.callback = callback
        self.active = True
    def cancel(self):
        self.active = False
    def invoke(self):
        if self.active:
            self.callback(self)
    def get_remaining(self):
        return 0


class TransportBase(object):
    def __init__(self, reactor):
        self._active = True
        self._want_read = False
        self._want_write = False
        self.reactor = reactor
    def set_read(self, value):
        self._want_read = value
    def set_write(self, value):
        self._want_write = value
    def deactivate(self):
        self._active = False
    def fileno(self):
        raise NotImplementedError()
    
    def on_error(self, info):
        pass
    def on_read(self, count_hint):
        pass
    def on_write(self, count_hint):
        pass


class ProcessHandler(object):
    def __init__(self, reactor, proc, protocol_factory):
        self.proc = proc
        self.reactor = reactor
        self.protocol = protocol_factory(self)
        
        self.stdin = PipeTransport(self.reactor, self.proc.stdin, "w")
        self.reactor.register_transport(self.stdin)
        
        self.stdout = PipeTransport(self.reactor, self.proc.stdout, "r")
        self.stdout.set_read(True)
        self.reactor.register_transport(self.stdout)
        
        self.stderr = PipeTransport(self.reactor, self.proc.stderr, "r")
        self.stderr.set_read(True)
        self.reactor.register_transport(self.stderr)
    
    def on_terminated(self):
        self.protocol.terminated(self.proc.returncode)


class ReactorBase(object):
    IDLE = 1
    RUNNING = 2
    STOPPED = 3

    READ_EVENT = 1
    WRITE_EVENT = 2
    
    def __init__(self, clock, subsystems):
        self.clock = clock
        self._state = self.IDLE
        self._lock = Lock()
        self._subsystems = {}
        for cls in subsystems:
            inst = cls(self)
            if cls.NAME in self._subsystems:
                raise ReactorError("subsystem %s already exists" % (inst.NAME,))
            self._subsystems[cls.NAME] = inst
            setattr(self, cls.NAME, inst)
        for cls in subsystems:
            self._subsystems[cls.NAME]._init()
        self._transports = set()
        self._processes = set()
        self._tasks = set()

    @classmethod
    def is_supported(cls):
        raise NotImplementedError()
    
    def start(self):
        with self._lock:
            if self._state != self.IDLE:
                raise ReactorError("cannot start, reactor not idle")
            self._state = self.RUNNING
        self._work()
        with self._lock:
            assert self._state == self.STOPPED
            self._state = self.IDLE
    
    def stop(self):
        with self._lock:
            if self._state != self.RUNNING:
                raise ReactorError("cannot start, reactor not running")
            self._state = self.STOPPED
    
    MAX_TIMEOUT = 0.5
    
    def _work(self):
        while self._state == self.RUNNING:
            if self._tasks:
                soonest = min(task.get_remaining() for task in self._tasks)
            else:
                soonest = self.MAX_TIMEOUT
            self._poll(min(max(soonest, 0), self.MAX_TIMEOUT))
            new_tasks = set()
            for task in self._tasks:
                if task.get_remaining() <= 0:
                    task.invoke()
                if task.active:
                    new_tasks.add(task)
            self._tasks = new_tasks
    
    def _sigchld_handler(self, sig, frame):
        pid, rc = os.waitpid(-1, os.WNOHANG)
        self._terminated_processes.append(pid)
    
    def _generic_signal_handler(self, sig, frame):
        self._signals.append(sig)
    
    def _poll(self, timeout):
        raise NotImplementedError()
    
    def register_transport(self, transport):
        self._transports.add(transport)
    def register_task(self, task):
        self._tasks.add(task)
    def register_process(self, proc):
        self._processes.add(proc)
    def register_signal_handler(self, sig, func):
        signal.signal(sig, self._generic_signal_handler)
        self._signal_handlers[sig]









