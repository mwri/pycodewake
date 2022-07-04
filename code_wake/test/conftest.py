"""
Code Wake store tests Pytest configuration / fixtures.

Store adapters should use this module to run standard store adapter tests.
"""


import pytest

from code_wake import Process
from code_wake.abstract_store import AbstractStore


@pytest.fixture
def clear():
    Process().singleton_detach_ref()


@pytest.fixture
def store(clear, store_cls, store_params, store_cleanup) -> AbstractStore:
    (args, kwargs) = store_params() if callable(store_params) else store_params
    store = store_cls(*args, **kwargs)
    yield store
    store_cleanup(store)


@pytest.fixture
def process(store):
    return Process(store=store).init()


@pytest.fixture
def loaded_process(store, process):
    return store.get_process_by_id(process.id)


@pytest.fixture
def exc():
    def foo():
        bar()

    def bar():
        baz()

    def baz():
        raise Exception("foo bar baz")

    try:
        foo()
    except Exception as err:
        return err
