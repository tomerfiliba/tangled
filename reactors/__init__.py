from .selecting import SelectingReactor
from .epoll import EpollReactor
from .kqueue import KqueueReactor
from .iocp import IocpReactor
from .subsystems import get_subsystems


def get_reactor_for_platform():
    for cls in [EpollReactor, KqueueReactor, IocpReactor, SelectingReactor]:
        if cls.is_supported():
            return cls
    raise ReactorError("no reactor supported on this platform")


the_reactor = None

def get_reactor():
    global the_reactor
    if the_reactor is None:
        cls = get_reactor_for_platform()
        the_reactor = cls(get_subsystems())
    return the_reactor


