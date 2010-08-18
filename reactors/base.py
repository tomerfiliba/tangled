import os
import signal
from threading import Lock
from tangled.lib import clock
from .transports import AutoResetEvent


HAS_SIGCHLD = hasattr(signal, "SIGCHLD")


class ReactorBase(object):
    IDLE = 1
    RUNNING = 2
    STOPPED = 3
    ERROR = 4
    MAX_POLL_TIMEOUT = 0.3


    def __init__(self, subsystems):
        self._state = self.IDLE
        self._lock = Lock()
        self._read_transports = set()
        self._write_transports = set()
        self._changed_transports = set()
        self._processes = set()
        self._tasks = []
        self._callbacks = []
        self._signal_handlers = {}
        self._event = AutoResetEvent()
        self.register_read(self._event)
        
        if HAS_SIGCHLD:
            self._check_processes = False
            def sigchld_handler(sig):
                self._check_processes = True
            self.register_signal(signal.SIGCHLD, sigchld_handler)
        
        self._subsystems = {}
        for cls in subsystems:
            inst = cls(self)
            if cls.NAME in self._subsystems:
                raise ReactorError("subsystem %s already exists" % (inst.NAME,))
            self._subsystems[cls.NAME] = inst
            setattr(self, cls.NAME, inst)
        for cls in subsystems:
            self._subsystems[cls.NAME]._init()

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

    def _work(self):
        try:
            while self._state == self.RUNNING:
                timeout = self._get_poll_timeout()
                self._poll_transports(min(timeout, self.MAX_POLL_TIMEOUT))
                self._changed_transports.clear()
                self._handle_processes()
                self._handle_tasks()
                self._handle_callbacks()
        except Exception, ex:
            self._state = self.ERROR
            raise

    def _get_poll_timeout(self):
        now = clock()
        if self._tasks:
            soonest = min(task.get_remaining_time(now) for task in self._tasks)
        else:
            soonest = self.MAX_POLL_TIMEOUT
        return max(soonest, 0)
    
    def _poll_transports(self, timeout):
        raise NotImplementedError()

    def _prune_bad_fds(self):
        for transports in [self._read_transports, self._write_transports]:
            bad = set()
            for trns in transports:
                try:
                    os.fstat(trns.fileno())
                except OSError, ex:
                    bad.add(trns)
                    self.call(trns.on_error, ex)
            transports -= bad
    
    def _handle_processes(self):
        if HAS_SIGCHLD:
            if self._check_processes:
                self._check_processes = False
            else:
                return
        for proc in self._processes:
            rc = proc.poll()
            if rc is not None:
                self.call(proc.on_terminated, rc)
                self.call(self._processes.remove, proc)
    
    def _handle_tasks(self):
        new_tasks = []
        now = clock()
        for task in self._tasks:
            if task.get_remaining_time(now) <= 0:
                self.call(task.invoke)
            else:
                new_tasks.append(task)
        self._tasks = new_tasks
    
    def _handle_callbacks(self):
        for func, args, kwargs in self._callbacks:
            func(*args, **kwargs)
        del self._callbacks[:]
    
    #
    # transports
    #
    def register_read(self, transport):
        self._read_transports.add(transport)
        self._changed_transports.add(transport)

    def unregister_read(self, transport):
        self._read_transports.discard(transport)
        self._changed_transports.add(transport)
    
    def register_write(self, transport):
        self._write_transports.add(transport)
        self._changed_transports.add(transport)
    
    def unregister_write(self, transport):
        self._write_transports.discard(transport)
        self._changed_transports.add(transport)
    
    #
    # processes
    #
    def register_process(self, proc):
        self._processes.add(proc)

    #
    # signals
    #
    def _generic_signal_handler(self, sig, frame):
        for handler in self._signal_handlers[sig]:
            if HAS_SIGCHLD and sig == signal.SIGCHLD:
                handler(sig)
            else:
                self.call(handler, sig)
        self._event.set()

    def register_signal(self, sig, func):
        signal.signal(sig, self._generic_signal_handler)
        if sig not in self._signal_handlers:
            self._signal_handlers[sig] = []
        self._signal_handlers[sig].append(func)

    def unregister_signal(self, sig, func):
        self._signal_handlers[sig].remove(func)
        if not self._signal_handlers[sig]:
            del self._signal_handlers[sig]
            signal.signal(sig, signal.SIG_DFL)

    #
    # tasks
    #
    def call(self, func, *args, **kwargs):
        self._callbacks.append((func, args, kwargs))

    def register_task(self, task):
        self._tasks.append(task)



