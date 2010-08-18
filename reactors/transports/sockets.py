import socket
from .base import TransportBase, StreamTransport


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
        try:
            data = self.fileobj.recv(self._read_size)
        except socket.error:
            return
        if not data:
            self.protocol.disconnected()
        else:
            self.protocol.received(data)
    
    def on_write(self, count_hint):
        count = self.fileobj.send(self._wbuffer[:self._write_size])
        self._wbuffer = self._wbuffer[count:]
        if not self._wbuffer:
            self.reactor.unregister_write(self)

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
        trns2 = SocketStreamTransport(self.reactor, sock2, self.protocol_factory)
        self.reactor.register_read(trns2)
        trns2.protocol.connected()
