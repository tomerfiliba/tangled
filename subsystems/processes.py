from ..reactors.base import Subsystem


class ProcSubsystem(Subsystem):
    NAME = "process"
    
    def spawn(self, cmdline, cwd = None, env = None, shell = False):
        pass
    
    def worker(self):
        pass






