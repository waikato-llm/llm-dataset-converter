import logging
from typing import Dict, List

from ldc.download import Downloader
from ldc.filter import Filter
from ldc.io import Reader, Writer
from seppl import Registry, Plugin

# the entry points defined in setup.py
ENTRY_POINT_DOWNLOADERS = "ldc.downloaders"
ENTRY_POINT_READERS = "ldc.readers"
ENTRY_POINT_FILTERS = "ldc.filters"
ENTRY_POINT_WRITERS = "ldc.writers"

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

REGISTRY = Registry(default_modules=DEFAULT_LDC_MODULES, env_modules=ENV_LDC_MODULES, enforce_uniqueness=True)

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


def available_downloaders() -> Dict[str, Plugin]:
    """
    Returns all available downloaders.

    :return: the dict of downloader objects
    :rtype: dict
    """
    return REGISTRY.plugins(ENTRY_POINT_DOWNLOADERS, Downloader)


def available_readers() -> Dict[str, Plugin]:
    """
    Returns all available readers.

    :return: the dict of reader objects
    :rtype: dict
    """
    return REGISTRY.plugins(ENTRY_POINT_READERS, Reader)


def available_writers() -> Dict[str, Plugin]:
    """
    Returns all available writers.

    :return: the dict of writer objects
    :rtype: dict
    """
    return REGISTRY.plugins(ENTRY_POINT_WRITERS, Writer)


def available_filters() -> Dict[str, Plugin]:
    """
    Returns all available filters.

    :return: the dict of filter objects
    :rtype: dict
    """
    return REGISTRY.plugins(ENTRY_POINT_FILTERS, Filter)


def available_plugins() -> Dict[str, Plugin]:
    """
    Returns all available plugins.

    :return: the dict of plugin objects
    :rtype: dict
    """
    result = dict()
    result.update(available_downloaders())
    result.update(available_readers())
    result.update(available_filters())
    result.update(available_writers())
    return result


def register_plugins(modules: List[str] = None):
    """
    Registers all plugins.

    :param modules: the list of modules to use instead of env variable or default modules
    :type modules: list
    """
    REGISTRY.custom_modules = modules
    available_plugins()
