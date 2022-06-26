"""Config module."""

import os

import yaml
from singleton_type import Singleton


class Config(dict, metaclass=Singleton):
    """Singleton class which subclasses dict."""

    def __init__(self):
        """
        Loads configuration, filling with defaults and environment variables as available.

        If the environment variable CODE_WAKE_CONFIG is given this will be taken as the
        path of a configuration file, if it exists.

        Otherwise "/etc/code_wake.conf" and then "./etc/code_wake.conf" will be looked
        for and loaded if they exist.
        """

        self._path = (
            self._file_exists(os.environ.get("CODE_WAKE_CONFIG"))
            or self._file_exists("/etc/code_wake.conf")
            or self._file_exists("./etc/code_wake.conf")
            or None
        )

        self._load()

    @classmethod
    def _file_exists(cls, path):
        if path is None:
            return None

        return os.path.exists(path) and os.path.isfile(path)

    def reload(self):
        self._load()

    def _load(self):
        self._store = None

        self.clear()

        if self._path is not None:
            with open(self._path, encoding="utf-8") as fh:
                for k, v in yaml.safe_load(fh).items():
                    self[k] = v

        self.setdefault("store", {})
        self["store"].setdefault("adapter", None)
        if os.environ.get("CODE_WAKE_STORE_ADAPTER"):
            self["store"]["adapter"] = os.environ.get("CODE_WAKE_STORE_ADAPTER")
        self["store"].setdefault("config", None)
        if os.environ.get("CODE_WAKE_STORE_CONFIG"):
            self["store"]["config"] = os.environ.get("CODE_WAKE_STORE_CONFIG")

        self.setdefault("environment", {})
        self["environment"].setdefault("name", None)
        if os.environ.get("CODE_WAKE_ENVIRONMENT"):
            self["environment"]["name"] = os.environ.get("CODE_WAKE_ENVIRONMENT")

        self.setdefault("app", {})
        self["app"].setdefault("name", None)
        if os.environ.get("CODE_WAKE_APP_NAME"):
            self["app"]["name"] = os.environ.get("CODE_WAKE_APP_NAME")
        self["app"].setdefault("vsn", None)
        if os.environ.get("CODE_WAKE_APP_VSN"):
            self["app"]["vsn"] = os.environ.get("CODE_WAKE_APP_VSN")

        self.setdefault("stacktraces", {})
        self["stacktraces"]["include"] = self._st_include_config(self["stacktraces"].get("include", {}))

    def _st_include_config(self, defaults):
        inc_from_exceptions = True

        if os.environ.get("CODE_WAKE_ST_FROM_EXCEPTIONS"):
            inc_from_exceptions = os.environ.get("CODE_WAKE_ST_FROM_EXCEPTIONS").lower() == "true"
        elif "from_exceptions" in defaults:
            inc_from_exceptions = bool(defaults["from_exceptions"])

        inc_for_non_exceptions = False

        if os.environ.get("CODE_WAKE_ST_FOR_NON_EXCEPTIONS"):
            inc_for_non_exceptions = os.environ.get("CODE_WAKE_ST_FOR_NON_EXCEPTIONS").lower() == "true"
        elif "for_non_exceptions" in defaults:
            inc_for_non_exceptions = bool(defaults["for_non_exceptions"])

        return {
            "from_exceptions": inc_from_exceptions,
            "for_non_exceptions": inc_for_non_exceptions,
        }

    def store(self):
        """Return the store implied by the config. This is cached, so it will be the same store thereafter."""

        if hasattr(self, "_store") and self._store is not None:
            return self._store

        try:
            (store_mod_name, store_cls_name) = self["store"]["adapter"].split(",")
            store_cls = getattr(__import__(store_mod_name), store_cls_name)
            store_args = self["store"]["config"].split(",")
        except Exception as err:
            raise Exception(f'could not load store module "{store_mod_name}" class "{store_cls_name}"') from err

        self._store = store_cls(*store_args)

        return self._store
