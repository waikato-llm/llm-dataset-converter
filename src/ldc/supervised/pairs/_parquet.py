import argparse
import os
from typing import Iterable, List, Union

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from ldc.io import locate_files, generate_output
from ._core import PairData, PairReader, BatchPairWriter


class ParquetPairsReader(PairReader):
    """
    Reader for Parquet database files.
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
        self._current_table = None
        self.col_instruction = "instruction"
        self.col_input = "input"
        self.col_output = "output"

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "from-parquet-pairs"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Reads prompt/output pairs from Parquet database files."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help="Path to the parquet file(s) to read; global syntax is supported", required=True, nargs="+")
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
        if (self.col_instruction is None) and (self.col_input is None) and (self.col_output is None):
            raise Exception("No columns specified!")

    def read(self) -> Iterable[PairData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: Iterable[PairData]
        """
        self.finalize()

        self._current_input = self._inputs.pop(0)
        self.session.current_input = self._current_input
        if self.verbose:
            self.logger().info("Reading from: " + str(self.session.current_input))
        self._current_table = pq.read_table(self._current_input).to_pandas()
        self.session.input_changed = True
        if (self.col_instruction is not None) and (self.col_instruction not in self._current_table.columns):
            raise Exception("Failed to locate instruction column: %s" % self.col_instruction)
        if (self.col_input is not None) and (self.col_input not in self._current_table.columns):
            raise Exception("Failed to locate input column: %s" % self.col_input)
        if (self.col_output is not None) and (self.col_output not in self._current_table.columns):
            raise Exception("Failed to locate output column: %s" % self.col_output)

        for index, row in self._current_table.iterrows():
            val_instruction = None if (self.col_instruction is None) else row[self.col_instruction]
            val_input = None if (self.col_input is None) else row[self.col_input]
            val_output = None if (self.col_output is None) else row[self.col_output]
            yield PairData(
                instruction=val_instruction,
                input=val_input,
                output=val_output,
            )

    def has_finished(self) -> bool:
        """
        Returns whether reading has finished.

        :return: True if finished
        :rtype: bool
        """
        return len(self._inputs) == 0

    def finalize(self):
        """
        Finishes the reading, e.g., for closing files or databases.
        """
        if self._current_input is not None:
            super().finalize()
            self._current_input = None


class ParquetPairsWriter(BatchPairWriter):
    """
    Writer for Parquet database files.
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
        self.col_instruction = None
        self.col_input = None
        self.col_output = None
        self._output = None
        self._output_writer = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "to-parquet-pairs"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Writes prompt/output pairs in Parquet database format."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="Path of the CSV file to write (directory when processing multiple files)", required=True)
        parser.add_argument("--col_instruction", metavar="COL", type=str, default=None, help="The name of the column for the instructions", required=False)
        parser.add_argument("--col_input", metavar="COL", type=str, default=None, help="The name of the column for the inputs", required=False)
        parser.add_argument("--col_output", metavar="COL", type=str, default=None, help="The name of the column for the outputs", required=False)
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
        if (self.col_instruction is None) and (self.col_input is None) and (self.col_output is None):
            raise Exception("No columns specified!")

    def write_batch(self, data: Iterable[PairData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of PairData
        :type data: Iterable
        """
        if self.session.input_changed:
            self.finalize()
            output = generate_output(self.session.current_input, self.target, ".parquet", self.session.options.compression)
            if self.verbose:
                self.logger().info("Writing to: " + output)
            # create dictionary
            d_instruction = []
            d_input = []
            d_output = []
            for row in data:
                d_instruction.append(row.instruction)
                d_input.append(row.input)
                d_output.append(row.output)
            d = dict()
            if self.col_instruction is not None:
                d[self.col_instruction] = d_instruction
            if self.col_input is not None:
                d[self.col_input] = d_input
            if self.col_output is not None:
                d[self.col_output] = d_output
            # create pandas dataframe
            df = pd.DataFrame.from_dict(d)
            table = pa.Table.from_pandas(df)
            pq.write_table(table, output)

    def finalize(self):
        """
        Finishes the writing, e.g., for closing files or databases.
        """
        if self._output is not None:
            super().finalize()
            self._output_writer = None
            self._output.close()
            self._output = None
