import abc
import argparse
import csv
import sys
import traceback
from typing import Iterable, List, Union

from wai.logging import LOGGING_WARNING
from seppl import add_metadata
from seppl.io import locate_files
from ldc.core import domain_suffix
from ldc.base_io import open_file, generate_output
from ._core import ClassificationData, ClassificationReader, BatchClassificationWriter
from ldc.utils import str_to_column_index


class AbstractCsvLikeClassificationReader(ClassificationReader, abc.ABC):
    """
    Ancestor for readers of CSV-like files.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 no_header: bool = False, col_text: str = None, col_label: str = None,
                 col_id: str = None, col_meta: List[str] = None, encoding: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param no_header: whether the data files have no header
        :type no_header: bool
        :param col_text: the column with the text data
        :type col_text: str
        :param col_label: the column with the label
        :type col_label: str
        :param col_id: the (optional) column containing row IDs
        :type col_id: str
        :param col_meta: the columns to store in the meta-data, can be None
        :type col_meta: list
        :param encoding: the encoding to use, None for auto-detect
        :type encoding: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.source = source
        self.source_list = source_list
        self.no_header = no_header
        self.col_text = col_text
        self.col_label = col_label
        self.col_id = col_id
        self.col_meta = col_meta
        self.idx_text = -1
        self.idx_label = -1
        self.idx_id = -1
        self.idx_meta = None
        self.encoding = encoding
        self._inputs = None
        self._current_input = None
        self._current_reader = None

    def _get_input_description(self) -> str:
        """
        Returns the description to use for the input file in the argparser.

        :return: the description
        :rtype: str
        """
        raise NotImplementedError()

    def _get_input_list_description(self) -> str:
        """
        Returns the description to use for the input_list file in the argparser.

        :return: the description
        :rtype: str
        """
        return "Path to the text file(s) listing the data files to use"

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help=self._get_input_description(), required=False, nargs="*")
        parser.add_argument("-I", "--input_list", type=str, help=self._get_input_list_description(), required=False, nargs="*")
        parser.add_argument("--col_text", metavar="COL", type=str, default=None, help="The name of the column (or 1-based index if no header row) with the text", required=False)
        parser.add_argument("--col_label", metavar="COL", type=str, default=None, help="The name of the column (or 1-based index if no header row) with the labels", required=False)
        parser.add_argument("--col_id", metavar="COL", type=str, default=None, help="The name (or 1-based index if no header row) of the column with the row IDs (gets stored under 'id' in meta-data)", required=False)
        parser.add_argument("--col_meta", metavar="COL", type=str, default=None, help="The name (or 1-based index) of the columns to store in the meta-data", required=False, nargs="*")
        parser.add_argument("-n", "--no_header", action="store_true", help="For files with no header row", required=False)
        parser.add_argument("--encoding", metavar="ENC", type=str, default=None, help="The encoding to force instead of auto-detecting it, e.g., 'utf-8'", required=False)
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
        self.no_header = ns.no_header
        self.encoding = ns.encoding

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self.idx_text = str_to_column_index(self.col_text)
        self.idx_label = str_to_column_index(self.col_label)
        if not self.no_header and (self.col_text is None) and (self.col_label is None):
            raise Exception("Header row expected but no columns specified!")
        if self.no_header and (self.idx_text == -1) and (self.idx_label == -1):
            raise Exception("No header row expected but no column indices specified!")

        self.idx_id = str_to_column_index(self.col_id) - 1

        if self.col_meta is not None:
            self.idx_meta = []
            for c in self.col_meta:
                self.idx_meta.append(str_to_column_index(c))

        self._inputs = locate_files(self.source, input_lists=self.source_list, fail_if_empty=True)

    def _init_reader(self, current_input) -> Union[csv.reader, csv.DictReader]:
        """
        Initializes and returns the CSV reader to use.

        :param current_input: the file pointer to initialize with
        :return: the reader to use
        :rtype: csv.reader or csv.DictReader
        """
        raise NotImplementedError()

    def read(self) -> Iterable[ClassificationData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: ClassificationData
        """
        self.finalize()

        self._current_input = self._inputs.pop(0)
        self.session.current_input = self._current_input
        self.logger().info("Reading from: " + str(self.session.current_input))
        self._current_input = open_file(self._current_input, mode="rt", encoding=self.encoding, logger=self.logger())
        self._current_reader = self._init_reader(self._current_input)

        for row in self._current_reader:
            try:
                val_text = None
                val_label = None
                if self.no_header:
                    if self.idx_text > -1:
                        val_text = row[self.idx_text]
                    if self.idx_label > -1:
                        val_label = row[self.idx_label]
                else:
                    if self.col_text is not None:
                        val_text = row[self.col_text]
                    if self.col_label is not None:
                        val_label = row[self.col_label]

                id_ = None
                if self.col_id is not None:
                    if self.no_header:
                        id_ = row[self.idx_id]
                    else:
                        id_ = row[self.col_id]

                meta = None

                # ID?
                if id_ is not None:
                    meta = add_metadata(meta, "id", id_)

                # additional meta-data columns
                if self.col_meta is not None:
                    if self.no_header:
                        for i in self.idx_meta:
                            if i > -1:
                                meta = add_metadata(meta, str(i), row[i])
                    else:
                        for c in self.col_meta:
                            if c in row:
                                meta = add_metadata(meta, c, row[c])

                yield ClassificationData(
                    text=val_text,
                    label=val_label,
                    meta=meta,
                )
            except:
                self.logger().error("Failed to process row: %s" % str(row))
                traceback.print_exc()

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
            self._current_reader = None
            self._current_input.close()
            self._current_input = None


class AbstractCsvLikeClassificationWriter(BatchClassificationWriter, abc.ABC):
    """
    Ancestor for writers of CSV-like files.
    """

    def __init__(self, target: str = None, no_header: bool = False,
                 col_text: str = None, col_label: str = None, col_id: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param no_header: whether to suppress the header row
        :type no_header: bool
        :param col_text: the column with the text data
        :type col_text: str
        :param col_label: the column with the labels
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
        self.no_header = no_header
        self.col_text = col_text
        self.col_label = col_label
        self.col_id = col_id
        self._current_output = None
        self._output = None
        self._output_writer = None

    def _get_output_description(self) -> str:
        """
        Returns the description to use for the output file in the argparser.

        :return: the description
        :rtype: str
        """
        raise NotImplementedError()

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help=self._get_output_description(), required=True)
        parser.add_argument("--col_text", metavar="COL", type=str, default=None, help="The name of the column for the text", required=False)
        parser.add_argument("--col_label", metavar="COL", type=str, default=None, help="The name of the column for the labels", required=False)
        parser.add_argument("--col_id", metavar="COL", type=str, default=None, help="The name of the column for the row IDs (uses 'id' from meta-data)", required=False)
        parser.add_argument("-n", "--no_header", action="store_true", help="For suppressing the header row", required=False)
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
        self.no_header = ns.no_header

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        if not self.no_header and (self.col_text is None) and (self.col_label is None):
            raise Exception("Outputting header, but no columns specified!")

    def _init_writer(self, current_output) -> csv.writer:
        """
        Initializes and returns the CSV writer to use for the output.

        :param current_output: the file pointer of the output file to initialize with
        :return: the reader
        :rtype: csv.writer
        """
        raise NotImplementedError()

    def _get_extension(self) -> str:
        """
        Returns the extension to use for output files.

        :return: the extension to use (incl dot)
        :rtype: str
        """
        raise NotImplementedError()

    def write_batch(self, data: Iterable[ClassificationData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of ClassificationData
        :type data: Iterable
        """
        if self._has_input_changed(update=True) and self._output_needs_changing(self._current_output, self.target, self._get_extension()):
            self.finalize()
            self._current_output = generate_output(self.session.current_input, self.target, self._get_extension(), self.session.options.compression)
            self.logger().info("Writing to: " + self._current_output)
            self._output = open_file(self._current_output, mode="wt")
            self._output_writer = self._init_writer(self._output)
            if not self.no_header:
                row = []
                if self.col_id is not None:
                    row.append(self.col_id)
                if self.col_text is not None:
                    row.append(self.col_text)
                if self.col_label is not None:
                    row.append(self.col_label)
                self._output_writer.writerow(row)

        for item in data:
            row = []
            if self.col_id is not None:
                if (item.meta is not None) and ("id" in item.meta):
                    row.append(item.meta["id"])
                else:
                    row.append(None)
            if self.no_header:
                row.extend([item.text, item.label])
            else:
                if self.col_text is not None:
                    row.append(item.text)
                if self.col_label is not None:
                    row.append(item.label)
            try:
                self._output_writer.writerow(row)
            except:
                print("Failed to write row: %s" % str(row), file=sys.stderr)
                traceback.print_exc()

    def finalize(self):
        """
        Finishes the writing, e.g., for closing files or databases.
        """
        if self._output is not None:
            super().finalize()
            self._output_writer = None
            self._output.close()
            self._output = None


class CsvClassificationReader(AbstractCsvLikeClassificationReader):
    """
    Reader for CSV files.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 no_header: bool = False, col_text: str = None, col_label: str = None,
                 col_id: str = None, col_meta: List[str] = None, encoding: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param no_header: whether the data files have no header
        :type no_header: bool
        :param col_text: the column with the tex data
        :type col_text: str
        :param col_label: the column with the labels
        :type col_label: str
        :param col_id: the (optional) column containing row IDs
        :type col_id: str
        :param col_meta: the columns to store in the meta-data, can be None
        :type col_meta: list
        :param encoding: the encoding to use, None for auto-detect
        :type encoding: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(source=source, source_list=source_list,
                         no_header=no_header, col_text=col_text, col_label=col_label,
                         col_id=col_id, col_meta=col_meta, encoding=encoding,
                         logger_name=logger_name, logging_level=logging_level)

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "from-csv-" + domain_suffix(self)

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Reads classification data in CSV format."

    def _get_input_description(self) -> str:
        """
        Returns the description to use for the input file in the argparser.

        :return: the description
        :rtype: str
        """
        return "Path to the CSV file(s) to read; glob syntax is supported"

    def _init_reader(self, current_input) -> Union[csv.reader, csv.DictReader]:
        """
        Initializes and returns the CSV reader to use.

        :param current_input: the file pointer to initialize with
        :return: the reader to use
        :rtype: csv.reader or csv.DictReader
        """
        if self.no_header:
            return csv.reader(current_input)
        else:
            return csv.DictReader(current_input)


class CsvClassificationWriter(AbstractCsvLikeClassificationWriter):
    """
    Writer for CSV files.
    """

    def __init__(self, target: str = None, no_header: bool = False,
                 col_text: str = None, col_label: str = None, col_id: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param no_header: whether to suppress the header row
        :type no_header: bool
        :param col_text: the column with the text data
        :type col_text: str
        :param col_label: the column with the labels
        :type col_label: str
        :param col_id: the (optional) column containing row IDs
        :type col_id: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(target=target, no_header=no_header, col_text=col_text, col_label=col_label,
                         col_id=col_id, logger_name=logger_name, logging_level=logging_level)

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "to-csv-" + domain_suffix(self)

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Writes classification data in CSV format."

    def _get_output_description(self) -> str:
        """
        Returns the description to use for the output file in the argparser.

        :return: the description
        :rtype: str
        """
        return "Path of the CSV file to write (directory when processing multiple files)"

    def _init_writer(self, current_output) -> csv.writer:
        """
        Initializes and returns the CSV writer to use for the output.

        :param current_output: the file pointer of the output file to initialize with
        :return: the reader
        :rtype: csv.writer
        """
        return csv.writer(current_output)

    def _get_extension(self) -> str:
        """
        Returns the extension to use for output files.

        :return: the extension to use (incl dot)
        :rtype: str
        """
        return ".csv"


class TsvClassificationReader(AbstractCsvLikeClassificationReader):
    """
    Reader for TSV files.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 no_header: bool = False, col_text: str = None, col_label: str = None,
                 col_id: str = None, col_meta: List[str] = None, encoding: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param no_header: whether the data files have no header
        :type no_header: bool
        :param col_text: the column with the text data
        :type col_text: str
        :param col_label: the column with the labels
        :type col_label: str
        :param col_id: the (optional) column containing row IDs
        :type col_id: str
        :param col_meta: the columns to store in the meta-data, can be None
        :type col_meta: list
        :param encoding: the encoding to use, None for auto-detect
        :type encoding: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(source=source, source_list=source_list,
                         no_header=no_header, col_text=col_text, col_label=col_label,
                         col_id=col_id, col_meta=col_meta, encoding=encoding,
                         logger_name=logger_name, logging_level=logging_level)

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "from-tsv-" + domain_suffix(self)

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Reads classification data in TSV format."

    def _get_input_description(self) -> str:
        """
        Returns the description to use for the input file in the argparser.

        :return: the description
        :rtype: str
        """
        return "Path to the TSV file(s) to read; glob syntax is supported"

    def _init_reader(self, current_input) -> Union[csv.reader, csv.DictReader]:
        """
        Initializes and returns the CSV reader to use.

        :param current_input: the file pointer to initialize with
        :return: the reader to use
        :rtype: csv.reader or csv.DictReader
        """
        if self.no_header:
            return csv.reader(current_input, delimiter='\t')
        else:
            return csv.DictReader(current_input, delimiter='\t')


class TsvClassificationWriter(AbstractCsvLikeClassificationWriter):
    """
    Writer for TSV files.
    """

    def __init__(self, target: str = None, no_header: bool = False,
                 col_text: str = None, col_label: str = None, col_id: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param no_header: whether to suppress the header row
        :type no_header: bool
        :param col_text: the column with the text data
        :type col_text: str
        :param col_label: the column with the labels
        :type col_label: str
        :param col_id: the (optional) column containing row IDs
        :type col_id: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(target=target, no_header=no_header, col_text=col_text, col_label=col_label,
                         col_id=col_id, logger_name=logger_name, logging_level=logging_level)

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "to-tsv-" + domain_suffix(self)

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Writes classification data in TSV format."

    def _get_output_description(self) -> str:
        """
        Returns the description to use for the output file in the argparser.

        :return: the description
        :rtype: str
        """
        return "Path of the TSV file to write (directory when processing multiple files)"

    def _init_writer(self, current_output) -> csv.writer:
        """
        Initializes and returns the CSV writer to use for the output.

        :param current_output: the file pointer of the output file to initialize with
        :return: the reader
        :rtype: csv.writer
        """
        return csv.writer(current_output, delimiter='\t')

    def _get_extension(self) -> str:
        """
        Returns the extension to use for output files.

        :return: the extension to use (incl dot)
        :rtype: str
        """
        return ".tsv"
