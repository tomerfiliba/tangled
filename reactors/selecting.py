from .base import ReactorBase


class SelectingReactor(ReactorBase):
    def _iterate(self, timeout):
        pass
    @classmethod
    def is_supported(cls):
        return hasattr(select, "select")




