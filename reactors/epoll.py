import select
from .base import ReactorBase


class EpollReactor(ReactorBase):
    def __init__(self, subsystems):
        ReactorBase.__init__(self, subsystems)
        self._epoll = select.epoll()
        self._registered_with_epoll = {}
    
    def _update_epoll(self):
        for trns in self._changed_transports:
            flags = 0
            if trns in self._read_transports:
                flags |= select.EPOLLIN
            if trns in self._write_transports:
                flags |= select.EPOLLOUT
            fd = trns.fileno()
            if flags == 0:
                if fd in self._registered_with_epoll:
                    self._epoll.unregister(fd)
                    del self._registered_with_epoll[fd]
            elif fd in self._registered_with_epoll:
                self._epoll.modify(fd, flags)
            else:
                self._epoll.register(fd, flags)
                self._registered_with_epoll[fd] = trns
    
    def _poll_transports(self, timeout):
        self._update_epoll()
        events = self._epoll.poll(timeout)
        
        for fd, flags in events:
            trns = self._registered_with_epoll[fd]
            if flags & select.EPOLLIN:
                self.call(trns.on_read, -1)
            if flags & select.EPOLLOUT:
                self.call(trns.on_write, -1)
            if flags & select.EPOLLERR:
                self.call(trns.on_error, None)

    @classmethod
    def is_supported(cls):
        return hasattr(select, "epoll")




