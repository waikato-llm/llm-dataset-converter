import argparse

from typing import List

from ldc.core import LOGGING_WARN
from ._core import TranslationData, TranslationFilter


class RequireLanguages(TranslationFilter):
    """
    Discards records if the required languages aren't present.
    """

    def __init__(self, languages: List[str] = None, logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param languages: the languages to enforce presence
        :type languages: list
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.languages = languages
        self.kept = 0
        self.discarded = 0

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "require-languages"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Discards records if the required languages aren't present."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-g", "--language", type=str, help="The languages to inspect; inspects all if not specified", required=True, nargs="+")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.languages = ns.language

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.languages is None:
            raise Exception("At least one language must be specified!")
        self.languages = [x.lower() for x in self.languages]
        self.kept = 0
        self.discarded = 0

    def _do_process(self, data: TranslationData):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        keep = True
        for lang in self.languages:
            if lang not in data.translations:
                keep = False
                break

        if keep:
            self.kept += 1
            return data
        else:
            self.discarded += 1
            return None

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self.logger().info("# kept: %d" % self.kept)
        self.logger().info("# discarded: %d" % self.discarded)
