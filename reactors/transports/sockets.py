import socket
from .base import TransportBase, StreamTransport


def _shutdown_helper(self, mode):
    if mode == "r":
        self.fileobj.shutdown(socket.SHUT_RD)
    elif mode == "r":
        self.fileobj.shutdown(socket.SHUT_WR)
    elif mode == "rw":
        self.fileobj.shutdown(socket.SHUT_RDWR)
    else:
        raise ValueError("invalid shutdown mode: %r" % (mode,))


class SocketStreamTransport(StreamTransport):
    def __init__(self, reactor, fileobj, protocol_factory, write_size = None, read_size = None):
        StreamTransport.__init__(self, reactor, fileobj, protocol_factory, write_size, read_size)
        self.localinfo = fileobj.getsockname()
        self.peerinfo = fileobj.getpeername()

    def close(self):
        if not self.fileobj:
            return
        self.shutdown("rw")
        StreamTransport.close(self)
    
    shutdown = _shutdown_helper

    def on_read(self, count_hint):
        try:
            data = self.fileobj.recv(self._read_size)
        except socket.error:
            return
        if not data:
            self.protocol.disconnected()
            self.close()
        else:
            self.protocol.data_received(data)
    
    def on_write(self, count_hint):
        count = self.fileobj.send(self._wbuffer[:self._write_size])
        self._wbuffer = self._wbuffer[count:]
        if not self._wbuffer:
            self.reactor.unregister_write(self)


class SocketListenerTransport(TransportBase):
    def __init__(self, reactor, sock, protocol_factory):
        TransportBase.__init__(self, reactor)
        self.protocol_factory = protocol_factory
        self.fileobj = sock
        self._fileno = sock.fileno()
        self.localinfo = sock.getsockname()
    
    @property
    def host(self):
        return self.localinfo[0]
    @property
    def port(self):
        return self.localinfo[1]

    def close(self):
        if not self.fileobj:
            return
        self.shutdown("rw")
        self.deactivate()
        self.fileobj.close()
        self.fileobj = None
    
    shutdown = _shutdown_helper
    
    def fileno(self):
        return self._fileno

    def on_read(self, count_hint):
        sock2, _ = self.fileobj.accept()
        trns2 = SocketStreamTransport(self.reactor, sock2, self.protocol_factory)
        self.reactor.register_read(trns2)
        trns2.protocol.connected()




