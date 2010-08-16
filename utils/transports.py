from ..reactors.base import TransportBase


class StreamTransport(TransportBase):
    READ_SIZE = 16000
    WRITE_SIZE = 16000
    
    def __init__(self, reactor, fileobj, protocol_factory, write_size = None, read_size = None):
        TransportBase.__init__(self, reactor)
        self.fileobj = fileobj
        self.protocol = protocol_factory(self)
        self._wbuffer = ""
        self._read_size = self.READ_SIZE if read_size is None else read_size
        self._write_size = self.WRITE_SIZE if write_size is None else write_size
    def fileno(self):
        return self.fileobj.fileno()
    def close(self):
        self.deactivate()
        self.fileobj.close()

    def write(self, data):
        self._wbuffer += data
        if self._wbuffer:
            self.set_write(True)
    
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
            self.set_write(False)

class SocketStreamTransport(StreamTransport):
    def close(self):
        self.shutdown("rw")
        StreamTransport.close(self)

    def shutdown(self, mode):
        if mode == "r":
            self.fileobj.shutdown(socket.SHUT_RD)
        elif mode == "r":
            self.fileobj.shutdown(socket.SHUT_WR)
        elif mode == "rw":
            self.fileobj.shutdown(socket.SHUT_RDWR)
        else:
            raise ValueError("invalid shutdown mode: %r" % (mode,))

    def on_read(self, count_hint):
        data = self.fileobj.recv(self._read_size)
        if not data:
            self.protocol.disconnected()
        else:
            self.protocol.received(data)
    
    def on_write(self, count_hint):
        count = self.fileobj.send(self._wbuffer[:self._write_size])
        self._wbuffer = self._wbuffer[count:]
        if not self._wbuffer:
            self.set_write(False)

class SocketListenerTransport(TransportBase):
    def __init__(self, reactor, sock, protocol_factory):
        TransportBase.__init__(self, reactor)
        self.sock = sock
        self.protocol_factory = protocol_factory
    def fileno(self):
        return self.sock.fileno()
    def close(self):
        self.deactivate()
        self.fileobj.close()

    def on_read(self, count_hint):
        sock2, _ = self.sock.accept()
        trns = StreamTransport(sock2, self.protocol_factory)
        self.reactor.register_transport(trns)
        trns.set_read(True)
        trns.protocol.connected()

class PipeTransport(StreamTransport):
    DONT_FLUSH = 0
    FLUSH_NOW = 1
    FLUSH_ALWAYS = 2
    
    def __init__(self, reactor, fileobj, protocol_factory, mode, flushing = FLUSH_ALWAYS, 
            write_size = None, read_size = None):
        if mode not in ["r", "w", "rw"]:
            raise ValueError("invalid open mode: %r" % (mode,))
        StreamTransport.__init__(self, reactor, fileobj, protocol_factory, write_size, read_size)
        self.mode = mode
        self.flushing = flushing
    
    def write(self, data):
        if "w" not in self.mode:
            raise IOError("transport does not allow writing")
        StreamTransport.write(data)
    
    def on_write(self, count_hint):
        StreamTransport.on_write(self, count_hint)
        if self.flushing == self.FLUSH_ALWAYS:
            self.flush()
        elif self.flushing == self.FLUSH_NOW:
            self.flush()
            self.flushing = self.DONT_FLUSH

    def isatty(self):
        return self.fileobj.isatty()

class FileTransport(PipeTransport):
    def seek(self, offset, whence = 0):
        self.fileobj.seek(offset, whence)
    def tell(self):
        return self.fileobj.tell()




















