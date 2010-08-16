import select
from .base import ReactorBase


class EpollReactor(ReactorBase):
    def _iterate(self, timeout):
        pass
    @classmethod
    def is_supported(cls):
        return False # hasattr(select, "epoll")




