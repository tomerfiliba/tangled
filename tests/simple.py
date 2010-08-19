import tangled
from functools import partial


class MyServer(tangled.StreamProtocol):
    def connected(self):
        print "server says hello to", self.transport.peerinfo
    def disconnected(self):
        print "server says goodbye to", self.transport.peerinfo
    def data_received(self, data):
        print "server got: %r" % (data,)
        self.send("foobar") 

class MyClient(tangled.StreamProtocol):
    def connected(self):
        self.count = 0
        self.send("what is your name? (%d)" % (self.count))
    
    def data_received(self, data):
        print "client got: %r" % (data,)
        self.count += 1
        if self.count < 10:
            self.send("what is your name? (%d)" % (self.count))
        else:
            self.close()


class App(tangled.utils.Application):
    def main(self):
        trns = yield self.reactor.tcp.listen(MyServer, 0)
        self.reactor.tcp.connect(MyClient, trns.host, trns.port)
        self.reactor.schedule.within(3, self.reactor.tcp.connect, MyClient, trns.host, trns.port)
        self.reactor.schedule.within(5, self.reactor.stop)


if __name__ == "__main__":
    App().start()



