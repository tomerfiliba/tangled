from .tasks import TaskSubsystem
from .sockets import TcpSubsystem
from .processes import ProcSubsystem


def get_subsystems():
    return [TaskSubsystem, TcpSubsystem, ProcSubsystem]

