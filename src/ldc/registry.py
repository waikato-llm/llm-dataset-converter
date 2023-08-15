from typing import Dict

from ldc.core import CommandlineHandler
from ldc.io import Reader, Writer
from ldc.filter import Filter
from ldc.supervised.pairs import AlpacaReader, AlpacaWriter, Keyword


def _add_to_dict(d: Dict[str, CommandlineHandler], h: CommandlineHandler):
    """
    Adds the plugin to the dictionary under its name.
    Raises an exception if plugin name already present.

    :param d: the dictionary to extend
    :type d: dict
    :param h: the plugin to add
    :type h: CommandlineHandler
    """
    if h.name() in d:
        raise Exception("Duplicate plugin name encountered: %s" % h.name())
    d[h.name()] = h


def available_readers() -> Dict[str, Reader]:
    """
    Returns all available readers.

    :return: the dict of reader objects
    :rtype: dict
    """
    result = dict()
    _add_to_dict(result, AlpacaReader())
    return result


def available_writers() -> Dict[str, Writer]:
    """
    Returns all available writers.

    :return: the dict of writer objects
    :rtype: dict
    """
    result = dict()
    _add_to_dict(result, AlpacaWriter())
    return result


def available_filters() -> Dict[str, Filter]:
    """
    Returns all available filters.

    :return: the dict of filter objects
    :rtype: dict
    """
    result = dict()
    _add_to_dict(result, Keyword())
    return result


def available_plugins() -> Dict[str, CommandlineHandler]:
    """
    Returns all available plugins.

    :return: the dict of plugin objects
    :rtype: dict
    """
    result = dict()
    result.update(available_readers())
    result.update(available_filters())
    result.update(available_writers())
    return result
