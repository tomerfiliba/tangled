import time
import select
import socket # needed for windows
from .base import ReactorBase


class SelectingReactor(ReactorBase):
    def _poll_transports(self, timeout):
        if not self._read_transports and not self._write_transports:
            time.sleep(timeout)
            return
        try:
            rlst, wlst, _ = select.select(self._read_transports, self._write_transports, [], timeout)
        except (select.error, OSError):
            self._prune_bad_fds()
            return
        for trns in rlst:
            self.call(trns.on_read, -1)
        for trns in wlst:
            self.call(trns.on_write, -1)
    
    @classmethod
    def is_supported(cls):
        return hasattr(select, "select")




