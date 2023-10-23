import argparse
import re
from typing import List

from ldc.core import LOGGING_WARN, DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION
from ldc.core import LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT, LOCATION_CONTENT, \
    LOCATIONS, LOCATIONS_PAIRS, LOCATIONS_PRETRAIN
from ._core import Filter, FILTER_ACTIONS, FILTER_ACTION_DISCARD, FILTER_ACTION_KEEP
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData
from ldc.translation import TranslationData


class FindSubstring(Filter):
    """
    Keeps or discards data records based on presence of substrings.
    """

    def __init__(self, substrings: List[str] = None, is_regexp: bool = False,
                 action: str = FILTER_ACTION_KEEP,
                 location: str = LOCATION_ANY, languages: List[str] = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param substrings: the list of substrings to look for (lower case)
        :type substrings: list
        :param is_regexp: whether the substrings represent regular expressions
        :type is_regexp: bool
        :param action: the action to perform
        :type action: str
        :param location: in which part of the data to look for the substrings
        :type location: str
        :param languages: the languages to restrict the substrings to, None to check all
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

        self.substrings = substrings
        self.is_regexp = is_regexp
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
        return "find-substr"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Keeps or discards data records based on sub-string(s) text matching. Search is performed in lower-case. Optionally, the sub-strings can represent regular expressions used for searching the strings."

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
        parser.add_argument("-s", "--sub_string", type=str, help="The substrings to look for (lower case)", required=True, nargs="+")
        parser.add_argument("-r", "--is_regexp", action="store_true", help="Whether the sub-strings represent regular expressions", required=False)
        parser.add_argument("-L", "--location", choices=LOCATIONS, default=LOCATION_ANY, help="Where to look for the substrings; pairs: " + ",".join(
            LOCATIONS_PAIRS) + ", pretrain: " + ",".join(LOCATIONS_PRETRAIN) + ", translation: " + ",".join(
            LOCATIONS_PRETRAIN))
        parser.add_argument("-g", "--language", type=str, help="The languages to inspect; inspects all if not specified", required=False, nargs="*")
        parser.add_argument("-a", "--action", choices=FILTER_ACTIONS, default=FILTER_ACTION_KEEP, help="How to react when a substring is found")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.substrings = ns.sub_string[:]
        self.is_regexp = ns.is_regexp
        self.action = ns.action
        self.location = ns.location
        self.languages = ns.language

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if (self.substrings is None) or (len(self.substrings) == 0):
            raise Exception("No substrings provided!")
        if not self.is_regexp:
            self.substrings = [x.lower() for x in self.substrings]
        if self.languages is not None:
            self.languages = [x.lower() for x in self.languages]
        self.kept = 0
        self.discarded = 0

    def _to_strings(self, data) -> List[str]:
        """
        Turns the record into strings.

        :return: the compiled list of strings (lower case)
        :rtype: list
        """
        result = list()

        if isinstance(data, PairData):
            if self.location in [LOCATION_INSTRUCTION, LOCATION_ANY]:
                result.append(data.instruction.lower())
            if self.location in [LOCATION_INPUT, LOCATION_ANY]:
                result.append(data.input.lower())
            if self.location in [LOCATION_OUTPUT, LOCATION_ANY]:
                result.append(data.output.lower())
        elif isinstance(data, PretrainData):
            if self.location in [LOCATION_CONTENT, LOCATION_ANY]:
                result.append(data.content.lower())
        elif isinstance(data, TranslationData):
            if self.languages is None:
                for k in data.translations:
                    result.append(data.translations[k].lower())
            else:
                for lang in self.languages:
                    if lang in data.translations:
                        result.append(data.translations[lang].lower())
        else:
            raise Exception("Unhandled data type: %s" % str(type(data)))

        return result

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = data

        # prepare lookup
        strings = self._to_strings(data)

        # check for substrings
        found = False
        for s in strings:
            for sub in self.substrings:
                if self.is_regexp:
                    if re.search(sub, s) is not None:
                        found = True
                        break
                else:
                    if sub in s:
                        found = True
                        break
            if found:
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
        self.logger().debug("Substring found, %s: %s" % (info, str(data)))

        return result

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self.logger().info("# kept: %d" % self.kept)
        self.logger().info("# discarded: %d" % self.discarded)
