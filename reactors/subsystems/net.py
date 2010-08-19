import socket
from .base import Subsystem
from ..transports import SocketListenerTransport, SocketStreamTransport
from tangled.utils import Deferred


class TcpSubsystem(Subsystem):
    NAME = "tcp"
    
    def listen(self, protocol_factory, port, host = "0.0.0.0", backlog = 10):
        dfr = Deferred()
        def callback():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            sock.listen(backlog)
            trns = SocketListenerTransport(self._reactor, sock, protocol_factory)
            self._reactor.register_read(trns)
            dfr.set(trns)
        self._reactor.call(callback)
        return dfr
    
    def connect(self, protocol_factory, host, port):
        dfr = Deferred()
        def callback():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            sock.setblocking(False)
            trns = SocketStreamTransport(self._reactor, sock, protocol_factory)
            self._reactor.register_read(trns)
            trns.protocol.connected()
            dfr.set(trns)
        self._reactor.call(callback)
        return dfr



