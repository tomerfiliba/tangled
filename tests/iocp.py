import win32file
import win32con
import socket
import itertools


class IOCP(object):
    def __init__(self):
        self._port = win32file.CreateIoCompletionPort(win32file.INVALID_HANDLE_VALUE, None, 0, 0)
        self._key = itertools.count()
    def __repr__(self):
        return "IOCP(%r)" % (self._port,)
    def add_handle(self, handle):
        if hasattr(handle, "fileno"):
            handle = handle.fileno()
        key = self._key.next()
        win32file.CreateIoCompletionPort(handle, self._port, key, 0)
        return key
    def post(self):
        win32file.PostQueuedCompletionStatus(self._port, numberOfbytes, completionKey, overlapped)
    def wait(self, timeout):
        res = win32file.GetQueuedCompletionStatus(self._port, int(timeout * 1000))
        return res


class WinSocket(object):
    def __init__(self, sock = None):
        if sock is None:
            sock = socket.socket()
        self.sock = sock
        self._recv_buffers = {}
        self._keep = {}
        self._buffers = []
    def fileno(self):
        return self.sock.fileno()
    
    def close(self):
        self.sock.close()
    def connect(self, ep):
        self.sock.connect(ep)
    def bind(self, ep):
        self.sock.bind(ep)
    def listen(self, backlog):
        self.sock.listen(backlog)
    def accept(self):
        return WinSocket(self.sock.accept()[0])
    
    def keep(self, obj):
        self._keep[id(obj)] = obj

    def send_done(self, rc, bytes, key, overlapped):
        print "SEND DONE", rc, bytes, key, overlapped 
    
    def enqueue_send(self, data):
        overlapped = win32file.OVERLAPPED()
        rc, _ = win32file.WSASend(self.fileno(), data, overlapped, 0)   
        overlapped.object = self.send_done
        self.keep(overlapped.object)
        self.keep(overlapped)

    def recv_done(self, rc, bytes, key, overlapped):
        print "RECV DONE", rc, bytes, key, overlapped
        print overlapped.dword, overlapped.hEvent
        buf = self._recv_buffers[overlapped]
        self._buffers.append(str(buf[:bytes]))

    def enqueue_recv(self, size):
        overlapped = win32file.OVERLAPPED()
        buf = win32file.AllocateReadBuffer(size)
        rc, _ = win32file.WSARecv(self.fileno(), buf, overlapped, 0)
        self._recv_buffers[overlapped] = buf
        overlapped.object = self.recv_done
        self.keep(overlapped.object)
        self.keep(overlapped)
    
    def send(self, data):
        self.enqueue_send(data)
    def recv(self, size):
        if not self._buffers:
            raise IOError("you must only call recv after the reactor indicated so")
        return self._buffers.pop(0)


class Reactor(object):
    def __init__(self):
        self.iocp = IOCP()
        self.active = False
    
    def add_handle(self, handle):
        self.iocp.add_handle(handle)
        
    def start(self):
        self.active = True
        for i in range(5):
        #while self.active:
            rc, size, key, overlapped = self.iocp.wait(1)
            if rc == win32con.WAIT_TIMEOUT:
                continue
            overlapped.object(rc, size, key, overlapped)
            
    def stop(self):
        self.active = False


if __name__ == "__main__":
    reactor = Reactor()
    listener = WinSocket()
    listener.bind(("localhost", 17777))
    listener.listen(1)
    s1 = WinSocket()
    s1.connect(("localhost", 17777))
    s2 = listener.accept()
    listener.close()

    reactor.add_handle(s1)
    reactor.add_handle(s2)
    
    s1.enqueue_send("hello")
    s1.enqueue_send("world")
    s2.enqueue_recv(100)
    reactor.start()




















