"""Store adapters integration tests module."""


from code_wake.test import store as test_store

from .conftest import ptparam_stores

for name in dir(test_store):
    if name.startswith("test_"):
        vars()[name] = ptparam_stores(getattr(test_store, name))
