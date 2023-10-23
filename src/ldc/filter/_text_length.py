import argparse
from typing import List

from ldc.core import LOGGING_WARN, DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION
from ldc.core import LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT, LOCATION_CONTENT, \
    LOCATIONS, LOCATIONS_PAIRS, LOCATIONS_PRETRAIN
from ._core import Filter
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData
from ldc.translation import TranslationData


class TextLength(Filter):
    """
    Keeps or discards data records based on text length constraints.
    """

    def __init__(self, min_length: int = None, max_length: int = None,
                 location: str = LOCATION_ANY, languages: List[str] = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param min_length: the minimum text length, ignored if None
        :type min_length: int
        :param max_length: the maximum text length, ignored if None
        :type max_length: int
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

        self.min_length = min_length
        self.max_length = max_length
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
        return "text-length"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Keeps or discards data records based on text length constraints."

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
        parser.add_argument("-m", "--min_length", type=int, help="The minimum text length, ignored if <0", default=-1, required=False)
        parser.add_argument("-M", "--max_length", type=int, help="The maximum text length, ignored if <0", default=-1, required=False)
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
        self.min_length = ns.min_length
        self.max_length = ns.max_length
        self.location = ns.location
        self.languages = ns.language

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()

        if (self.min_length is None) or (self.min_length < 0):
            self.min_length = -1
        if (self.max_length is None) or (self.max_length < 0):
            self.max_length = -1
        if (self.min_length > 0) and (self.max_length > 0) and (self.min_length > self.max_length):
            raise Exception("Minimum length can be at most the maximum length: min=%d, max=%d" % (self.min_length, self.max_length))

        if self.languages is not None:
            self.languages = [x.lower() for x in self.languages]

        self.kept = 0
        self.discarded = 0

    def _get_lengths(self, data) -> List[int]:
        """
        Turns the record into list of lengths.

        :return: the compiled list of lengths
        :rtype: list
        """
        lengths = list()

        if isinstance(data, PairData):
            if self.location in [LOCATION_INSTRUCTION, LOCATION_ANY]:
                lengths.append(len(data.instruction))
            if self.location in [LOCATION_INPUT, LOCATION_ANY]:
                lengths.append(len(data.input))
            if self.location in [LOCATION_OUTPUT, LOCATION_ANY]:
                lengths.append(len(data.output))
        elif isinstance(data, PretrainData):
            if self.location in [LOCATION_CONTENT, LOCATION_ANY]:
                lengths.append(len(data.content))
        elif isinstance(data, TranslationData):
            if self.languages is None:
                for k in data.translations:
                    lengths.append(len(data.translations[k]))
            else:
                for lang in self.languages:
                    if lang in data.translations:
                        lengths.append(len(data.translations[lang]))
                    else:
                        # missing language gets length 0
                        lengths.append(0)
        else:
            raise Exception("Unhandled data type: %s" % str(type(data)))

        return lengths

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = data

        # get lengths
        lengths = self._get_lengths(data)

        keep = True
        for length in lengths:
            if self.min_length > -1:
                if length < self.min_length:
                    keep = False
            if self.max_length > -1:
                if length > self.max_length:
                    keep = False
            if not keep:
                break

        if not keep:
            result = None
            self.logger().debug("Text length violated constraints (min=%d, max=%d): %s" % (self.min_length, self.max_length, str(data)))

        if result is None:
            self.discarded += 1
        else:
            self.kept += 1

        return result

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self.logger().info("# kept: %d" % self.kept)
        self.logger().info("# discarded: %d" % self.discarded)
