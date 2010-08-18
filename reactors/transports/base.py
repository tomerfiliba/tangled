import socket
import os


class TransportBase(object):
    def __init__(self, reactor):
        self.reactor = reactor
    def deactivate(self):
        self.reactor.unregister_read(self)
        self.reactor.unregister_write(self)
    
    def fileno(self):
        raise NotImplementedError()

    def on_error(self, info):
        pass
    def on_read(self, count_hint):
        pass
    def on_write(self, count_hint):
        pass

class AutoResetEvent(TransportBase):
    __slots__ = ["_rfd", "_wfd", "_is_set"]
    def __init__(self):
        self._is_set = False
        self._rfd, self._wfd = os.pipe()
    def __del__(self):
        self.close()
    def close(self):
        os.close(self._rfd)
        os.close(self._wfd)
    def fileno(self):
        return self._rfd
    def set(self):
        if self._is_set:
            return
        self._is_set = True
        os.write(self._wfd, "X")
    def reset(self):
        if not self._is_set:
            return
        os.read(self._rfd, 10)
        self._is_set = False
    def on_read(self, count_hint):
        self.reset()

class StreamTransport(TransportBase):
    READ_SIZE = 16000
    WRITE_SIZE = 16000
    
    def __init__(self, reactor, fileobj, protocol_factory, write_size = None, read_size = None):
        TransportBase.__init__(self, reactor)
        self.fileobj = fileobj
        self.protocol = protocol_factory(self)
        self._fileno = fileobj.fileno()
        self._wbuffer = ""
        self._read_size = self.READ_SIZE if read_size is None else read_size
        self._write_size = self.WRITE_SIZE if write_size is None else write_size
    def fileno(self):
        return self._fileno
    def close(self):
        self.deactivate()
        self.fileobj.close()

    def write(self, data):
        self._wbuffer += data
        if self._wbuffer:
            self.reactor.register_write(self)
    
    def on_read(self, count_hint):
        data = self.fileobj.read(self._read_size)
        if not data:
            self.protocol.disconnected()
        else:
            self.protocol.received(data)
    
    def on_write(self, count_hint):
        self.fileobj.write(self._wbuffer[:self._write_size])
        self._wbuffer = self._wbuffer[self._write_size:]
        if not self._wbuffer:
            self.reactor.unregister_write(self)










