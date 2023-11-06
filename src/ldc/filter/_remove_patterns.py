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
from ldc.text_utils import remove_patterns


class RemovePatterns(Filter):
    """
    Removes substrings that match regular expressions patterns.
    """

    def __init__(self, expr_remove: List[str] = None,
                 location: str = LOCATION_ANY, languages: List[str] = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param expr_remove: the list of regexp for removing sub-strings from the text
        :type expr_remove: list
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

        self.expr_remove = expr_remove
        self.location = location
        self.languages = languages
        self.affected = 0

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "remove-patterns"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Removes substrings that match the supplied regular expression patterns."

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
        parser.add_argument("-r", "--expr_remove", type=str, default=None, help="Regular expressions for removing sub-strings from the text (gets applied before skipping empty lines); uses re.sub(...).", nargs="*")
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
        self.expr_remove = ns.expr_remove
        self.location = ns.location
        self.languages = ns.language

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.languages is not None:
            self.languages = [x.lower() for x in self.languages]
        self.affected = 0

    def _remove_patterns(self, line: str) -> Tuple[str, int]:
        """
        Removes all lines that match the patterns (inline).

        :param line: the line to process
        :type line: str
        :return: the processed lines
        :rtype: list
        """
        result, affected = remove_patterns(line.split("\n"), self.expr_remove)
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
            if self.location in [LOCATION_INSTRUCTION, LOCATION_ANY]:
                data.instruction, r = self._remove_patterns(data.instruction)
                removed += r
            if self.location in [LOCATION_INPUT, LOCATION_ANY]:
                data.input, r = self._remove_patterns(data.input)
                removed += r
            if self.location in [LOCATION_OUTPUT, LOCATION_ANY]:
                data.output, r = self._remove_patterns(data.output)
                removed += r
        elif isinstance(data, PretrainData):
            if self.location in [LOCATION_CONTENT, LOCATION_ANY]:
                data.content, r = self._remove_patterns(data.content)
                removed += r
        elif isinstance(data, TranslationData):
            if self.languages is None:
                for k in data.translations:
                    data.translations[k], r = self._remove_patterns(data.translations[k])
                    removed += r
            else:
                for lang in self.languages:
                    if lang in data.translations:
                        data.translations[lang], r = self._remove_patterns(data.translations[lang])
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
