from .tasks import TaskSubsystem
from .net import TcpSubsystem
from .processes import ProcSubsystem
from .files import FilesSubsystem


def get_subsystems():
    return [TaskSubsystem, TcpSubsystem, ProcSubsystem, FilesSubsystem]

