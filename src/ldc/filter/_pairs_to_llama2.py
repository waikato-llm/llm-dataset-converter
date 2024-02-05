import argparse
from typing import List

from wai.logging import LOGGING_WARNING
from ldc.core import DOMAIN_PAIRS, DOMAIN_PRETRAIN
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData
from ._core import Filter


class PairsToLlama2(Filter):
    """
    Converts records of prompt/response pairs to llama2-formatted pretrain ones.

    <s>[INST] <<SYS>>
    {{system message}}
    <</SYS>>
    {{message}} [/INST] {{answer}} </s>

    <s>[INST] {{message}} [/INST] {{answer}} </s>

    <s>[INST] {{message}} [/INST]
    """

    def __init__(self, prefix: str = None, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param prefix: the prompt prefix to use, ignored if None or empty
        :type prefix: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.prefix = prefix

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "pairs-to-llama2"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Converts records of prompt/response pairs to llama2-formatted pretrain ones. " \
               + "The 'instruction' (ie prompt) gets wrapped in [INST]...[/INST] " \
               + "and the 'output' (ie response) follows that."

    def domains(self) -> List[str]:
        """
        Returns the domains of the handler.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PAIRS, DOMAIN_PRETRAIN]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PairData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PretrainData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-p", "--prefix", type=str, default=None, help="The prefix to use for the instruction.")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.prefix = ns.prefix

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.prefix is None:
            self.prefix = ""
        if len(self.prefix) > 0:
            if self.prefix[-1] != " ":
                self.prefix += " "

    def _do_process(self, data: PairData):
        """
        Processes the data record.

        :param data: the record to process
        :type data: PairData
        :return: the potentially updated record(s)
        """
        content = "<s> [INST] %s%s [/INST] %s </s>" % (self.prefix, data.instruction, data.output)
        return PretrainData(content=content)
