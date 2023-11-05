import argparse
import logging
import os
import traceback

from typing import Dict, List, Optional

from ldc.downloader import Downloader
from ldc.filter import Filter
from ldc.base_io import Reader, Writer
from seppl import Registry, Plugin, MODE_DYNAMIC, get_class_name

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
    "ldc.downloader",
    "ldc.filter",
    "ldc.pretrain",
    "ldc.supervised.pairs",
    "ldc.translation",
])

REGISTRY = Registry(mode=MODE_DYNAMIC, default_modules=DEFAULT_LDC_MODULES, env_modules=ENV_LDC_MODULES, enforce_uniqueness=True)

LLM_REGISTRY = "llm-registry"

_logger = None


LIST_PLUGINS = "plugins"
LIST_DOWNLOADERS = "downloaders"
LIST_READERS = "readers"
LIST_FILTERS = "filters"
LIST_WRITERS = "writers"
LIST_CUSTOM_MODULES = "custom-modules"
LIST_ENV_MODULES = "env-modules"
LIST_TYPES = [
    LIST_PLUGINS,
    LIST_CUSTOM_MODULES,
    LIST_ENV_MODULES,
    LIST_DOWNLOADERS,
    LIST_READERS,
    LIST_FILTERS,
    LIST_WRITERS,
]


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


def _list(list_type: str, custom_modules: Optional[List[str]] = None):
    """
    Lists various things on stdout.

    :param list_type: the type of list to generate
    :type list_type: str
    """
    register_plugins(modules=custom_modules)

    if list_type in [LIST_PLUGINS, LIST_DOWNLOADERS, LIST_READERS, LIST_FILTERS, LIST_WRITERS]:
        if list_type == LIST_PLUGINS:
            plugins = available_plugins()
        elif list_type == LIST_DOWNLOADERS:
            plugins = available_downloaders()
        elif list_type == LIST_READERS:
            plugins = available_readers()
        elif list_type == LIST_FILTERS:
            plugins = available_filters()
        elif list_type == LIST_WRITERS:
            plugins = available_readers()
        else:
            raise Exception("Unhandled type: %s" % list_type)
        print("name: class")
        for name in plugins:
            print("%s: %s" % (name, get_class_name(plugins[name])))
    elif list_type == LIST_CUSTOM_MODULES:
        modules = REGISTRY.custom_modules
        print("custom modules:")
        if modules is None:
            print("-none")
        else:
            for m in modules:
                print(m)
    elif list_type == LIST_ENV_MODULES:
        print("env modules:")
        if REGISTRY.env_modules is None:
            print("-none-")
        else:
            modules = os.getenv(REGISTRY.env_modules)
            if modules is None:
                print("-none listed in env var %s-" % REGISTRY.env_modules)
            else:
                modules = modules.split(",")
                for m in modules:
                    print(m)


def main(args=None):
    """
    The main method for parsing command-line arguments.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    parser = argparse.ArgumentParser(
        description="For inspecting/querying the registry.",
        prog=LLM_REGISTRY,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--custom_modules", type=str, default=None, help="The comma-separated list of custom modules to use.", required=False)
    parser.add_argument("-l", "--list", choices=LIST_TYPES, default=None, help="For outputting various lists on stdout.", required=False)
    parsed = parser.parse_args(args=args)

    custom_modules = None
    if parsed.custom_modules is not None:
        custom_modules = parsed.custom_modules.split(",")

    if parsed.list is not None:
        _list(parsed.list, custom_modules=custom_modules)


def sys_main() -> int:
    """
    Runs the main function using the system cli arguments, and
    returns a system error code.

    :return: 0 for success, 1 for failure.
    """
    try:
        main()
        return 0
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    main()
