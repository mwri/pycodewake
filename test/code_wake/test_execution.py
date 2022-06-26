"""Process module tests."""


import pytest

from code_wake import Process

from .conftest import ptparam_stores


@ptparam_stores
def test_constructor_returns_obj(store):
    assert isinstance(Process(store=store), Process)


@ptparam_stores
def test_obj_is_singleton(store):
    assert id(Process(store=store)) == id(Process(store=store))


@ptparam_stores
def test_pid_returns_int(process):
    assert isinstance(process.pid, int)


@ptparam_stores
def test_username_returns_str(process):
    assert isinstance(process.username, str)


@ptparam_stores
def test_fqdn_returns_str(process):
    assert isinstance(process.fqdn, str)


@ptparam_stores
def test_exe_path_returns_str(process):
    assert isinstance(process.exe_path, str)


@ptparam_stores
def test_app_name_returns_str(process):
    assert isinstance(process.app.name, str)


@ptparam_stores
def test_id_returns_int(process):
    assert isinstance(process.id, int)
