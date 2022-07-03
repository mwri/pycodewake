# Python code wake lib/service (pycodewake)

[![test](https://github.com/mwri/pycodewake/actions/workflows/test.yml/badge.svg)](https://github.com/mwri/pycodewake/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/mwri/pycodewake/branch/main/graph/badge.svg)](https://codecov.io/gh/mwri/pycodewake)

## Concept

Code Wake is a code instrumentation aid, recording to a database for analysis.

With configuration so that Code Wake can find a data store, usage can be as
simple as this, create a process:

```python
import code_wake

cwproc = code_wake.Process()
cwproc.log()
```

Record events:

```python
cwproc.log({"event": "order", "type": "special", "customer": customer})
```

Or log an exception:

```python
cwproc.log({"event": "fault", "doing": "create_order", "customer": customer}, exc)
```

Here `exc` is an exception, and by default it's stack trace will be recorded along with
the event. Stack traces may also be recorded for non exception events as well, either
by specifying `inc_st=True`, or by changing the configuration such that non exception
events always have them.

The event will be logged asynchronously by default if the store supports this, and
thus `log` will return `None`. If you specify the kward `sync=True` then the event
created will be returned.

## Configuration

By default, if `/etc/code_wake.conf` exists, or `./etc/code_wake.conf`, then they will
be taken as configuration. If the `CODE_WAKE_CONFIG` environment variable is set then
this will override the config location.

What you put in the configuration depends a lot on if it is a global config used my many
different apps, or just one, and having a configuration at all is entirely optional.

A complete, canonical configuration might look like this:

```yaml
store:
    adapter: "code_wake_sql14_store,Sql14Store"
    config: "sqlite:////tmp/some_file.sqlite"
environment:
    name: "production"
app:
    name: "my_app"
    vsn: "1.2.3"
stacktraces:
    include:
        from_exceptions: true
        for_non_exceptions: false
```

This might be appropriate for a simple app, as it configures the app name and version.
A more general config for use by many apps would certainly omit those.

An environment is optional, app versions are optional, the stack trace configuration
will be defaulted, the app name will default to the executable path, so the only really
essential thing is the store adapter and configuration. If you don't want to use a config
you must provide at least that when you instantiate your process.

## Use without config

If you do not use a config, you should instantiate a store adapter yourself and pass
it to the `Process` constructor:

```python
import code_wake
from code_wake_sql14_store import Sql14Store

cwproc = code_wake.Process(store=Sql14Store("sqlite:////tmp/some_file.sqlite"))
```

The process is a singleton, so subsequently when you want to log an event you can
simply do:

```python
import code_wake

cwproc = code_wake.Process()
cwproc.log({"what": "ever"})
```

## Other process options

When you instantiate the `Process` for the first time, there are other options which
would be good to use (if there isn't a configurartion to provide good values):

```python
import code_wake
from code_wake_sql14_store import Sql14Store

cwproc = code_wake.Process(
    app_name="my_app",
    app_vsn="1.2.3",
    env_name="production",
    store=Sql14Store("sqlite:////tmp/some_file.sqlite"),
)
```

Also `st_for_non_exceptions` will override the recording of stack traces for non exception
events and `st_from_exceptions` for exception events.

## Queue store

A "queue store" which can be mixed in with another store, can be used to turn any
store into one which always queues, instead of immediately adding the event. This
means that a process may be protected from being adversely affected by high latency
or unreliable stores. The events are processed by another thread, which commits them
to whatever actual storage you are using.

For example:

```python
from code_wake import QueueStore
from code_wake_sql14_store import Sql14Store

class Sql14QueueStore(QueueStore, Sql14Store):
    pass

store = Sql14QueueStore("sqlite:////tmp/some_file.sqlite")
```

The store adapter used with the queue store must be thread safe and cross thread operable.
Sqlite for example, does not work cross threads when used with memory backing!

## Environment variables

Apart from `CODE_WAKE_CONFIG` to set the config, the following are supported
and will override any configuration file settings if set:

| Environment variable            | Description |
+---------------------------------+-------------|
| CODE_WAKE_STORE_ADAPTER         | set the store adapter (module,class) |
| CODE_WAKE_STORE_CONFIG          | comma separated adapter params |
| CODE_WAKE_ENVIRONMENT           | name of the environment |
| CODE_WAKE_APP_NAME              | name of the application |
| CODE_WAKE_APP_VSN               | version of the application |
| CODE_WAKE_ST_FROM_EXCEPTIONS    | "true" or "false to turn exception stack traces on/off |
| CODE_WAKE_ST_FOR_NON_EXCEPTIONS | "true" or "false to turn other event stack traces on/off |
