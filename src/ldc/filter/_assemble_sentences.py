import argparse
import copy
from typing import List

from ldc.core import LOGGING_WARN, DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION, DEFAULT_END_CHARS, DEFAULT_QUOTE_CHARS
from ldc.core import LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT, LOCATION_CONTENT, \
    LOCATIONS, LOCATIONS_PAIRS, LOCATIONS_PRETRAIN
from ._core import Filter
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData
from ldc.translation import TranslationData
from ldc.text_utils import assemble_preformatted, split_into_sentences, combine_sentences


class AssembleSentences(Filter):
    """
    For keeping sentences together, e.g., when reading preformatted text.
    """

    def __init__(self, end_chars: str = DEFAULT_END_CHARS, quote_chars: str = DEFAULT_QUOTE_CHARS,
                 max_sentences: int = 1, location: str = LOCATION_ANY, languages: List[str] = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param end_chars: the characters that signify the ending of a sentence
        :type end_chars: str
        :param quote_chars: the characters that represent quotes
        :type quote_chars: str
        :param max_sentences: the maximum number of sentences per line
        :type max_sentences: int
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

        self.end_chars = end_chars
        self.quote_chars = quote_chars
        self.max_sentences = max_sentences
        self.location = location
        self.languages = languages

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "assemble-sentences"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "For keeping sentences together, e.g., when reading preformatted text."

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
        parser.add_argument("-c", "--end_chars", type=str, help="The characters signifying the end of a sentence.", default=DEFAULT_END_CHARS, required=False)
        parser.add_argument("-q", "--quote_chars", type=str, help="The characters that represent quotes.", default=DEFAULT_QUOTE_CHARS, required=False)
        parser.add_argument("-m", "--max_sentences", type=int, help="The maximum number of sentences per line.", default=1, required=False)
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
        self.end_chars = ns.end_chars
        self.quote_chars = ns.quote_chars
        self.max_sentences = ns.max_sentences
        self.location = ns.location
        self.languages = ns.language

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.end_chars is None:
            self.end_chars = ""
        if self.quote_chars is None:
            self.quote_chars = ""
        if self.max_sentences < 1:
            raise Exception("At least one sentence per line is required, currently set: %d" % self.max_sentences)

        if self.languages is not None:
            self.languages = [x.lower() for x in self.languages]

    def _assemble_sentences(self, s: str) -> str:
        """
        Assembles lines into sentences, e.g., when processing preformatted text.

        :param s: the string to process (gets split into lines)
        :type s: str
        :return: the updated string
        :rtype: str
        """
        lines = s.split("\n")
        pre = len(lines)
        result = assemble_preformatted(lines, end_chars=self.end_chars, quote_chars=self.quote_chars)
        result = split_into_sentences(result, end_chars=self.end_chars)
        result = combine_sentences(result, max_sentences=self.max_sentences)
        post = len(result)
        self.logger().info("assembling sentences, #lines: %d -> %d" % (pre, post))
        return "\n".join(result)

    def _process(self, data):
        """
        Removes the blocks.

        :param data: the record to process
        """
        if isinstance(data, PairData):
            if self.location in [LOCATION_INSTRUCTION, LOCATION_ANY]:
                data.instruction = self._assemble_sentences(data.instruction)
            if self.location in [LOCATION_INPUT, LOCATION_ANY]:
                data.input = self._assemble_sentences(data.input)
            if self.location in [LOCATION_OUTPUT, LOCATION_ANY]:
                data.output = self._assemble_sentences(data.output)
        elif isinstance(data, PretrainData):
            if self.location in [LOCATION_CONTENT, LOCATION_ANY]:
                data.content = self._assemble_sentences(data.content)
        elif isinstance(data, TranslationData):
            if self.languages is None:
                for k in data.translations:
                    data.translations[k] = self._assemble_sentences(data.translations[k])
            else:
                for lang in self.languages:
                    if lang in data.translations:
                        data.translations[lang] = self._assemble_sentences(data.translations[lang])
        else:
            raise Exception("Unhandled data type: %s" % str(type(data)))

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = copy.deepcopy(data)
        self._process(result)

        return result
