import time
import select
import socket # needed for windows
from .base import ReactorBase


class SelectingReactor(ReactorBase):
    def _poll(self, timeout):
        rset = [trns for trns in self._transports if trns._want_read]
        wset = [trns for trns in self._transports if trns._want_write]
        if not rset and not wset:
            time.sleep(timeout)
            return
        rset2, wset2, _ = select.select(rset, wset, [], timeout)
        for set in [rset2, wset2]:
            for trns in set:
                trns.on_read(None)
    
    @classmethod
    def is_supported(cls):
        return hasattr(select, "select")




