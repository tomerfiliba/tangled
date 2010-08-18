from .base import StreamTransport


class PipeTransport(StreamTransport):
    DONT_FLUSH = 0
    FLUSH_NOW = 1
    FLUSH_ALWAYS = 2
    
    def __init__(self, reactor, fileobj, protocol_factory, mode, flushing = FLUSH_ALWAYS, 
            write_size = None, read_size = None):
        if mode not in ["r", "w", "rw"]:
            raise ValueError("invalid open mode: %r" % (mode,))
        StreamTransport.__init__(self, reactor, fileobj, protocol_factory, write_size, read_size)
        self.mode = mode
        self.flushing = flushing
    
    def write(self, data):
        if "w" not in self.mode:
            raise IOError("transport does not allow writing")
        StreamTransport.write(data)
    
    def on_write(self, count_hint):
        StreamTransport.on_write(self, count_hint)
        if self.flushing == self.FLUSH_ALWAYS:
            self.flush()
        elif self.flushing == self.FLUSH_NOW:
            self.flush()
            self.flushing = self.DONT_FLUSH

    def isatty(self):
        return self.fileobj.isatty()

class FileTransport(PipeTransport):
    def seek(self, offset, whence = 0):
        self.fileobj.seek(offset, whence)
    def tell(self):
        return self.fileobj.tell()

