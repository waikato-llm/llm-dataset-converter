import argparse
from typing import List

from ldc.core import DOMAIN_PAIRS, DOMAIN_PRETRAIN
from ldc.core import LOGGING_WARN
from ldc.filter import Filter
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData, PAIRDATA_FIELDS, PAIRDATA_INSTRUCTION, PAIRDATA_INPUT, PAIRDATA_OUTPUT


class PairsToPretrain(Filter):
    """
    Converts records of prompt/output pairs to pretrain ones.
    """

    def __init__(self, data_fields: List[str] = None, logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter.

        :param data_fields: the list of data fields to turn into pretrain content
        :type data_fields: list
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)

        if data_fields is not None:
            for data_field in data_fields:
                if data_field not in PAIRDATA_FIELDS:
                    raise Exception("Invalid data field: %s" % data_field)

        self.data_fields = data_fields

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "pairs-to-pretrain"

    def description(self) -> str:
        """
        Returns a description of the handler.

        :return: the description
        :rtype: str
        """
        return "Converts records of prompt/output pairs to pretrain ones."

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
        parser.add_argument("-f", "--data_fields", choices=PAIRDATA_FIELDS, default=None, help="The data fields to use for the pretrain content", nargs="+")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.data_fields = ns.data_fields[:]

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if (self.data_fields is None) or (len(self.data_fields) == 0):
            raise Exception("No data fields provided!")

    def _do_process(self, data: PairData):
        """
        Processes the data record.

        :param data: the record to process
        :type data: PairData
        :return: the potentially updated record or None if to drop
        """
        content = []
        for data_field in self.data_fields:
            if data_field == PAIRDATA_INSTRUCTION:
                content.append(data.instruction)
            elif data_field == PAIRDATA_INPUT:
                content.append(data.input)
            elif data_field == PAIRDATA_OUTPUT:
                content.append(data.output)
            else:
                raise Exception("Unhandled data field: %s" % data_field)

        return PretrainData(content=" ".join(content))
