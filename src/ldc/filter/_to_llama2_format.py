import argparse
from typing import List

from wai.logging import LOGGING_WARNING
from ldc.core import DOMAIN_PRETRAIN
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData
from ._core import Filter


class ToLlama2Format(Filter):
    """
    Turns pretrain records into llama2 format.
    https://github.com/facebookresearch/llama/blob/ef351e9cd9496c579bf9f2bb036ef11bdc5ca3d2/llama/generation.py#L320

    <s>[INST] <<SYS>>
    {{system message}}
    <</SYS>>
    {{message}} [/INST] {{answer}} </s>

    <s>[INST] {{message}} [/INST] {{answer}} </s>

    <s>[INST] {{message}} [/INST]

    Adding the [INST] and [/INST] tokens is optional.
    """

    def __init__(self, skip_tokens: bool = False, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param skip_tokens: whether to leave out the [INST] [/INST] tokens
        :type skip_tokens: bool
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.skip_tokens = skip_tokens

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "to-llama2-format"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Turns pretrain records into llama2 format. Based on: https://github.com/facebookresearch/llama/blob/ef351e9cd9496c579bf9f2bb036ef11bdc5ca3d2/llama/generation.py#L320"

    def domains(self) -> List[str]:
        """
        Returns the domains of the handler.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PRETRAIN]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PretrainData]

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
        parser.add_argument("--skip_tokens", action="store_true", help="Whether to leave out the [INST] [/INST] tokens", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.skip_tokens = ns.skip_tokens

    def _do_process(self, data: PretrainData):
        """
        Processes the data record.

        :param data: the record to process
        :type data: PairData
        :return: the potentially updated record(s)
        """
        if self.skip_tokens:
            content = "<s> %s" % data.content
        else:
            content = "<s>[INST] %s [/INST]" % data.content
        return PretrainData(content=content)
