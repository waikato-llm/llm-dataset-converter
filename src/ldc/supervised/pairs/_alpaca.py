import argparse
import json
import os
from typing import Iterable, List, Union

from ._core import PairData, PairReader, BatchPairWriter
from ldc.io import locate_files, open_file, generate_output


class AlpacaReader(PairReader):
    """
    Reader for the Alpaca JSON format.
    """

    def __init__(self, source: Union[str, List[str]] = None, verbose: bool = False):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param verbose: whether to be more verbose in the output
        :type verbose: bool
        """
        super().__init__(verbose=verbose)
        self.source = source
        self._inputs = None
        self._current_input = None

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
        parser.add_argument("-i", "--input", type=str, help="Path to the Alpaca file(s) to read; global syntax is supported", required=True, nargs="+")
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
        super().initialize()
        self._inputs = locate_files(self.source)

    def read(self) -> Iterable[PairData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: PairData
        """
        self.finalize()

        self._current_input = self._inputs.pop(0)
        self.session.current_input = self._current_input
        if self.verbose:
            self.logger().info("Reading from: " + str(self.session.current_input))
        self._current_input = open_file(self._current_input)
        self.session.input_changed = True

        array = json.load(self._current_input)
        for item in array:
            yield PairData.parse(item)

    def has_finished(self) -> bool:
        """
        Returns whether reading has finished.

        :return: True if finished
        :rtype: bool
        """
        return (len(self._inputs) == 0) and (self._current_input is None)

    def finalize(self):
        """
        Finishes the reading, e.g., for closing files or databases.
        """
        if self._current_input is not None:
            super().finalize()
            self._current_input.close()
            self._current_input = None


class AlpacaWriter(BatchPairWriter):
    """
    Writer for the Alpaca JSON format.
    """

    def __init__(self, target: str = None, verbose: bool = False):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
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
        parser.add_argument("-o", "--output", type=str, help="Path of the Alpaca file to write (directory when processing multiple files)", required=True)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.target = ns.output

    def write_batch(self, data: Iterable[PairData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of PairData
        :type data: Iterable
        """
        if self.session.input_changed:
            self.finalize()
            if os.path.isdir(self.target):
                output = generate_output(self.session.current_input, self.target, ".json")
            else:
                output = self.target
            if self.verbose:
                self.logger().info("Writing to: " + output)
            self._output = open(output, "w")

        json.dump([x.to_dict() for x in data], self._output)

    def finalize(self):
        """
        Finishes the writing, e.g., for closing files or databases.
        """
        if self._output is not None:
            super().finalize()
            self._output.close()
            self._output = None
