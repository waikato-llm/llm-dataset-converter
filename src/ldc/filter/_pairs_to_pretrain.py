import argparse
from typing import List

from ldc.filter._core import Filter
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData

DATA_FIELD_INSTRUCTION = "instruction"
DATA_FIELD_INPUT = "input"
DATA_FIELD_OUTPUT = "output"
DATA_FIELDS = [DATA_FIELD_INSTRUCTION, DATA_FIELD_INPUT, DATA_FIELD_OUTPUT]


class PairsToPretrain(Filter):
    """
    Converts the data from prompt pairs to pretrain data.
    """

    def __init__(self, data_fields: List[str] = None, verbose: bool = False):
        """
        Initializes the filter.

        :param data_fields: the list of data fields to turn into pretrain content
        :type data_fields: list
        :param verbose: whether to be more verbose in the output
        :type verbose: bool
        """
        super().__init__(verbose=verbose)

        if data_fields is not None:
            for data_field in data_fields:
                if data_field not in DATA_FIELDS:
                    raise Exception("Invalid data field: %s" % data_field)

        self.data_fields = data_fields

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "pairs-to-pretrain"

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

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Converts the data from prompt pairs to pretrain data."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-f", "--data_fields", choices=DATA_FIELDS, default=None, help="The data fields to use for the pretrain content", nargs="+")
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
        if (self.data_fields is None) or (len(self.data_fields) == 0):
            raise Exception("No data fields provided!")

    def process(self, data: PairData):
        """
        Processes the data record.

        :param data: the record to process
        :type data: PairData
        :return: the potentially updated record or None if to drop
        """
        content = []
        for data_field in self.data_fields:
            if data_field == DATA_FIELD_INSTRUCTION:
                content.append(data.instruction)
            elif data_field == DATA_FIELD_INPUT:
                content.append(data.input)
            elif data_field == DATA_FIELD_OUTPUT:
                content.append(data.output)
            else:
                raise Exception("Unhandled data field: %s" % data_field)

        return PretrainData(content=" ".join(content))
