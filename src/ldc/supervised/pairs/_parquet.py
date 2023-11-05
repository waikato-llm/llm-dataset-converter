import argparse
from typing import Iterable, List, Union

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from ldc.core import LOGGING_WARN, domain_suffix
from ldc.base_io import locate_files, generate_output
from ._core import PairData, PairReader, BatchPairWriter
from ldc.utils import add_meta_data


class ParquetPairsReader(PairReader):
    """
    Reader for Parquet database files.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 col_instruction: str = None, col_input: str = None, col_output: str = None,
                 col_id: str = None, col_meta: List[str] = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param col_instruction: the column with the instruction data
        :type col_instruction: str
        :param col_input: the column with the input data
        :type col_input: str
        :param col_output: the column with the output data
        :type col_output: str
        :param col_id: the (optional) column containing row IDs
        :type col_id: str
        :param col_meta: the columns to store in the meta-data, can be None
        :type col_meta: list
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.source = source
        self.source_list = source_list
        self.col_instruction = col_instruction
        self.col_input = col_input
        self.col_output = col_output
        self.col_id = col_id
        self.col_meta = col_meta
        self._inputs = None
        self._current_input = None
        self._current_table = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "from-parquet-" + domain_suffix(self)

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
        parser.add_argument("-i", "--input", type=str, help="Path to the parquet file(s) to read; glob syntax is supported", required=False, nargs="*")
        parser.add_argument("-I", "--input_list", type=str, help="Path to the text file(s) listing the data files to use", required=False, nargs="*")
        parser.add_argument("--col_instruction", metavar="COL", type=str, default=None, help="The name of the column with the instructions", required=False)
        parser.add_argument("--col_input", metavar="COL", type=str, default=None, help="The name of the column with the inputs", required=False)
        parser.add_argument("--col_output", metavar="COL", type=str, default=None, help="The name of the column with the outputs", required=False)
        parser.add_argument("--col_id", metavar="COL", type=str, default=None, help="The name of the column with the row IDs (gets stored under 'id' in meta-data)", required=False)
        parser.add_argument("--col_meta", metavar="COL", type=str, default=None, help="The name of the columns to store in the meta-data", required=False, nargs="*")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.source = ns.input
        self.source_list = ns.input_list
        self.col_instruction = ns.col_instruction
        self.col_input = ns.col_input
        self.col_output = ns.col_output
        self.col_id = ns.col_id
        self.col_meta = ns.col_meta

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, input_lists=self.source_list, fail_if_empty=True)
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
        self.logger().info("Reading from: " + str(self.session.current_input))
        self._current_table = pq.read_table(self._current_input).to_pandas()
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

            id_ = None
            if self.col_id is not None:
                id_ = row[self.col_id]

            meta = None

            # ID?
            if id_ is not None:
                meta = add_meta_data(meta, "id", id_)

            # additional meta-data columns
            if self.col_meta is not None:
                for c in self.col_meta:
                    if c in row:
                        meta = add_meta_data(meta, c, row[c])

            yield PairData(
                instruction=val_instruction,
                input=val_input,
                output=val_output,
                meta=meta,
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

    def __init__(self, target: str = None,
                 col_instruction: str = None, col_input: str = None, col_output: str = None, col_id: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param col_instruction: the column with the instruction data
        :type col_instruction: str
        :param col_input: the column with the input data
        :type col_input: str
        :param col_output: the column with the output data
        :type col_output: str
        :param col_id: the (optional) column containing row IDs
        :type col_id: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.target = target
        self.col_instruction = col_instruction
        self.col_input = col_input
        self.col_output = col_output
        self.col_id = col_id
        self._current_output = None
        self._output = None
        self._output_writer = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "to-parquet-" + domain_suffix(self)

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
        parser.add_argument("--col_id", metavar="COL", type=str, default=None, help="The name of the column for the row IDs (uses 'id' from meta-data)", required=False)
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
        self.col_id = ns.col_id

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        if (self.col_instruction is None) and (self.col_input is None) and (self.col_output is None):
            raise Exception("No columns specified!")

    def write_batch(self, data: Iterable[PairData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of PairData
        :type data: Iterable
        """
        if self._has_input_changed(update=True) and self._output_needs_changing(self._current_output, self.target, ".parquet"):
            self.finalize()
            self._current_output = generate_output(self.session.current_input, self.target, ".parquet", self.session.options.compression)
            self.logger().info("Writing to: " + self._current_output)
            # create dictionary
            d_instruction = []
            d_input = []
            d_output = []
            d_ids = []
            for row in data:
                d_instruction.append(row.instruction)
                d_input.append(row.input)
                d_output.append(row.output)
                if self.col_id is not None:
                    if (row.meta is not None) and ("id" in row.meta):
                        d_ids.append(row.meta["id"])
                    else:
                        d_ids.append(None)
            d = dict()
            if self.col_instruction is not None:
                d[self.col_instruction] = d_instruction
            if self.col_input is not None:
                d[self.col_input] = d_input
            if self.col_output is not None:
                d[self.col_output] = d_output
            if self.col_id is not None:
                d[self.col_id] = d_ids
            # create pandas dataframe
            df = pd.DataFrame.from_dict(d)
            table = pa.Table.from_pandas(df)
            pq.write_table(table, self._current_output)

    def finalize(self):
        """
        Finishes the writing, e.g., for closing files or databases.
        """
        if self._output is not None:
            super().finalize()
            self._output_writer = None
            self._output.close()
            self._output = None
