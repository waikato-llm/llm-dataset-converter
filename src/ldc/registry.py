import importlib
import inspect
import logging
import os
import sys
import traceback
from typing import Dict, Iterator, List

from pkg_resources import working_set, EntryPoint

from ldc.core import CommandlineHandler
from ldc.download import Downloader
from ldc.filter import Filter
from ldc.io import Reader, Writer

# the entry points defined in setup.py
ENTRY_POINT_DOWNLOADERS = "ldc.downloaders"
ENTRY_POINT_READERS = "ldc.readers"
ENTRY_POINT_FILTERS = "ldc.filters"
ENTRY_POINT_WRITERS = "ldc.writers"

# dictionaries for caching the available plugins
AVAILABLE_DOWNLOADERS = None
AVAILABLE_READERS = None
AVAILABLE_FILTERS = None
AVAILABLE_WRITERS = None
AVAILABLE_PLUGINS = None

# environment variable with comma-separated list of modules to inspect for readers, filters, writers
ENV_LDC_MODULES = "LDC_MODULES"

# the default modules to inspect (for development)
# can be overridden with LDC_MODULES environment variable
DEFAULT_LDC_MODULES = ",".join([
    "ldc.download",
    "ldc.filter",
    "ldc.pretrain",
    "ldc.supervised.pairs",
    "ldc.translation",
])

LLM_REGISTRY = "llm-registry"

_logger = None


def logger() -> logging.Logger:
    """
    Returns the logger instance to use, initializes it if necessary.

    :return: the logger instance
    :rtype: logging.Logger
    """
    global _logger
    if _logger is None:
        _logger = logging.getLogger(LLM_REGISTRY)
    return _logger


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


def _register_from_modules(cls, modules: List[str] = None):
    """
    Locates all the classes implementing the specified class and adds them to the dictionary.

    :param cls: the type to look for, eg Reader
    :param modules: the list of modules to use instead of env variable or default modules
    :type modules: list
    """
    result = dict()
    if modules is None:
        modules = os.getenv(ENV_LDC_MODULES, default=DEFAULT_LDC_MODULES).split(",")
    logger().info("%s using modules: %s" % (cls.__name__, str(modules)))

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
                except NotImplementedError:
                    pass
                except:
                    print("Problem encountered instantiating: " + m + "." + att, file=sys.stderr)
                    traceback.print_exc()

    return result


def _register_from_env() -> bool:
    """
    Checks whether registering via environment variable should happen.

    :return: True if to register via environment variable
    :rtype: bool
    """
    return os.getenv(ENV_LDC_MODULES) is not None


def available_downloaders(modules: List[str] = None) -> Dict[str, CommandlineHandler]:
    """
    Returns all available downloaders.

    :param modules: the list of modules to use instead of env variable or default modules
    :type modules: list
    :return: the dict of downloader objects
    :rtype: dict
    """
    global AVAILABLE_DOWNLOADERS
    if AVAILABLE_DOWNLOADERS is None:
        AVAILABLE_DOWNLOADERS = _register_from_entry_point(ENTRY_POINT_DOWNLOADERS)
        # fallback for development
        if (len(AVAILABLE_DOWNLOADERS) == 0) or _register_from_env() or (modules is not None):
            AVAILABLE_DOWNLOADERS = _register_from_modules(Downloader, modules)
    return AVAILABLE_DOWNLOADERS


def available_readers(modules: List[str] = None) -> Dict[str, CommandlineHandler]:
    """
    Returns all available readers.

    :param modules: the list of modules to use instead of env variable or default modules
    :type modules: list
    :return: the dict of reader objects
    :rtype: dict
    """
    global AVAILABLE_READERS
    if AVAILABLE_READERS is None:
        AVAILABLE_READERS = _register_from_entry_point(ENTRY_POINT_READERS)
        # fallback for development
        if (len(AVAILABLE_READERS) == 0) or _register_from_env() or (modules is not None):
            AVAILABLE_READERS = _register_from_modules(Reader, modules)
    return AVAILABLE_READERS


def available_writers(modules: List[str] = None) -> Dict[str, CommandlineHandler]:
    """
    Returns all available writers.

    :param modules: the list of modules to use instead of env variable or default modules
    :type modules: list
    :return: the dict of writer objects
    :rtype: dict
    """
    global AVAILABLE_WRITERS
    if AVAILABLE_WRITERS is None:
        AVAILABLE_WRITERS = _register_from_entry_point(ENTRY_POINT_WRITERS)
        # fallback for development
        if (len(AVAILABLE_WRITERS) == 0) or _register_from_env() or (modules is not None):
            AVAILABLE_WRITERS = _register_from_modules(Writer, modules)
    return AVAILABLE_WRITERS


def available_filters(modules: List[str] = None) -> Dict[str, CommandlineHandler]:
    """
    Returns all available filters.

    :param modules: the list of modules to use instead of env variable or default modules
    :type modules: list
    :return: the dict of filter objects
    :rtype: dict
    """
    global AVAILABLE_FILTERS
    if AVAILABLE_FILTERS is None:
        AVAILABLE_FILTERS = _register_from_entry_point(ENTRY_POINT_FILTERS)
        # fallback for development
        if (len(AVAILABLE_FILTERS) == 0) or _register_from_env() or (modules is not None):
            AVAILABLE_FILTERS = _register_from_modules(Filter, modules)
    return AVAILABLE_FILTERS


def available_plugins(modules: List[str] = None) -> Dict[str, CommandlineHandler]:
    """
    Returns all available plugins.

    :param modules: the list of modules to use instead of env variable or default modules
    :type modules: list
    :return: the dict of plugin objects
    :rtype: dict
    """
    global AVAILABLE_PLUGINS
    if AVAILABLE_PLUGINS is None:
        AVAILABLE_PLUGINS = dict()
        AVAILABLE_PLUGINS.update(available_downloaders(modules))
        AVAILABLE_PLUGINS.update(available_readers(modules))
        AVAILABLE_PLUGINS.update(available_filters(modules))
        AVAILABLE_PLUGINS.update(available_writers(modules))
    return AVAILABLE_PLUGINS


def register_plugins(modules: List[str] = None):
    """
    Registers all plugins.

    :param modules: the list of modules to use instead of env variable or default modules
    :type modules: list
    """
    available_plugins(modules)
