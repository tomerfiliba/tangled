import socket
from .base import Subsystem
from ..transports import SocketListenerTransport, SocketStreamTransport


class TcpSubsystem(Subsystem):
    NAME = "tcp"
    
    def listen(self, protocol_factory, port, host = "0.0.0.0", backlog = 10):
        def callback():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((host, port))
            sock.listen(backlog)
            trns = SocketListenerTransport(self._reactor, sock, protocol_factory)
            self._reactor.register_read(trns)
        self._reactor.call(callback)
    
    def connect(self, protocol_factory, host, port):
        def callback():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            sock.setblocking(False)
            trns = SocketStreamTransport(self._reactor, sock, protocol_factory)
            self._reactor.register_read(trns)
            trns.protocol.connected()
        self._reactor.call(callback)



