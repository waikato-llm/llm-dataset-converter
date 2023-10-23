import argparse
from typing import List, Set

from ldc.core import LOGGING_WARN, DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION
from ldc.core import LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT, LOCATION_CONTENT, \
    LOCATIONS, LOCATIONS_PAIRS, LOCATIONS_PRETRAIN
from ._core import Filter, FILTER_ACTIONS, FILTER_ACTION_DISCARD, FILTER_ACTION_KEEP
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData
from ldc.translation import TranslationData


class Keyword(Filter):
    """
    Keeps or discards data records based on keyword(s).
    """

    def __init__(self, keywords: List[str] = None, action: str = FILTER_ACTION_KEEP,
                 location: str = LOCATION_ANY, languages: List[str] = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param keywords: the list of keywords to look for (lower case)
        :type keywords: list
        :param action: the action to perform
        :type action: str
        :param location: in which part of the data to look for the keywords
        :type location: str
        :param languages: the languages to restrict the keywords to, None to check all
        :type languages: list
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)

        if action not in FILTER_ACTIONS:
            raise Exception("Invalid action: %s" % action)
        if location not in LOCATIONS:
            raise Exception("Invalid location: %s" % location)

        self.keywords = keywords
        self.action = action
        self.location = location
        self.languages = languages
        self.kept = 0
        self.discarded = 0

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "keyword"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Keeps or discards data records based on keyword(s). Search is performed in lower-case."

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
        parser.add_argument("-k", "--keyword", type=str, help="The keywords to look for (lower case)", required=True, nargs="+")
        parser.add_argument("-L", "--location", choices=LOCATIONS, default=LOCATION_ANY, help="Where to look for the keywords; pairs: " + ",".join(
            LOCATIONS_PAIRS) + ", pretrain: " + ",".join(LOCATIONS_PRETRAIN) + ", translation: " + ",".join(
            LOCATIONS_PRETRAIN))
        parser.add_argument("-g", "--language", type=str, help="The languages to inspect; inspects all if not specified", required=False, nargs="*")
        parser.add_argument("-a", "--action", choices=FILTER_ACTIONS, default=FILTER_ACTION_KEEP, help="How to react when a keyword is encountered")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.keywords = ns.keyword[:]
        self.action = ns.action
        self.location = ns.location
        self.languages = ns.language

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if (self.keywords is None) or (len(self.keywords) == 0):
            raise Exception("No keywords provided!")
        self.keywords = [x.lower() for x in self.keywords]
        if self.languages is not None:
            self.languages = [x.lower() for x in self.languages]
        self.kept = 0
        self.discarded = 0

    def _to_words(self, data) -> Set[str]:
        """
        Turns the record into words.

        :return: the compiled set of words (lower case)
        :rtype: set
        """
        words = set()

        if isinstance(data, PairData):
            if self.location in [LOCATION_INSTRUCTION, LOCATION_ANY]:
                words.update(data.instruction.lower().split())
            if self.location in [LOCATION_INPUT, LOCATION_ANY]:
                words.update(data.input.lower().split())
            if self.location in [LOCATION_OUTPUT, LOCATION_ANY]:
                words.update(data.output.lower().split())
        elif isinstance(data, PretrainData):
            if self.location in [LOCATION_CONTENT, LOCATION_ANY]:
                words.update(data.content.lower().split())
        elif isinstance(data, TranslationData):
            if self.languages is None:
                for k in data.translations:
                    words.update(data.translations[k].lower().split())
            else:
                for lang in self.languages:
                    if lang in data.translations:
                        words.update(data.translations[lang].lower().split())
        else:
            raise Exception("Unhandled data type: %s" % str(type(data)))

        return words

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = data

        # prepare lookup
        words = self._to_words(data)

        # check for keywords
        found = False
        for keyword in self.keywords:
            if keyword in words:
                found = True
                break

        if self.action == FILTER_ACTION_KEEP:
            if not found:
                result = None
        elif self.action == FILTER_ACTION_DISCARD:
            if found:
                result = None
        else:
            raise Exception("Unhandled action: %s" % self.action)

        if result is None:
            self.discarded += 1
        else:
            self.kept += 1

        info = "keeping" if (result is not None) else "discarding"
        self.logger().debug("Keyword found, %s: %s" % (info, str(data)))

        return result

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self.logger().info("# kept: %d" % self.kept)
        self.logger().info("# discarded: %d" % self.discarded)
