import argparse
from typing import Iterable, List, Union

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from ldc.core import LOGGING_WARN
from ldc.io import locate_files, generate_output
from ._core import PretrainData, PretrainReader, BatchPretrainWriter


class ParquetPretrainReader(PretrainReader):
    """
    Reader for Parquet database files.
    """

    def __init__(self, source: Union[str, List[str]] = None, col_content: str = None, col_id: str = None,
                 logging_level: str = LOGGING_WARN):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param col_content: the column with the content
        :type col_content: str
        :param col_id: the (optional) column containing row IDs
        :type col_id: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.source = source
        self.col_content = col_content
        self.col_id = col_id
        self._inputs = None
        self._current_input = None
        self._current_table = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "from-parquet-pretrain"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Reads text from Parquet database files to use for pretraining."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help="Path to the parquet file(s) to read; glob syntax is supported", required=True, nargs="+")
        parser.add_argument("--col_content", metavar="COL", type=str, default=None, help="The name of the column with the text to retrieve", required=False)
        parser.add_argument("--col_id", metavar="COL", type=str, default=None, help="The name of the column with the row IDs (gets stored under 'id' in meta-data)", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.source = ns.input
        self.col_content = ns.col_content
        self.col_id = ns.col_id

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, fail_if_empty=True)
        if self.col_content is None:
            raise Exception("No content column specified!")

    def read(self) -> Iterable[PretrainData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: Iterable[PretrainData]
        """
        self.finalize()

        self._current_input = self._inputs.pop(0)
        self.session.current_input = self._current_input
        self.logger().info("Reading from: " + str(self.session.current_input))
        self._current_table = pq.read_table(self._current_input).to_pandas()
        self.session.input_changed = True
        if (self.col_content is not None) and (self.col_content not in self._current_table.columns):
            raise Exception("Failed to locate content column: %s" % self.col_content)

        for index, row in self._current_table.iterrows():
            val_content = None if (self.col_content is None) else row[self.col_content]

            id_ = None
            if self.col_id is not None:
                id_ = row[self.col_id]

            meta = None
            if id_ is not None:
                meta = {"id": id_}

            yield PretrainData(
                content=val_content,
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


class ParquetPretrainWriter(BatchPretrainWriter):
    """
    Writer for Parquet database files.
    """

    def __init__(self, target: str = None, col_content: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param col_content: the column with the content
        :type col_content: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.target = target
        self.col_content = col_content
        self._output = None
        self._output_writer = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "to-parquet-pretrain"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Writes text used for pretraining in Parquet database format."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="Path of the CSV file to write (directory when processing multiple files)", required=True)
        parser.add_argument("--col_content", metavar="COL", type=str, default=None, help="The name of the column for the text content", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.target = ns.output
        self.col_content = ns.col_content

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        if self.col_content is None:
            raise Exception("No content column specified!")

    def write_batch(self, data: Iterable[PretrainData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of PretrainData
        :type data: Iterable
        """
        if self.session.input_changed:
            self.finalize()
            output = generate_output(self.session.current_input, self.target, ".parquet", self.session.options.compression)
            self.logger().info("Writing to: " + output)
            # create dictionary
            d_content = []
            for row in data:
                d_content.append(row.content)
            d = dict()
            if self.col_content is not None:
                d[self.col_content] = d_content
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
