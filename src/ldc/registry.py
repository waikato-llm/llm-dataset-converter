import importlib
import inspect
import os
from typing import Dict, Iterator

from pkg_resources import working_set, EntryPoint

from ldc.core import CommandlineHandler
from ldc.filter import Filter
from ldc.io import Reader, Writer

# the entry points defined in setup.py
ENTRY_POINT_READERS = "ldc.readers"
ENTRY_POINT_FILTERS = "ldc.filters"
ENTRY_POINT_WRITERS = "ldc.writers"

# dictionaries for caching the available plugins
AVAILABLE_READERS = None
AVAILABLE_FILTERS = None
AVAILABLE_WRITERS = None
AVAILABLE_PLUGINS = None

# environment variable with comma-separated list of modules to inspect for readers, filters, writers
ENV_LDC_MODULES = "LDC_MODULES"

# the default modules to inspect (for development)
# can be overridden with LDC_MODULES environment variable
DEFAULT_LDC_MODULES = ",".join([
    "ldc.filter",
    "ldc.pretrain",
    "ldc.supervised.context",
    "ldc.supervised.dialog",
    "ldc.supervised.pairs",
])


def _plugin_entry_points(group: str) -> Iterator[EntryPoint]:
    """
    Iterates through all plugin entry-points with the given group name.

    :param group: the group to search for
    :return: iterator of entry-points.
    """
    return working_set.iter_entry_points(group, None)


def _register_plugin(d: Dict[str, CommandlineHandler], h: CommandlineHandler):
    """
    Adds the plugin to the registry dictionary under its name.
    Raises an exception if plugin name already present.

    :param d: the registry dictionary to extend
    :type d: dict
    :param h: the plugin to add
    :type h: CommandlineHandler
    """
    if h.name() in d:
        raise Exception("Duplicate plugin name encountered: %s" % h.name())
    d[h.name()] = h


def _register_from_entry_point(group: str) -> Dict[str, CommandlineHandler]:
    """
    Generates a dictionary (name/object) for the specified entry_point group.

    :param group: the entry_point group to generate dictionary for
    :type group: str
    :return: the generated dictionary
    :rtype: dict
    """
    result = dict()
    for item in _plugin_entry_points(group):
        module = importlib.import_module(item.module_name)
        cls = getattr(module, item.attrs[0])
        obj = cls()
        _register_plugin(result, obj)
    return result


def _register_from_modules(cls):
    """
    Locates all the classes implementing the specified class and adds them to the dictionary.

    :param cls: the type to look for, eg Reader
    """
    result = dict()
    modules = os.getenv(ENV_LDC_MODULES, default=DEFAULT_LDC_MODULES).split(",")

    for m in modules:
        module = importlib.import_module(m)
        for att in dir(module):
            if att.startswith("_"):
                continue
            c = getattr(module, att)
            if inspect.isclass(c) and issubclass(c, cls):
                try:
                    o = c()
                    _register_plugin(result, o)
                except:
                    pass

    return result


def _register_from_env() -> bool:
    """
    Checks whether registering via environment variable should happen.

    :return: True if to register via environment variable
    :rtype: bool
    """
    return os.getenv(ENV_LDC_MODULES) is not None


def available_readers() -> Dict[str, CommandlineHandler]:
    """
    Returns all available readers.

    :return: the dict of reader objects
    :rtype: dict
    """
    global AVAILABLE_READERS
    if AVAILABLE_READERS is None:
        AVAILABLE_READERS = _register_from_entry_point(ENTRY_POINT_READERS)
        # fallback for development
        if (len(AVAILABLE_READERS) == 0) or _register_from_env():
            AVAILABLE_READERS = _register_from_modules(Reader)
    return AVAILABLE_READERS


def available_writers() -> Dict[str, CommandlineHandler]:
    """
    Returns all available writers.

    :return: the dict of writer objects
    :rtype: dict
    """
    global AVAILABLE_WRITERS
    if AVAILABLE_WRITERS is None:
        AVAILABLE_WRITERS = _register_from_entry_point(ENTRY_POINT_WRITERS)
        # fallback for development
        if (len(AVAILABLE_WRITERS) == 0) or _register_from_env():
            AVAILABLE_WRITERS = _register_from_modules(Writer)
    return AVAILABLE_WRITERS


def available_filters() -> Dict[str, CommandlineHandler]:
    """
    Returns all available filters.

    :return: the dict of filter objects
    :rtype: dict
    """
    global AVAILABLE_FILTERS
    if AVAILABLE_FILTERS is None:
        AVAILABLE_FILTERS = _register_from_entry_point(ENTRY_POINT_FILTERS)
        # fallback for development
        if (len(AVAILABLE_FILTERS) == 0) or _register_from_env():
            AVAILABLE_FILTERS = _register_from_modules(Filter)
    return AVAILABLE_FILTERS


def available_plugins() -> Dict[str, CommandlineHandler]:
    """
    Returns all available plugins.

    :return: the dict of plugin objects
    :rtype: dict
    """
    global AVAILABLE_PLUGINS
    if AVAILABLE_PLUGINS is None:
        AVAILABLE_PLUGINS = dict()
        AVAILABLE_PLUGINS.update(available_readers())
        AVAILABLE_PLUGINS.update(available_filters())
        AVAILABLE_PLUGINS.update(available_writers())
    return AVAILABLE_PLUGINS


def register_plugins():
    """
    Registers all plugins.
    """
    available_plugins()
