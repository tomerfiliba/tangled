import select
from .base import ReactorBase
try:
    import win32file
except ImportError:
    win32file = None


class IocpReactor(ReactorBase):
    def _iterate(self, timeout):
        pass
    @classmethod
    def is_supported(cls):
        if not win32file:
            return False
        return hasattr(win32file, "CreateIOCompletionPort")




