import win32file
import win32con
import ctypes
import socket


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
    def __init__(self, sock):
        self.sock = sock
        self._handle = sock.fileno()
        self._overlapped_callbacks = {}
        self._handler = self._handler
    def close(self):
        self.sock.close()
    def fileno(self):
        return self._handle

    def _handler(self, overlapped):
        callback, args = self._overlapped_callbacks.pop(overlapped)
        callback(*args)
    
    def _get_overlapped(self, callback, *args):
        overlapped = win32file.OVERLAPPED()
        overlapped.object = self._handler
        self._overlapped_callbacks[overlapped] = (callback, args)
    
    def _connect_done(self, overlapped):
        print "_connect_done", overlapped
    
    def connect(self, endpoint):
        self._get_overlapped(self._connect_done)
        rc, _ = win32file.ConnectEx(self._handle, endpoint, Overlapped, None)

    def listen(self, backlog):
        self.sock.listen(backlog)

    def _accept_done(self):
        pass

    def accept(self, endpoint):
        sock2 = WinSock(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        buf = win32file.AllocateReadBuffer(CalculateSocketEndPointSize(sock2))
        # need to attach sock2 to iocp too
        overlapped = self._get_overlapped(self._accept_done, sock2, buf)
        rc, _ = win32file.AcceptEx(self._handle, sock2._handle, buf, overlapped)
































