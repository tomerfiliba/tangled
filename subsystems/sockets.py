import socket
from ..reactors.base import Subsystem
from ..utils.transports import SocketListenerTransport, SocketStreamTransport


class TcpSubsystem(Subsystem):
    NAME = "tcp"
    
    def listen(self, protocol_factory, port, host = "0.0.0.0", backlog = 10):
        def callback(task):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((host, port))
            sock.listen(backlog)
            trns = SocketListenerTransport(self._reactor, sock, protocol_factory)
            self._reactor.register_transport(trns)
            trns.set_read(True)
        self._reactor.call(callback)
    
    def connect(self, protocol_factory, host, port):
        def callback(task):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            sock.setblocking(False)
            trns = SocketStreamTransport(self._reactor, sock, protocol_factory)
            self._reactor.register_transport(trns)
            trns.set_read(True)
            trns.protocol.connected()
        self._reactor.call(callback)




















