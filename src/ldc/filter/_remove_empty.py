import argparse
import copy
from typing import List, Tuple

from ldc.core import LOGGING_WARN, DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION
from ldc.core import LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT, LOCATION_CONTENT, \
    LOCATIONS, LOCATIONS_PAIRS, LOCATIONS_PRETRAIN
from ._core import Filter
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData
from ldc.translation import TranslationData
from ldc.text_utils import remove_empty


class RemoveEmpty(Filter):
    """
    Removes empty lines.
    """

    def __init__(self, location: str = LOCATION_ANY, languages: List[str] = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

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

        if location not in LOCATIONS:
            raise Exception("Invalid location: %s" % location)

        self.location = location
        self.languages = languages
        self.removed = 0

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "remove-empty"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Removes empty lines."

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
        parser.add_argument("-L", "--location", choices=LOCATIONS, default=LOCATION_ANY, help="Where to look for the keywords; pairs: " + ",".join(
            LOCATIONS_PAIRS) + ", pretrain: " + ",".join(LOCATIONS_PRETRAIN) + ", translation: " + ",".join(
            LOCATIONS_PRETRAIN))
        parser.add_argument("-g", "--language", type=str, help="The languages to inspect; inspects all if not specified", required=False, nargs="*")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.location = ns.location
        self.languages = ns.language

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()

        if self.languages is not None:
            self.languages = [x.lower() for x in self.languages]
        self.removed = 0

    def _remove_empty(self, s: str) -> Tuple[str, int]:
        """
        Removes empty lines.

        :param s: the text to process
        :type s: str
        :return: the tuple of processed string and number of lines removed
        :rtype: tuple
        """
        lines = s.split("\n")
        pre = len(lines)
        lines = remove_empty(lines)
        post = len(lines)
        return "\n".join(lines), pre - post

    def _process(self, data) -> int:
        """
        Removes the blocks.

        :param data: the record to process
        :return: the number of lines that were removed
        :rtype: int
        """
        removed = 0
        if isinstance(data, PairData):
            if self.location in [LOCATION_INSTRUCTION, LOCATION_ANY]:
                data.instruction, r = self._remove_empty(data.instruction)
                removed += r
            if self.location in [LOCATION_INPUT, LOCATION_ANY]:
                data.input, r = self._remove_empty(data.input)
                removed += r
            if self.location in [LOCATION_OUTPUT, LOCATION_ANY]:
                data.output, r = self._remove_empty(data.output)
                removed += r
        elif isinstance(data, PretrainData):
            if self.location in [LOCATION_CONTENT, LOCATION_ANY]:
                data.content, r = self._remove_empty(data.content)
                removed += r
        elif isinstance(data, TranslationData):
            if self.languages is None:
                for k in data.translations:
                    data.translations[k], r = self._remove_empty(data.translations[k])
                    removed += r
            else:
                for lang in self.languages:
                    if lang in data.translations:
                        data.translations[lang], r = self._remove_empty(data.translations[lang])
                        removed += r
        else:
            raise Exception("Unhandled data type: %s" % str(type(data)))

        return removed

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = copy.deepcopy(data)
        removed = self._process(result)
        self.removed += removed

        self.logger().debug("removed # lines: %d" % removed)

        return result

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self.logger().info("total # lines removed: %d" % self.removed)
