"""Config module tests."""


from code_wake.config import Config


def test_constructor_returns_obj():
    assert isinstance(Config(), Config)


def test_obj_is_singleton():
    assert id(Config()) == id(Config())
