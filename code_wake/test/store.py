"""
Code Wake store tests module.

All store adapters should pass these tests.

Two fixtures must be provided by the store adapter test suite to make these tests work:

store_cls - the store adapter class
store_params - a two tuple (args and kwargs) providing the arguments for the store constructor
"""


import pytest

from code_wake import Process


def test_constructor_returns_obj(store_cls, store_params):
    (args, kwargs) = store_params() if callable(store_params) else store_params
    assert isinstance(store_cls(*args, **kwargs), store_cls)


def test_insert_process_no_env_name_inserts_process_without_env(store):
    proc = Process(store=store, env_name=None)
    store.insert_process(proc)

    loaded_process = store.get_process_by_id(proc.id)
    assert isinstance(loaded_process, store.Process)
    assert loaded_process.environment is None


def test_insert_process_with_env_name_inserts_process_with_env(store):
    proc = Process(store=store, env_name="foo")
    store.insert_process(proc)

    loaded_process = store.get_process_by_id(proc.id)
    assert isinstance(loaded_process, store.Process)
    assert loaded_process.environment.name == "foo"


def test_insert_process_no_existing_app_name_inserts_process_with_app(store):
    proc = Process(store=store, app_name="bar")
    store.insert_process(proc)

    loaded_process = store.get_process_by_id(proc.id)
    assert isinstance(loaded_process, store.Process)
    assert loaded_process.app.name == "bar"


def test_insert_process_with_existing_app_name_inserts_process_with_app(store):
    store.insert_app("baz")

    proc = Process(store=store, app_name="baz")
    store.insert_process(proc)

    loaded_process = store.get_process_by_id(proc.id)
    assert isinstance(loaded_process, store.Process)
    assert loaded_process.app.name == "baz"


def test_insert_process_without_app_vsn_inserts_process_with_no_app_vsn(store):
    proc = Process(store=store, app_name="bar")
    store.insert_process(proc)

    loaded_process = store.get_process_by_id(proc.id)
    assert isinstance(loaded_process, store.Process)
    assert loaded_process.app_vsn is None


def test_insert_process_with_app_vsn_inserts_process_with_app_vsn(store):
    proc = Process(store=store, app_name="bar", app_vsn="1.2.3")
    store.insert_process(proc)

    loaded_process = store.get_process_by_id(proc.id)
    assert isinstance(loaded_process, store.Process)
    assert loaded_process.app_vsn.vsn == "1.2.3"


def test_insert_event_returns_event(store, process):
    event = store.insert_event(process)
    assert isinstance(event, store.Event)


def test_logged_event_has_logged_data(store, process):
    event = store.insert_event(process, data=(("foo1", "foo1bar"), ("bar2", "bar2baz")))
    assert len(event.data) == 2
    loaded_data = [{r.key: r.val} for r in event.data]
    assert {"foo1": "foo1bar"} in loaded_data
    assert {"bar2": "bar2baz"} in loaded_data


def test_logged_event_has_no_stacktrace_by_default(store, process):
    event = store.insert_event(process)
    assert event.stacktrace is None


def test_logged_event_has_stacktrace_if_requested(store, process):
    event = store.insert_event(process, inc_st=True)
    assert event.stacktrace is not None


def test_logged_event_like_stacktraces_not_duplicated_if_same(store, process):
    def bat(st_len):
        return store.insert_event(process, inc_st=True, st_len=st_len)

    event1 = bat(1)
    st1 = event1.stacktrace
    event2 = bat(1)
    st2 = event2.stacktrace

    assert st1.id == st2.id

    event3 = bat(2)
    st3 = event3.stacktrace
    event4 = bat(2)
    st4 = event4.stacktrace

    assert st3.id != st4.id


def test_logged_exc_event_like_stacktraces_not_duplicated_if_same(store, process, exc):
    event1 = store.insert_event(process, exc=exc)
    st1 = event1.stacktrace
    event2 = store.insert_event(process, exc=exc)
    st2 = event2.stacktrace

    assert st1.id == st2.id

    exc2 = None
    try:
        1 / 0
    except Exception as err:
        exc2 = err
    assert isinstance(exc2, Exception)

    event3 = store.insert_event(process, exc=exc2)
    st3 = event3.stacktrace

    assert st1.id != st3.id


def test_logged_event_stacktrace_frames_as_expected(store, process):
    def foo():
        return bar()

    def bar():
        return baz()

    def baz():
        return store.insert_event(process, inc_st=True)

    event = foo()

    assert event.stacktrace.stackframes[0].filename.endswith(".py")
    assert isinstance(event.stacktrace.stackframes[0].lineno, int)
    assert event.stacktrace.stackframes[0].src == "return store.insert_event(process, inc_st=True)"

    assert event.stacktrace.stackframes[1].filename.endswith(".py")
    assert isinstance(event.stacktrace.stackframes[1].lineno, int)
    assert event.stacktrace.stackframes[1].src == "return baz()"

    assert event.stacktrace.stackframes[2].filename.endswith(".py")
    assert isinstance(event.stacktrace.stackframes[2].lineno, int)
    assert event.stacktrace.stackframes[2].src == "return bar()"

    assert event.stacktrace.stackframes[3].filename.endswith(".py")
    assert isinstance(event.stacktrace.stackframes[3].lineno, int)
    assert event.stacktrace.stackframes[3].src == "event = foo()"


def test_logged_exc_event_has_stacktrace_by_default(store, process, exc):
    event = store.insert_event(process, exc=exc)
    assert event.stacktrace is not None


def test_logged_exc_event_stacktrace_frames_as_expected(store, process, exc):
    event = store.insert_event(process, exc=exc)
    assert event.stacktrace is not None

    assert event.stacktrace.stackframes[0].filename.endswith(".py")
    assert isinstance(event.stacktrace.stackframes[0].lineno, int)
    assert event.stacktrace.stackframes[0].src == 'raise Exception("foo bar baz")'

    assert event.stacktrace.stackframes[1].filename.endswith(".py")
    assert isinstance(event.stacktrace.stackframes[1].lineno, int)
    assert event.stacktrace.stackframes[1].src == "baz()"

    assert event.stacktrace.stackframes[2].filename.endswith(".py")
    assert isinstance(event.stacktrace.stackframes[2].lineno, int)
    assert event.stacktrace.stackframes[2].src == "bar()"

    assert event.stacktrace.stackframes[3].filename.endswith(".py")
    assert isinstance(event.stacktrace.stackframes[3].lineno, int)
    assert event.stacktrace.stackframes[3].src == "foo()"


def test_logged_exc_event_has_no_stacktrace_if_requested(store, process, exc):
    event = store.insert_event(process, exc=exc, inc_st=False)
    assert event.stacktrace is None


def test_get_events_by_data_one_term_returns_indicated_events(store, process):
    event1 = store.insert_event(process, (("foo", "foo1"), ("bar", "bar1"), ("baz", "baz1")))
    event2 = store.insert_event(process, (("foo", "foo2"), ("bar", "bar1"), ("baz", "baz1")))
    event3 = store.insert_event(process, (("foo", "foo2"), ("bar", "bar2"), ("baz", "baz1"), ("baz", "baz2")))
    event4 = store.insert_event(process, (("foo", "foo3"), ("bar", "bar1"), ("baz", "baz1")))

    assert set([e.id for e in store.get_events_by_data((("foo", "foo1"),))]) == set([event1.id])
    assert set([e.id for e in store.get_events_by_data((("foo", "foo2"),))]) == set([event2.id, event3.id])
    assert set([e.id for e in store.get_events_by_data((("foo", "foo4"),))]) == set()
    assert set([e.id for e in store.get_events_by_data((("baz", "foo4"),))]) == set()


def test_get_events_by_data_two_terms_returns_indicated_events(store, process):
    event1 = store.insert_event(process, (("foo", "foo1"), ("bar", "bar1"), ("baz", "baz1")))
    event2 = store.insert_event(process, (("foo", "foo2"), ("bar", "bar1"), ("baz", "baz1")))
    event3 = store.insert_event(process, (("foo", "foo2"), ("bar", "bar2"), ("baz", "baz1"), ("baz", "baz2")))
    event4 = store.insert_event(process, (("foo", "foo3"), ("bar", "bar1"), ("baz", "baz1")))

    result_set = set([e.id for e in store.get_events_by_data((("foo", "foo1"), ("bar", "bar2")))])
    expected_set = set()
    assert result_set == expected_set

    result_set = set([e.id for e in store.get_events_by_data((("foo", "foo2"), ("bar", "bar2")))])
    expected_set = set([event3.id])
    assert result_set == expected_set

    result_set = set([e.id for e in store.get_events_by_data((("foo", "foo2"), ("baz", "baz1")))])
    expected_set = set([event2.id, event3.id])
    assert result_set == expected_set


def test_get_events_by_data_three_terms_two_unique_keys_returns_indicated_events(store, process):
    event1 = store.insert_event(process, (("foo", "foo1"), ("bar", "bar1"), ("baz", "baz1")))
    event2 = store.insert_event(process, (("foo", "foo2"), ("bar", "bar1"), ("baz", "baz1")))
    event3 = store.insert_event(process, (("foo", "foo2"), ("bar", "bar2"), ("baz", "baz1"), ("baz", "baz2")))
    event4 = store.insert_event(process, (("foo", "foo3"), ("bar", "bar1"), ("baz", "baz1")))

    result_set = set([e.id for e in store.get_events_by_data((("foo", "foo2"), ("baz", "baz1"), ("baz", "baz2")))])
    expected_set = set([event3.id])
    assert result_set == expected_set
