import os
import fcntl
from ..reactors.base import Subsystem
from ..utils.transports import FileTransport


class FilesSubsystem(Subsystem):
    NAME = "files"
    
    MODE_MAPPING = {"r" : "r", "w" : "w", "r+" : "rw", "w+" : "rw", "a" : "w"}
    
    def open(self, filename, mode = "r"):
        f = open(filename, mode)
        fcntl.fcntl(f.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
        mode2 = self.MODE_MAPPING[mode]
        trns = FileTransport(self._reactor, f, mode2)
        if "r" in mode2:
            trns.set_read(True)
        self._reactor.register_transport(trns)


    






