import argparse
import json
import statistics
import sys
import yaml

from dataclasses import dataclass, field
from typing import List, Dict

from ldc.core import LOGGING_WARN, DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION
from ldc.core import LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT, LOCATION_CONTENT, \
    LOCATIONS, LOCATIONS_PAIRS, LOCATIONS_PRETRAIN
from ._core import Filter
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData
from ldc.translation import TranslationData


@dataclass
class Statistics:
    """
    For storing statistics.
    """
    count: int = 0
    min_len: int = sys.maxsize * 2 + 1
    max_len: int = 0
    lengths: Dict[int, int] = field(default_factory=dict)
    stats: Dict[str, 'Statistics'] = None  # nested stats
    stats_name: str = "stats"

    def to_dict(self, incl_lengths: bool = False) -> Dict:
        """
        Returns the data as a dictionary.

        :param incl_lengths: whether to output the counts per string length as well
        :type incl_lengths: bool
        :return: the current data
        :rtype: dict
        """
        result = dict()
        result["count"] = self.count
        if incl_lengths:
            result["lengths"] = self.lengths.copy()
        result["min"] = self.min_len
        result["max"] = self.max_len
        lengths = self.lengths.values()
        if len(lengths) > 1:
            result["mean"] = statistics.mean(lengths)
            result["stdev"] = statistics.stdev(lengths)
            result["median"] = statistics.median(lengths)
        if self.stats is not None:
            result[self.stats_name] = dict()
            for k in self.stats:
                result[self.stats_name][k] = self.stats[k].to_dict(incl_lengths=incl_lengths)
        return result


class TextStatistics(Filter):
    """
    Computes basic statics from the textual data passing through.
    """

    def __init__(self, output: str = None, detailed: bool = False, location: str = LOCATION_ANY, languages: List[str] = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param output: the json file to store the statistics in
        :type output: str
        :param detailed: whether to output detailed stats
        :type detailed: bool
        :param location: in which part of the data to look for the text
        :type location: str
        :param languages: the languages to restrict the check to, None to check all
        :type languages: list
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)

        if location not in LOCATIONS:
            raise Exception("Invalid location: %s" % location)

        self.output = output
        self.detailed = detailed
        self.location = location
        self.languages = languages
        self._stats: Dict[str, Statistics] = dict()

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "text-stats"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Computes basic statics from the textual data passing through."

    def domains(self) -> List[str]:
        """
        Returns the domains of the filter.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PairData, PretrainData, TranslationData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PairData, PretrainData, TranslationData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="The JSON file to store the statistics in; outputs a textual representation on stdout when missing", required=False, default=None)
        parser.add_argument("-d", "--detailed", action="store_true", help="Whether to output more detailed statistics, e.g., the counts per string length", required=False)
        parser.add_argument("-L", "--location", choices=LOCATIONS, default=LOCATION_ANY, help="Where to look for the text; pairs: " + ",".join(LOCATIONS_PAIRS) + ", pretrain: " + ",".join(LOCATIONS_PRETRAIN) + ", translation: " + ",".join(LOCATIONS_PRETRAIN))
        parser.add_argument("-g", "--language", type=str, help="The languages to inspect; inspects all if not specified", required=False, nargs="*")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.output = ns.output
        self.detailed = ns.detailed
        self.location = ns.location
        self.languages = ns.language

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.languages is not None:
            self.languages = [x.lower() for x in self.languages]
        self._stats = dict()

    def _update_container(self, stats: statistics, s: str):
        """
        Updates the stats container.

        :param stats: the container to update
        :type stats: Statistics
        :param s: the string to use for the update
        :type s: str
        """
        stats.count += 1
        len_s = len(s)
        stats.min_len = min(stats.min_len, len_s)
        stats.max_len = max(stats.max_len, len_s)
        if len_s not in stats.lengths:
            stats.lengths[len_s] = 0
        stats.lengths[len_s] += 1

    def _update(self, domain: str, location: str, language: str, s: str):
        """
        Updates the stats for the given string.

        :param domain: the domain this string belongs to
        :type domain: str
        :param location: the location where the string was taken from
        :type location: str
        :param language: the language this string was taken from (if applicable)
        :type language: str
        :param s: the string to use for the update
        :type s: str
        """
        if domain not in [DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION]:
            raise Exception("Unhandled domain: %s" % domain)

        # per domain
        if domain not in self._stats:
            self._stats[domain] = Statistics()
        self._update_container(self._stats[domain], s)

        # per language
        if len(language) > 0:
            if self._stats[domain].stats is None:
                self._stats[domain].stats = dict()
                self._stats[domain].stats_name = "languages"
            if language not in self._stats[domain].stats:
                self._stats[domain].stats[language] = Statistics()
            self._update_container(self._stats[domain].stats[language], s)

        # per location
        if domain == DOMAIN_PAIRS:
            if self._stats[domain].stats is None:
                self._stats[domain].stats = dict()
            self._stats[domain].stats_name = "locations"
            if location not in self._stats[domain].stats:
                self._stats[domain].stats[location] = Statistics()
            self._update_container(self._stats[domain].stats[location], s)

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        if isinstance(data, PairData):
            if self.location in [LOCATION_INSTRUCTION, LOCATION_ANY]:
                self._update(DOMAIN_PAIRS, LOCATION_INSTRUCTION, "", data.instruction)
            if self.location in [LOCATION_INPUT, LOCATION_ANY]:
                self._update(DOMAIN_PAIRS, LOCATION_INPUT, "", data.input)
            if self.location in [LOCATION_OUTPUT, LOCATION_ANY]:
                self._update(DOMAIN_PAIRS, LOCATION_OUTPUT, "", data.output)
        elif isinstance(data, PretrainData):
            if self.location in [LOCATION_CONTENT, LOCATION_ANY]:
                self._update(DOMAIN_PRETRAIN, LOCATION_CONTENT, "", data.content)
        elif isinstance(data, TranslationData):
            if self.languages is None:
                for k in data.translations:
                    self._update(DOMAIN_TRANSLATION, "", k, data.translations[k])
            else:
                for lang in self.languages:
                    if lang in data.translations:
                        self._update(DOMAIN_TRANSLATION, "", lang, data.translations[lang])
        else:
            raise Exception("Unhandled data type: %s" % str(type(data)))

        return data

    def _output_stats(self):
        """
        Outputs the statistics.
        """
        stats = dict()
        for k in self._stats:
            stats[k] = self._stats[k].to_dict(incl_lengths=self.detailed)

        if self.output is None:
            print(yaml.dump(stats))
        else:
            self.logger().info("Writing stats to: %s" % self.output)
            with open(self.output, "w") as fp:
                json.dump(stats, fp, indent=2)

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self._output_stats()
