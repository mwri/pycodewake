"""Code Wake integration store tests Pytest configuration / fixtures."""

import contextlib
import queue
import threading
import time

import flask
import flask.testing
import pytest
import sqlalchemy as sa
from code_wake_sql14_store import Sql14Store
from code_wake_v1rest_store import V1RestStore
from code_wake_v1wsgi_service import V1WsgiMiddleware
from requests_flask_adapter import Session

from code_wake import Process, QueueStore
from code_wake.test.conftest import *


def v1rest_store_params():
    flask_app = flask.Flask(__name__)
    flask_app.wsgi_app = V1WsgiMiddleware(flask_app.wsgi_app, "", Sql14Store("sqlite:///:memory:"))

    Session.register("http://", flask_app)

    return (["http://abc"], {"session": Session()})


class TestV1RestStore(V1RestStore):
    def __init__(self, *args, session, **kwargs):
        super().__init__(*args, **kwargs)

        self._session = session

    def session(self):
        return self._session


class TestSql14QueueStore(QueueStore, Sql14Store):
    def __init__(self, *args, **kwargs):
        """
        Modified QueueStore using Sql14Store.

        This uses a ./test.sqlite instead of the memory DB, because, ugh, memory
        sqlite doesn't work cross threads :( so, this cleans the DB before the
        Sql14Store constructor is called to make sure it is empty, and it uses
        a queue to turn the fundamentally async event logging back into sync, which
        is handy for unit testing.
        """

        engine = sa.create_engine("sqlite:///./test.sqlite")
        with contextlib.closing(engine.connect()) as conn:
            trans = conn.begin()
            for table in reversed(self.Base.metadata.sorted_tables):
                try:
                    conn.execute(table.delete())
                except sa.exc.OperationalError:
                    pass

            trans.commit()

        super().__init__(*args, **kwargs)

        self._processed_events = queue.Queue()

    def insert_event(self, *args, st_level=2, **kwargs):
        super().insert_event(*args, st_level=st_level + 1, **kwargs)

        return self._processed_events.get(block=True, timeout=2)

    def _processed(self, event_record):
        super()._processed(event_record)

        self._processed_events.put(event_record)


def sql14queue_store_cleanup(store):
    store.__del__()


ptparam_stores = pytest.mark.parametrize(
    "store_cls,store_params,store_cleanup",
    [
        (Sql14Store, (["sqlite:///:memory:"], {}), lambda _store: None),
        (TestV1RestStore, v1rest_store_params, lambda _store: None),
        (TestSql14QueueStore, (["sqlite:///./test.sqlite"], {}), sql14queue_store_cleanup),
    ],
)
