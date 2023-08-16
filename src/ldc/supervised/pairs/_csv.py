import argparse
import csv
import os
from typing import Iterable, List, Union

from ._core import PairData, PairReader, BatchPairWriter
from ldc.io import locate_files, open_file, generate_output


class CsvPairsReader(PairReader):
    """
    Reader for CSV files.
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
        self._current_reader = None
        self.col_instruction = "instruction"
        self.col_input = "input"
        self.col_output = "output"

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "from-csv-pairs"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Reads prompt/output pairs in CSV format."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help="Path to the CSV file(s) to read; global syntax is supported", required=True, nargs="+")
        parser.add_argument("--col_instruction", metavar="COL", type=str, default=None, help="The name of the column with the instructions", required=False)
        parser.add_argument("--col_input", metavar="COL", type=str, default=None, help="The name of the column with the inputs", required=False)
        parser.add_argument("--col_output", metavar="COL", type=str, default=None, help="The name of the column with the outputs", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.source = ns.input
        self.col_instruction = ns.col_instruction
        self.col_input = ns.col_input
        self.col_output = ns.col_output

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, fail_if_empty=True)

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
        self._current_input = open_file(self._current_input, mode="rt")
        self._current_reader = csv.DictReader(self._current_input)
        self.session.input_changed = True

        for row in self._current_reader:
            yield PairData(
                instruction=row[self.col_instruction],
                input=row[self.col_input],
                output=row[self.col_output],
            )

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
            self._current_reader = None
            self._current_input.close()
            self._current_input = None


class CsvPairsWriter(BatchPairWriter):
    """
    Writer for CSV files.
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
        self.col_instruction = "instruction"
        self.col_input = "input"
        self.col_output = "output"
        self._output = None
        self._output_writer = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "to-csv-pairs"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Writes prompt/output pairs in CSV format."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="Path of the CSV file to write (directory when processing multiple files)", required=True)
        parser.add_argument("--col_instruction", metavar="COL", type=str, default="instruction", help="The name of the column for the instructions", required=False)
        parser.add_argument("--col_input", metavar="COL", type=str, default="input", help="The name of the column for the inputs", required=False)
        parser.add_argument("--col_output", metavar="COL", type=str, default="output", help="The name of the column for the outputs", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.target = ns.output
        self.col_instruction = ns.col_instruction
        self.col_input = ns.col_input
        self.col_output = ns.col_output

    def write_batch(self, data: Iterable[PairData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of PairData
        :type data: Iterable
        """
        if self.session.input_changed:
            self.finalize()
            output = generate_output(self.session.current_input, self.target, ".csv", self.session.options.compression)
            if self.verbose:
                self.logger().info("Writing to: " + output)
            self._output = open_file(output, mode="wt")
            self._output_writer = csv.writer(self._output)
            self._output_writer.writerow([self.col_instruction, self.col_input, self.col_output])

        for item in data:
            row = [item.instruction, item.input, item.output]
            self._output_writer.writerow(row)

    def finalize(self):
        """
        Finishes the writing, e.g., for closing files or databases.
        """
        if self._output is not None:
            super().finalize()
            self._output_writer = None
            self._output.close()
            self._output = None
