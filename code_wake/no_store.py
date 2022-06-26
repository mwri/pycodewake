"""No store module."""


from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .process import Process


class NoStore:
    """
    Used in place of a store by a current/running process object until it commits to a real store.

    Maintains minimal API compatibility layer with real stores and store provided process objects.
    """

    def get_process_by_id(self, id: int):
        raise Exception("unimplemented")

    def insert_process(self, unstored_process: Process):
        raise Exception("unimplemented")

    def insert_event(self):
        raise Exception("unimplemented")

    class Process:
        """A single process / process invocation."""

        def __init__(self, *, pid: int, username: str, fqdn: str, exe_path: str):
            """Initialise process."""

            self.pid = pid
            self.username = username
            self.fqdn = fqdn
            self.exe_path = exe_path

    class Environment:
        """Environment."""

        def __init__(self, name: str):
            self.name = name
            self.id = None

    class App:
        """App."""

        def __init__(self, name: str):
            self.name = name

    class AppVsn:
        """App version."""

        def __init__(self, vsn: str):
            self.vsn = vsn
