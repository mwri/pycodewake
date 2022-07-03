"""Pytest configuration / fixtures."""


import pytest
from code_wake_sql14_store import Sql14Store

from code_wake import Process
from code_wake.abstract_store import AbstractStore
from code_wake.test.conftest import *

ptparam_stores = pytest.mark.parametrize(
    "store_cls,store_params,store_cleanup",
    [
        (Sql14Store, (["sqlite:///:memory:"], {}), lambda _store: None),
    ],
)
