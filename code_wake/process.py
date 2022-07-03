"""Process module."""


from __future__ import annotations

import getpass
import os
import socket
import sys
from typing import Iterable, Optional, Tuple

from singleton_type import Singleton

from .abstract_store import AbstractStore
from .config import Config
from .no_store import NoStore


class Process(NoStore.Process, metaclass=Singleton):
    """
    Singleton class representing the current process.

    This may be a simple CLI script and therefore be very transitory, or a service that runs
    for months.
    """

    def __init__(
        self,
        app_name: Optional[str] = None,
        app_vsn: Optional[str] = None,
        exe_path: Optional[str] = None,
        env_name: Optional[str] = None,
        st_for_non_exceptions: Optional[bool] = None,
        st_from_exceptions: Optional[bool] = None,
        store: Optional[AbstractStore] = None,
    ):
        """
        Ideally you would call the constructor as soon as possible when the process begins. It
        should be OK to call it from the outer scope (i.e. compile time) though it is safer (as
        with everything) to not do that, preferring to run it from a function called after all
        modules are compiled. It's up to you.

        Since it is a singleton you may invoke it without arguments subsequently.

        It may also be invoked without arguments the first time, if sufficient configuration is
        found (a store is required), see the configuration documentation.
        """

        self._async_setup = False
        self._store = store

        super().__init__(
            pid=os.getpid(),
            username=getpass.getuser(),
            fqdn=socket.getfqdn(),
            exe_path=exe_path or os.environ.get("_") or sys.argv[0],
        )

        environment_name = env_name or Config()["environment"]["name"]
        self._environment = None if environment_name is None else NoStore.Environment(name=environment_name)

        app_name = app_name or Config()["app"]["name"] or exe_path or os.environ.get("_") or sys.argv[0]
        self._app = NoStore.App(name=app_name)

        app_vsn = app_vsn or Config()["app"]["vsn"]
        self._app_vsn = None if app_vsn is None else NoStore.AppVsn(vsn=app_vsn)

        self._st_for_non_exceptions = (
            st_for_non_exceptions
            if st_for_non_exceptions is not None
            else Config()["stacktraces"]["include"]["for_non_exceptions"]
        )

        self._st_from_exceptions = (
            st_from_exceptions
            if st_from_exceptions is not None
            else Config()["stacktraces"]["include"]["from_exceptions"]
        )

    def init(self):
        """Force initialisation (synchronises to store). This is normally done lazily."""

        if self._async_setup:
            raise RuntimeError("double init")

        return self._async_init()

    def _async_init(self):
        if self._store is None:
            self._store = Config().store()

        store_record = self._store.insert_process(self)

        self._id = store_record.id
        self._environment = store_record.environment
        self._app = store_record.app
        self._app_vsn = store_record.app_vsn

        self._async_setup = True

        return self

    @property
    def environment(self):
        return self._environment

    @property
    def app(self):
        return self._app

    @property
    def app_vsn(self):
        return self._app_vsn

    @property
    def id(self):
        if not self._async_setup:
            self._async_init()

        return self._id

    @property
    def store(self):
        if not self._async_setup:
            self._async_init()

        return self._store

    def log(
        self,
        data: Optional[Iterable[Tuple[str, str]]] = None,
        exc: Optional[Exception] = None,
        inc_st: Optional[bool] = None,
        st_len: Optional[int] = None,
        when_ts: Optional[float] = None,
        sync: Optional[bool] = False,
    ) -> Optional[AbstractStore.Event]:
        if not self._async_setup:
            self._async_init()

        if inc_st is None:
            if exc is None:
                inc_st = self._st_for_non_exceptions
            else:
                inc_st = self._st_from_exceptions

        return self._store.insert_event(self, data, exc=exc, inc_st=inc_st, st_len=st_len, sync=sync)  # type: ignore
