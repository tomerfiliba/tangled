import socket
from ..reactors.base import Subsystem
from ..utils.transports import SocketListenerTransport, SocketStreamTransport


class TcpSubsystem(Subsystem):
    NAME = "tcp"
    
    def listen(self, port, protocol_factory, host = "0.0.0.0", backlog = 10):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(backlog)
        trns = SocketListenerTransport(sock, protocol_factory)
        self._reactor.register_transport(trns)
        trns.set_read(True)
    
    def connect(self, host, port, protocol_factory):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.setblocking(False)
        trns = SocketStreamTransport(sock, protocol_factory)
        self._reactor.register_transport(trns)
        trns.set_read(True)
        trns.protocol.connected()




















