import select
from .base import ReactorBase


class KqueueReactor(ReactorBase):
    def _iterate(self, timeout):
        pass
    @classmethod
    def is_supported(cls):
        return False # hasattr(select, "kqueue")




