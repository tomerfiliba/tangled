class ProtocolBase(object):
    def __init__(self, transport):
        self.transport = transport
        self.reactor = self.transport.reactor


class StreamProtocol(ProtocolBase):
    def send(self, data):
        self.transport.write(data)
    def close(self):
        self.transport.close()

    # events
    def error(self):
        pass
    def connected(self, info):
        pass
    def disconnected(self):
        pass
    def received(self, data):
        pass


class ProcessProtocol(ProtocolBase):
    def write(self, data):
        self.transport.stdin.write(data)
    def signal(self, sig):
        self.transport.proc.send_signal(sig)
    def terminate(self):
        self.transport.proc.terminate(sig)
    
    # events
    def started(self):
        pass
    def terminated(self, exitcode):
        pass
    
    def stdout_received(self, data):
        pass
    def stdout_closed(self):
        pass
    def stderr_received(self, data):
        pass
    def stderr_closed(self):
        pass



