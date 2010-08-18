import os
import fcntl
from .base import Subsystem
from ..transports import FileTransport


class FilesSubsystem(Subsystem):
    NAME = "files"
    
    MODE_MAPPING = {"r" : "r", "w" : "w", "r+" : "rw", "w+" : "rw", "a" : "w"}
    
    def open(self, filename, mode = "r"):
        f = open(filename, mode)
        fcntl.fcntl(f.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
        mode2 = self.MODE_MAPPING[mode]
        trns = FileTransport(self._reactor, f, mode2)
        if "r" in mode2:
            self._reactor.register_read(trns)


    






