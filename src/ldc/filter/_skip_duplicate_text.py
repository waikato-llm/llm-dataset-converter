import argparse
from typing import List

from ldc.core import DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION
from ldc.core import LOGGING_WARN
from ldc.core import LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT, LOCATION_CONTENT, \
    LOCATIONS, LOCATIONS_PAIRS, LOCATIONS_PRETRAIN
from ldc.filter import Filter
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData
from ldc.translation import TranslationData


class SkipDuplicateText(Filter):
    """
    Suppresses records with text that has already passed through.
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
        self._texts = set()
        self._num_texts_skipped = 0

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "skip-duplicate-text"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Suppresses records with text that has already passed through."

    def domains(self) -> List[str]:
        """
        Returns the domains of the handler.

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
        self._texts = set()
        self._num_texts_skipped = 0

    def _get_texts(self, data) -> List[str]:
        """
        Turns the record into list of texts.

        :return: the compiled list of texts (lower case)
        :rtype: list
        """
        words = list()

        if isinstance(data, PairData):
            if self.location in [LOCATION_INSTRUCTION, LOCATION_ANY]:
                words.append(data.instruction.lower())
            if self.location in [LOCATION_INPUT, LOCATION_ANY]:
                words.append(data.input.lower())
            if self.location in [LOCATION_OUTPUT, LOCATION_ANY]:
                words.append(data.output.lower())
        elif isinstance(data, PretrainData):
            if self.location in [LOCATION_CONTENT, LOCATION_ANY]:
                words.append(data.content.lower())
        elif isinstance(data, TranslationData):
            if self.languages is None:
                for k in data.translations:
                    words.append(data.translations[k].lower())
            else:
                for lang in self.languages:
                    if lang in data.translations:
                        words.append(data.translations[lang].lower())
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

        texts = self._get_texts(data)

        # already passed through?
        for t in texts:
            if t in self._texts:
                self._num_texts_skipped += 1
                result = None

        for t in texts:
            self._texts.add(t)

        return result

    def finalize(self):
        """
        Finishes the reading, e.g., for closing files or databases.
        """
        self.logger().info("# duplicate texts skipped: %d" % self._num_texts_skipped)
