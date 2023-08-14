import argparse
import io
import json

from typing import Iterable
from ._core import PairData, PairReader, BatchPairWriter


class AlpacaReader(PairReader):
    """
    Reader for the Alpaca JSON format.
    """

    def __init__(self, source=None, verbose=False):
        """
        Initializes the reader.

        :param source: the filename or file like object
        :param verbose: whether to be more verbose in the output
        :type verbose: bool
        """
        super().__init__(verbose=verbose)
        self.source = source
        self._input = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "from-alpaca"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Reads prompt/output pairs in Alpaca-like JSON format."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help="Path to the Alpaca file to read", required=True)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.source = ns.input

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        if isinstance(self.source, str):
            self._input = open(self.source, "r")
        elif isinstance(self.source, io.IOBase):
            self._input = self.source
        else:
            raise Exception("Invalid source, must be filename or file-like object!")
        if self.verbose:
            self.logger().info("Reading from: " + self.source)

    def read(self) -> Iterable[PairData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: PairData
        """
        array = json.load(self._input)
        for item in array:
            yield PairData.parse(item)

    def finalize(self):
        """
        Finishes the reading, e.g., for closing files or databases.
        """
        if self._input is not None:
            self._input.close()


class AlpacaWriter(BatchPairWriter):
    """
    Writer for the Alpaca JSON format.
    """

    def __init__(self, target=None, verbose=False):
        """
        Initializes the writer.

        :param target: the filename or file like object to write to
        :param verbose: whether to be more verbose in the output
        :type verbose: bool
        """
        super().__init__(verbose=verbose)
        self.target = target
        self._output = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "to-alpaca"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Writes prompt/output pairs in Alpaca-like JSON format."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="Path to the Alpaca file to write", required=True)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.target = ns.output

    def initialize(self):
        """
        Initializes the writing, e.g., for opening files or databases.
        """
        self._output = open(self.target, "w")
        if self.verbose:
            self.logger().info("Writing to: " + self.target)

    def finalize(self):
        """
        Finishes the writing, e.g., for closing files or databases.
        """
        if self._output is not None:
            self._output.close()

    def write_batch(self, data: Iterable[PairData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of PairData
        :type data: Iterable
        """
        json.dump([x.to_dict() for x in data], self._output)
