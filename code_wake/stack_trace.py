"""Stack traces module."""


import traceback

from . import utils


class Stacktrace:
    """Common stack trace interface class."""

    def __init__(self, stackframes):
        """Initialise stack trace."""

        self._stackframes = stackframes

    @property
    def stackframes(self):
        """The stack trace's stack frames."""

        return self._stackframes

    @classmethod
    def from_exc(cls, exc, st_len=None):
        """
        Return a stack trace from the given exception.
        """

        exc_traceback = exc.__traceback__

        return cls(
            [
                Stacktrace.Stackframe(sf.filename, sf.lineno, sf.line)
                for sf in traceback.extract_tb(exc_traceback if st_len is None else exc_traceback[-st_len:])
            ]
        )

    @classmethod
    def from_raised_exc(cls, st_len=None):
        """
        Return a stack trace from the raised exception. Must be called within an 'except' clause.
        """

        return cls(
            [
                Stacktrace.Stackframe(sf.filename, sf.lineno, sf.line)
                for sf in traceback.extract_tb(exc_traceback if st_len is None else exc_traceback[-st_len:])
            ]
        )

    @classmethod
    def from_data(cls, data, st_len=None):
        """
        Return a stack trace from the data.

        The data is as returned by the 'data' method, thus 'data' and 'from_date' may be used to serialise
        and deserialise stack trace objects.
        """

        return cls([Stacktrace.Stackframe(*data_frame) for data_frame in (data if st_len is None else data[-st_len:])])

    @classmethod
    def from_caller(cls, st_len=None, stacklevel=2):
        """
        Return a stack trace for the caller.

        The 'stacklevel' kwarg (default 2) dictates how many frames are discarded from the top.
        """

        caller_traceback = traceback.extract_stack()[:-stacklevel]

        return cls(
            [
                Stacktrace.Stackframe(sf.filename, sf.lineno, sf.line)
                for sf in (caller_traceback if st_len is None else caller_traceback[-st_len:])
            ]
        )

    def digest(self):
        """A binary digest for the stack trace."""

        return utils.data_digest(self.data())

    def data(self):
        """Data structure representing the stack trace."""

        return [sf.data() for sf in self._stackframes]

    def __str__(self):
        return f"<Stacktrace(len(stackframes)={len(self._stackframes)})>"

    class Stackframe:
        """Common stack frame interface class."""

        def __init__(self, filename, lineno, src):
            """Initialise stack frame."""

            self._filename = filename
            self._lineno = lineno
            self._src = src

        @property
        def filename(self):
            """Filename."""

            return self._filename

        @property
        def lineno(self):
            """Line number."""

            return self._lineno

        @property
        def src(self):
            """Source code line."""

            return self._src

        def data(self):
            """Data structure representing the stackframe."""

            return [self._filename, self._lineno, self._src]

        def __str__(self):
            return f"{self._filename}:{self._lineno}: {self._src}"
