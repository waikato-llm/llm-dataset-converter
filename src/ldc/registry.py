from typing import Dict

from ldc.core import CommandlineHandler
from ldc.io import Reader, Writer
from ldc.filter import Filter
from ldc.filter import PairsToPretrain
from ldc.supervised.pairs import AlpacaReader, AlpacaWriter
from ldc.supervised.pairs import CsvPairsReader, CsvPairsWriter
from ldc.supervised.pairs import JsonLinesReader, JsonLinesWriter
from ldc.supervised.pairs import ParquetPairsReader, ParquetPairsWriter
from ldc.supervised.pairs import Keyword as KeywordPairs
from ldc.pretrain import ParquetPretrainReader, ParquetPretrainWriter


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
    _add_to_dict(result, CsvPairsReader())
    _add_to_dict(result, JsonLinesReader())
    _add_to_dict(result, ParquetPairsReader())
    _add_to_dict(result, ParquetPretrainReader())
    return result


def available_writers() -> Dict[str, Writer]:
    """
    Returns all available writers.

    :return: the dict of writer objects
    :rtype: dict
    """
    result = dict()
    _add_to_dict(result, AlpacaWriter())
    _add_to_dict(result, CsvPairsWriter())
    _add_to_dict(result, JsonLinesWriter())
    _add_to_dict(result, ParquetPairsWriter())
    _add_to_dict(result, ParquetPretrainWriter())
    return result


def available_filters() -> Dict[str, Filter]:
    """
    Returns all available filters.

    :return: the dict of filter objects
    :rtype: dict
    """
    result = dict()
    _add_to_dict(result, KeywordPairs())
    _add_to_dict(result, PairsToPretrain())
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
