from .base import StreamProtocol
from struct import Struct


class MessageProtocol(StreamProtocol):
    HEADER = Struct("!I")
    
    # compression? max size?
    
    def connected(self):
        self._buffer = ""
        self._length = None
    
    def disconnected(self):
        self._process()
    
    def _process(self):
        while True:
            if self._length is None:
                if len(self._buffer) >= self.HEADER.size:
                    self._length, = self.HEADER.unpack(self._buffer[:HEADER.size])
                    self._buffer = self._buffer[HEADER.size:]
                else:
                    break
            elif len(self._buffer) >= self._length:
                message = self._buffer[:self._length]
                self._buffer = self._buffer[self._length:]
                self._length = None
                self.message_received(message)
            else:
                break
    
    def data_received(self, data):
        self._buffer += data
        self._process()
    
    def message_received(self, data):
        pass
    

class Sequential(MessageProtocol):
    def connected(self):
        MessageProtocol.connected(self)
        self.state = self.statemachine()
        self.state.next()
    
    def message_received(self, data):
        self.state.send(data)
    
    def final_message_received(self, data):
        pass



























