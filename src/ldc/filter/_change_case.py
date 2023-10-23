import argparse
from typing import List

from ldc.core import LOGGING_WARN, DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION
from ldc.core import LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT, LOCATION_CONTENT, \
    LOCATIONS, LOCATIONS_PAIRS, LOCATIONS_PRETRAIN
from ._core import Filter
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData
from ldc.translation import TranslationData

CASE_UNCHANGED = "unchanged"
CASE_LOWER = "lower"
CASE_UPPER = "upper"
CASE_TITLE = "title"
CASES = [
    CASE_UNCHANGED,
    CASE_LOWER,
    CASE_UPPER,
    CASE_TITLE,
]


class ChangeCase(Filter):
    """
    Keeps or discards data records based on keyword(s).
    """

    def __init__(self, keywords: List[str] = None, case: str = CASE_UNCHANGED,
                 location: str = LOCATION_ANY, languages: List[str] = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param keywords: the list of keywords to look for (lower case)
        :type keywords: list
        :param case: the case to use
        :type case: str
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

        if case not in CASES:
            raise Exception("Invalid case: %s" % case)
        if location not in LOCATIONS:
            raise Exception("Invalid location: %s" % location)

        self.keywords = keywords
        self.case = case
        self.location = location
        self.languages = languages

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "change-case"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Changes the case of text, e.g., to all lower case."

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
        parser.add_argument("-c", "--case", choices=CASES, default=CASE_LOWER, help="How to change the case of the text")
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
        self.case = ns.case
        self.location = ns.location
        self.languages = ns.language

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.languages is not None:
            self.languages = [x.lower() for x in self.languages]

    def _change_case(self, s: str) -> str:
        """
        Changes the case of the string.

        :param s: the string to process
        :type s: str
        :return: the processed string
        :rtype: str
        """
        if self.case == CASE_UNCHANGED:
            return s
        elif self.case == CASE_LOWER:
            return s.lower()
        elif self.case == CASE_UPPER:
            return s.upper()
        elif self.case == CASE_TITLE:
            return s.title()
        else:
            raise Exception("Unhandled case: %s" % self.case)

    def _update(self, data):
        """
        Changes the case in the relevant strings of the record (in-place updates).

        :param data: the record to update
        """
        if isinstance(data, PairData):
            if self.location in [LOCATION_INSTRUCTION, LOCATION_ANY]:
                data.instruction = self._change_case(data.instruction)
            if self.location in [LOCATION_INPUT, LOCATION_ANY]:
                data.input = self._change_case(data.input)
            if self.location in [LOCATION_OUTPUT, LOCATION_ANY]:
                data.output = self._change_case(data.output)
        elif isinstance(data, PretrainData):
            if self.location in [LOCATION_CONTENT, LOCATION_ANY]:
                data.content = self._change_case(data.content)
        elif isinstance(data, TranslationData):
            if self.languages is None:
                for k in data.translations:
                    data.translations[k] = self._change_case(data.translations[k])
            else:
                for lang in self.languages:
                    if lang in data.translations:
                        data.translations[lang] = self._change_case(data.translations[lang])
        else:
            raise Exception("Unhandled data type: %s" % str(type(data)))

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        return self._update(data.copy())
