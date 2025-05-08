import argparse
import copy
from typing import List, Tuple, Union

from wai.logging import LOGGING_WARNING
from ldc.core import DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION, DOMAIN_CLASSIFICATION
from ldc.core import LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT, LOCATION_CONTENT, \
    LOCATION_TEXT, LOCATIONS, locations_match, add_location_argument
from ldc.api.pretrain import PretrainData
from ldc.api.supervised.classification import ClassificationData
from ldc.api.supervised.pairs import PairData
from ldc.api.translation import TranslationData
from ldc.text_utils import strip_strings
from ldc.api import Filter


class StripStrings(Filter):
    """
    Strips whitespaces from start/end of strings.
    """

    def __init__(self, location: Union[str, List[str]] = LOCATION_ANY, languages: List[str] = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param location: in which part of the data to look for the keywords
        :type location: str or list
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
        self.affected = 0

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "strip-strings"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Strips whitespaces from start/end of strings."

    def domains(self) -> List[str]:
        """
        Returns the domains of the filter.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION, DOMAIN_CLASSIFICATION]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PairData, PretrainData, TranslationData, ClassificationData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PairData, PretrainData, TranslationData, ClassificationData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        add_location_argument(parser, "Which strings to strip")
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
        if isinstance(self.location, str):
            self.location = [self.location]
        self.affected = 0

    def _strip_strings(self, line: str) -> Tuple[str, int]:
        """
        Strips whitespaces from the strings.

        :param line: the line to process
        :type line: str
        :return: the processed lines
        :rtype: list
        """
        result, affected = strip_strings(line.split("\n"))
        return "\n".join(result), affected

    def _process(self, data) -> int:
        """
        Removes the blocks.

        :param data: the record to process
        :return: the number of lines that were removed
        :rtype: int
        """
        removed = 0
        if isinstance(data, PairData):
            if locations_match(self.location, LOCATION_INSTRUCTION):
                data.instruction, r = self._strip_strings(data.instruction)
                removed += r
            if locations_match(self.location, LOCATION_INPUT):
                data.input, r = self._strip_strings(data.input)
                removed += r
            if locations_match(self.location, LOCATION_OUTPUT):
                data.output, r = self._strip_strings(data.output)
                removed += r
        elif isinstance(data, ClassificationData):
            if locations_match(self.location, LOCATION_TEXT):
                data.text, r = self._strip_strings(data.text)
                removed += r
        elif isinstance(data, PretrainData):
            if locations_match(self.location, LOCATION_CONTENT):
                data.content, r = self._strip_strings(data.content)
                removed += r
        elif isinstance(data, TranslationData):
            if self.languages is None:
                for k in data.translations:
                    data.translations[k], r = self._strip_strings(data.translations[k])
                    removed += r
            else:
                for lang in self.languages:
                    if lang in data.translations:
                        data.translations[lang], r = self._strip_strings(data.translations[lang])
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
        affected = self._process(result)
        self.affected += affected

        self.logger().debug("affected # lines: %d" % affected)

        return result

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self.logger().info("total # lines affected: %d" % self.affected)
