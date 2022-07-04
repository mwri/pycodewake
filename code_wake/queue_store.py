"""Queue store module."""

from __future__ import annotations

import queue
from datetime import datetime
from threading import Thread
from typing import TYPE_CHECKING

from .config import Config
from .stack_trace import Stacktrace

if TYPE_CHECKING:
    from .process import Process


class QueueStore:
    """
    Use this as a mixin/wrapper for another store to make event logging asynchronous.

    All calls are passed through to the back end store provided, except `insert_event`, which
    will just push the request on an in memory queue, to be handled asynchronously.

    This is helpful for ensuring that if a store is slow, of if there is a temporary event flood, the
    execution of the process is not immediately seriously impacted.

    Note that this breaks synchronous event logging, obviously synchronous is impossible
    as the queue is a fundanemtally asynchronous process; if `sync=True` is given this will be
    ignored.

    The time of the event is defaulted to the time the event is queued.

    For example:

        class Sql14QueueStore(QueueStore, Sql14Store):
            pass

        store = Sql14QueueStore("sqlite:////tmp/some_file.sqlite")
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._queue = queue.Queue()
        self._continue_thread = True
        self._thread = Thread(target=self._queue_proc_thread)
        self._thread.start()

    def insert_event(self, *args, st_level=2, **kwargs):
        kwargs.setdefault("when_ts", datetime.now().timestamp())

        inc_st = kwargs.get("inc_st")
        st_data = kwargs.get("st_data")
        st_len = kwargs.get("st_len")
        exc = kwargs.get("exc")

        if inc_st is None:
            inc_st = Config()["stacktraces"]["include"]["for_non_exceptions" if exc is None else "from_exceptions"]
            kwargs.setdefault("inc_st", inc_st)

        if inc_st:
            if st_data is not None:
                st = Stacktrace.from_data(st_data, st_len=st_len)
            elif exc is not None:
                st = Stacktrace.from_exc(exc, st_len=st_len)
                kwargs.setdefault("st_data", st.data())
            else:
                st = Stacktrace.from_caller(st_len=st_len, stacklevel=st_level)
                kwargs.setdefault("st_data", st.data())

        self._queue.put((args, kwargs))

    def _queue_proc_thread(self):
        while self._continue_thread:
            self._process_queue_until_empty(True, 1)
        self._process_queue_until_empty(False, 0)

    def _process_queue_until_empty(self, block, timeout):
        try:
            (logev_args, logev_kwargs) = self._queue.get(block=block, timeout=timeout)
            event_record = super().insert_event(*logev_args, **logev_kwargs)
            self._processed(event_record)
        except queue.Empty:
            pass

    def __del__(self):
        self._continue_thread = False
        self._thread.join()

    def _processed(self, event_record):
        pass
