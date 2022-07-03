"""Abstract store module."""


from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, List, Optional, Tuple

if TYPE_CHECKING:
    from .process import Process


class AbstractStore:
    def get_process_by_id(self, id: int) -> Optional[AbstractStore.Process]:
        raise Exception("unimplemented")

    def insert_process(self, unstored_process: Process) -> AbstractStore.Process:
        raise Exception("unimplemented")

    def session(self) -> Any:
        raise Exception("unimplemented")

    def insert_app(self, name: str, vsn: Optional[str] = None) -> AbstractStore.App:
        raise Exception("unimplemented")

    def get_environment_by_id(self, id: int) -> Optional[AbstractStore.Environment]:
        raise Exception("unimplemented")

    def get_app_by_id(self, id: int) -> Optional[AbstractStore.App]:
        raise Exception("unimplemented")

    def get_app_vsn_by_id(self, id: int) -> Optional[AbstractStore.AppVsn]:
        raise Exception("unimplemented")

    def insert_event(
        self,
        process: Process,
        data: Optional[Iterable[Tuple[str, str]]] = None,
        exc: Optional[Exception] = None,
        inc_st: Optional[bool] = None,
        st_len: Optional[int] = None,
        st_data: Optional[List[Tuple[str, int, str]]] = None,
        sync: Optional[bool] = None,
    ) -> Optional[AbstractStore.Event]:
        raise Exception("unimplemented")

    def get_events_by_data(self, where: Iterable[Tuple[str, str]]) -> List[AbstractStore.Event]:
        raise Exception("unimplemented")

    class Process:
        """A single process / process invocation."""

        def __init__(self, *, pid: int, username: str, fqdn: str, exe_path: str):
            """Initialise process."""

    class Environment:
        """Environment."""

        def __init__(self, *args, **kwargs):
            raise Exception("unimplemented")

    class App:
        """App."""

        def __init__(self, *args, **kwargs):
            raise Exception("unimplemented")

    class AppVsn:
        """App version."""

        def __init__(self, *args, **kwargs):
            raise Exception("unimplemented")

    class Event:
        """Event."""

        def __init__(self, *args, **kwargs):
            raise Exception("unimplemented")
