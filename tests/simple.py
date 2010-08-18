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

class MyClient(tangled.StreamProtocol):
    def connected(self):
        self.count = 0
        self.send("what is your name? (%d)" % (self.count))
    def received(self, data):
        print "client got: %r" % (data,)
        if self.count < 10:
            self.count += 1
            self.send("what is your name? (%d)" % (self.count))
        else:
            self.close()


reactor.tcp.listen(MyServer, 12345)
reactor.tcp.connect(MyClient, "localhost", 12345)
reactor.start()
print "reactor finished"

