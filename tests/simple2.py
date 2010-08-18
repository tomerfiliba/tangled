import tangled
from functools import partial


class MyServer(tangled.StreamProtocol):
    def connected(self):
        self.peerinfo = self.transport.get_remote_endpoint()
        print "server says hello to", self.peerinfo
    def disconnected(self):
        print "server says goodbye to", self.peerinfo
    def received(self, data):
        print "server got: %r" % (data,)
        self.send("foobar") 

class MyClient(tangled.StreamProtocol):
    def connected(self):
        self.count = 0
        self.send("what is your name? (%d)" % (self.count))
    
    def statemachine(self):
        for i in range(10):
            self.send("what is your name? (%d)" % (self.count))
            reply = self.recv()
        self.close()
        yield


reactor = tangled.get_reactor()
reactor.tcp.listen(MyServer, 12345)
reactor.tcp.connect(MyClient, "localhost", 12345)
reactor.schedule.within(5, reactor.tcp.connect, MyClient, "localhost", 12345)
reactor.schedule.within(10, reactor.stop)

reactor.start()
print "reactor finished"



