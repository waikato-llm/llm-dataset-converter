import argparse
from typing import Iterable, List, Union

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from wai.logging import LOGGING_WARNING
from seppl import add_metadata
from seppl.io import locate_files
from seppl.placeholders import PlaceholderSupporter, placeholder_list, expand_placeholders
from ldc.core import domain_suffix
from ldc.api import generate_output
from ldc.api.supervised.classification import ClassificationData, ClassificationReader, BatchClassificationWriter
from ldc.text_utils import empty_str_if_none


class ParquetClassificationReader(ClassificationReader, PlaceholderSupporter):
    """
    Reader for Parquet database files.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 col_text: str = None, col_label: str = None,
                 col_id: str = None, col_meta: List[str] = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param col_text: the column with the text data
        :type col_text: str
        :param col_label: the column with the label
        :type col_label: str
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
        self.col_text = col_text
        self.col_label = col_label
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
        return "Reads classification data from Parquet database files."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help="Path to the parquet file(s) to read; glob syntax is supported; " + placeholder_list(obj=self), required=False, nargs="*")
        parser.add_argument("-I", "--input_list", type=str, help="Path to the text file(s) listing the parquet files to use; " + placeholder_list(obj=self), required=False, nargs="*")
        parser.add_argument("--col_text", metavar="COL", type=str, default=None, help="The name of the column with the text", required=False)
        parser.add_argument("--col_label", metavar="COL", type=str, default=None, help="The name of the column with the label", required=False)
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
        self.col_text = ns.col_text
        self.col_label = ns.col_label
        self.col_id = ns.col_id
        self.col_meta = ns.col_meta

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, input_lists=self.source_list, fail_if_empty=True, default_glob="*.parquet")
        if (self.col_text is None) and (self.col_label is None):
            raise Exception("No columns specified!")

    def read(self) -> Iterable[ClassificationData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: Iterable[ClassificationData]
        """
        self.finalize()

        self._current_input = self._inputs.pop(0)
        self.session.current_input = self._current_input
        self.logger().info("Reading from: " + str(self.session.current_input))
        self._current_table = pq.read_table(self._current_input).to_pandas()
        if (self.col_text is not None) and (self.col_text not in self._current_table.columns):
            raise Exception("Failed to locate instruction column: %s" % self.col_text)
        if (self.col_label is not None) and (self.col_label not in self._current_table.columns):
            raise Exception("Failed to locate input column: %s" % self.col_label)

        for index, row in self._current_table.iterrows():
            val_text = None if (self.col_text is None) else row[self.col_text]
            val_label = None if (self.col_label is None) else row[self.col_label]

            id_ = None
            if self.col_id is not None:
                id_ = row[self.col_id]

            meta = None

            # file
            meta = add_metadata(meta, "file", self.session.current_input)

            # ID?
            if id_ is not None:
                meta = add_metadata(meta, "id", id_)

            # additional meta-data columns
            if self.col_meta is not None:
                for c in self.col_meta:
                    if c in row:
                        meta = add_metadata(meta, c, row[c])

            yield ClassificationData(
                text=val_text,
                label=val_label,
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


class ParquetClassificationWriter(BatchClassificationWriter, PlaceholderSupporter):
    """
    Writer for Parquet database files.
    """

    def __init__(self, target: str = None,
                 col_text: str = None, col_label: str = None, col_id: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param col_text: the column with the text data
        :type col_text: str
        :param col_label: the column with the label
        :type col_label: str
        :param col_id: the (optional) column containing row IDs
        :type col_id: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.target = target
        self.col_text = col_text
        self.col_label = col_label
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
        return "Writes classification data in Parquet database format."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="Path of the CSV file to write (directory when processing multiple files); " + placeholder_list(obj=self), required=True)
        parser.add_argument("--col_text", metavar="COL", type=str, default=None, help="The name of the column for the text", required=False)
        parser.add_argument("--col_label", metavar="COL", type=str, default=None, help="The name of the column for the label", required=False)
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
        self.col_text = ns.col_text
        self.col_label = ns.col_label
        self.col_id = ns.col_id

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        if (self.col_text is None) and (self.col_label is None):
            raise Exception("No columns specified!")

    def write_batch(self, data: Iterable[ClassificationData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of ClassificationData
        :type data: Iterable
        """
        target = expand_placeholders(self.target)
        if self._has_input_changed(update=True) and self._output_needs_changing(self._current_output, target, ".parquet"):
            self.finalize()
            self._current_output = generate_output(self.session.current_input, target, ".parquet", self.session.options.compression)
            self.logger().info("Writing to: " + self._current_output)
            # create dictionary
            d_text = []
            d_label = []
            d_ids = []
            for row in data:
                d_text.append(empty_str_if_none(row.text))
                d_label.append(empty_str_if_none(row.label))
                if self.col_id is not None:
                    if (row.meta is not None) and ("id" in row.meta):
                        d_ids.append(row.meta["id"])
                    else:
                        d_ids.append(None)
            d = dict()
            if self.col_text is not None:
                d[self.col_text] = d_text
            if self.col_label is not None:
                d[self.col_label] = d_label
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
