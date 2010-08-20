from .base import ReactorBase
try:
    import win32file
except ImportError:
    win32file = None


class IOCP(object):
    def __init__(self):
        self._port = win32file.CreateIoCompletionPort(win32file.INVALID_FILE_HANDLE, None, 0, 0)
    def add_handle(self, handle):
        win32file.CreateIoCompletionPort(handle, self._port, int(port), 0)
    def post(self):
        win32file.PostQueuedCompletionStatus(self._port, numberOfbytes, completionKey, overlapped)
    def wait(self, timeout):
        rc, size, key, overlapped = win32file.GetQueuedCompletionStatus(self._port, int(timeout * 1000))
        if rc == 0:
            pass
        else:
            pass
        

#(rc, cBytesRecvd) = WSARecv(s, buffer, ol, dwFlags)
#s : PySocket/int
#    Socket to send data on.
#buffer: buffer
#    Buffer to send data from.
#ol : PyOVERLAPPED
#    An overlapped structure.
#dwFlags : int
#    Optional reception flags.
#
#(rc, cBytesSent) = WSASend(s, buffer , ol , dwFlags )
#s : PySocket /int
#    Socket to send data on.
#buffer : string/buffer
#    Buffer to send data from.
#ol : PyOVERLAPPED
#    An overlapped structure
#dwFlags : int
#    Optional send flags.

class WinSocket(object):
    def __init__(self):
        self._recv_buffer = []
    
    def enqueue_recv(self, size):
        overlapped = win32file.OVERLAPPED()
        buf = win32file.AllocateReadBuffer(size)
        rc, buf = win32file.WSARecv(self.handle, buf, overlapped, 0)
        self._recv_buffer.append(buf)
        overlapped.object = self

    def enqueue_send(self, size):
        overlapped = win32file.OVERLAPPED()
        buf = win32file.AllocateReadBuffer(size)
        rc, buf = win32file.WSASend(self.handle, buf, overlapped, 0)
        overlapped.object = self
    
    def recv(self, size):
        buf = self._recv_buffer.pop(0)
        return str(buf)

 


class IocpReactor(ReactorBase):
    def __init__(self, subsystems):
        ReactorBase.__init__(self, subsystems)
        self._port = IOCP()
    
    
    def _poll_transports(self, timeout):
        pass
    
    @classmethod
    def is_supported(cls):
        return False
        #if not win32file:
        #    return False
        #return hasattr(win32file, "CreateIOCompletionPort")




