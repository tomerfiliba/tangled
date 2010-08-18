import tangled


reactor = tangled.get_reactor()

class MyServer(tangled.StreamProtocol):
    def connected(self, peerinfo):
        self.peerinfo = peerinfo
        print "server says hello to", self.peerinfo
    def disconnected(self):
        print "server says goodbye to", self.peerinfo
        reactor.stop()
    def received(self, data):
        print "server got: %r" % (data,)
        self.send("foobar") 


def flow(func):
    def wrapper(*args, **kwargs):
        gen = func()
        gen.next()
    return wrapper


class InlineProtocol(tangled.StreamProtocol):
    def recv(self):
        pass
    
    def received(self, data):
        self._recvbuf.append(data)
    
    @flow
    def statemachine(trns):
        for i in range(10):
            yield trns.send("what is your name? (%d)" % (i))
            data = yield trns.recv()
        yield trns.close()







reactor.tcp.listen(MyServer, 12345)
reactor.tcp.connect(MyClient, "localhost", 12345)
reactor.start()
print "reactor finished"

