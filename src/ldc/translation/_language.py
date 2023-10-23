import argparse
from typing import List

from ldc.core import LOGGING_WARN
from ._core import TranslationFilter
from ldc.translation import TranslationData

KEYWORD_ACTION_KEEP = "keep"
KEYWORD_ACTION_DISCARD = "discard"
KEYWORD_ACTIONS = [KEYWORD_ACTION_KEEP, KEYWORD_ACTION_DISCARD]


class Language(TranslationFilter):
    """
    Keeps or discards languages.
    """

    def __init__(self, languages: List[str] = None, action: str = KEYWORD_ACTION_KEEP,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param languages: the list of languages to look for (lower case)
        :type languages: list
        :param action: the action to perform
        :type action: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)

        if action not in KEYWORD_ACTIONS:
            raise Exception("Invalid action: %s" % action)

        self.languages = languages
        self.action = action
        self.kept = 0
        self.discarded = 0

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "language"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Keeps or discards languages."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-g", "--language", type=str, help="The languages to look for", required=True, nargs="+")
        parser.add_argument("-a", "--action", choices=KEYWORD_ACTIONS, default=KEYWORD_ACTION_KEEP, help="How to react when a language is encountered")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.languages = ns.language[:]
        self.action = ns.action

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if (self.languages is None) or (len(self.languages) == 0):
            raise Exception("No languages provided!")
        self.languages = [x.lower() for x in self.languages]
        self.discarded = 0

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        translations = dict()

        # check for languages
        langs = set(self.languages)
        for lang in data.translations.keys():
            if lang in langs:
                if self.action == KEYWORD_ACTION_KEEP:
                    translations[lang] = data.translations[lang]
                elif self.action == KEYWORD_ACTION_DISCARD:
                    self.discarded += 1
            else:
                self.discarded += 1

        if len(translations) == 0:
            return None
        else:
            return TranslationData(translations=translations, meta=data.meta)

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self.logger().info("# discarded: %d" % self.discarded)
