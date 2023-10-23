import argparse
from typing import List

from ldc.core import DOMAIN_TRANSLATION, DOMAIN_PAIRS
from ldc.core import LOGGING_WARN
from ldc.filter import Filter
from ldc.supervised.pairs import PairData
from ldc.translation import TranslationData


class TranslationToPairs(Filter):
    """
    Converts records of translation records to pair ones.
    """

    def __init__(self, lang_instruction: str = None, lang_input: str = None, lang_output: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param lang_instruction: the ID of the language to use as instruction
        :type lang_instruction: str
        :param lang_input: the ID of the language to use as input (optional)
        :type lang_input: str
        :param lang_output: the ID of the language to use as output
        :type lang_output: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.lang_instruction = lang_instruction
        self.lang_input = lang_input
        self.lang_output = lang_output

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "translation-to-pairs"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Converts records of translation data to pair ones, using specific languages for instruction, input (optional) and output."

    def domains(self) -> List[str]:
        """
        Returns the domains of the handler.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_TRANSLATION, DOMAIN_PAIRS]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [TranslationData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PairData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("--lang_instruction", type=str, default=None, help="The ID of the language to use for the instruction")
        parser.add_argument("--lang_input", type=str, default=None, help="The ID of the language to use for the input (optional)")
        parser.add_argument("--lang_output", type=str, default=None, help="The ID of the language to use for the output")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.lang_instruction = ns.lang_instruction
        self.lang_input = ns.lang_input
        self.lang_output = ns.lang_output

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.lang_instruction is None:
            raise Exception("No language ID specified for instructions!")
        if self.lang_output is None:
            raise Exception("No language ID specified for outputs!")

    def _do_process(self, data: TranslationData):
        """
        Processes the data record.

        :param data: the record to process
        :type data: PairData
        :return: the potentially updated record or None if to drop
        """
        instruction = None
        input_ = None
        output = None
        if self.lang_instruction in data.translations:
            instruction = data.translations[self.lang_instruction]
        if self.lang_input in data.translations:
            input_ = data.translations[self.lang_input]
        if self.lang_output in data.translations:
            output = data.translations[self.lang_output]
        if (instruction is None) or (output is None):
            return None
        else:
            return PairData(
                instruction=instruction,
                input=input_,
                output=output,
            )
