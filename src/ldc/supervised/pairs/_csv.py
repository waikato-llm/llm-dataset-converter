import abc
import argparse
import csv
import sys
import traceback
from typing import Iterable, List, Union

from wai.logging import LOGGING_WARNING
from seppl import add_metadata
from seppl.io import locate_files
from seppl.placeholders import PlaceholderSupporter, placeholder_list, expand_placeholders
from ldc.core import domain_suffix
from ldc.api import open_file, generate_output
from ldc.api.supervised.pairs import PairData, PairReader, BatchPairWriter
from ldc.utils import str_to_column_index
from ldc.text_utils import empty_str_if_none


class AbstractCsvLikePairsReader(PairReader, abc.ABC, PlaceholderSupporter):
    """
    Ancestor for readers of CSV-like files.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 no_header: bool = False, col_instruction: str = None, col_input: str = None, col_output: str = None,
                 col_id: str = None, col_meta: List[str] = None, encoding: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param no_header: whether the data files have no header
        :type no_header: bool
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
        self.col_instruction = col_instruction
        self.col_input = col_input
        self.col_output = col_output
        self.col_id = col_id
        self.col_meta = col_meta
        self.idx_instruction = -1
        self.idx_input = -1
        self.idx_output = -1
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

    def _get_default_glob(self) -> str:
        """
        Returns the default glob to use for locate_files.

        :return: the glob, can be None
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
        parser.add_argument("-i", "--input", type=str, help=self._get_input_description() + "; " + placeholder_list(obj=self), required=False, nargs="*")
        parser.add_argument("-I", "--input_list", type=str, help=self._get_input_list_description() + "; " + placeholder_list(obj=self), required=False, nargs="*")
        parser.add_argument("--col_instruction", metavar="COL", type=str, default=None, help="The name of the column (or 1-based index if no header row) with the instructions", required=False)
        parser.add_argument("--col_input", metavar="COL", type=str, default=None, help="The name of the column (or 1-based index if no header row) with the inputs", required=False)
        parser.add_argument("--col_output", metavar="COL", type=str, default=None, help="The name of the column (or 1-based index if no header row) with the outputs", required=False)
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
        self.col_instruction = ns.col_instruction
        self.col_input = ns.col_input
        self.col_output = ns.col_output
        self.col_id = ns.col_id
        self.col_meta = ns.col_meta
        self.no_header = ns.no_header
        self.encoding = ns.encoding

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self.idx_instruction = str_to_column_index(self.col_instruction)
        self.idx_input = str_to_column_index(self.col_input)
        self.idx_output = str_to_column_index(self.col_output)
        if not self.no_header and (self.col_instruction is None) and (self.col_input is None) and (self.col_output is None):
            raise Exception("Header row expected but no columns specified!")
        if self.no_header and (self.idx_instruction == -1) and (self.idx_input == -1) and (self.idx_output == -1):
            raise Exception("No header row expected but no column indices specified!")

        self.idx_id = str_to_column_index(self.col_id) - 1

        if self.col_meta is not None:
            self.idx_meta = []
            for c in self.col_meta:
                self.idx_meta.append(str_to_column_index(c))

        self._inputs = locate_files(self.source, input_lists=self.source_list, fail_if_empty=True, default_glob=self._get_default_glob())

    def _init_reader(self, current_input) -> Union[csv.reader, csv.DictReader]:
        """
        Initializes and returns the CSV reader to use.

        :param current_input: the file pointer to initialize with
        :return: the reader to use
        :rtype: csv.reader or csv.DictReader
        """
        raise NotImplementedError()

    def read(self) -> Iterable[PairData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: PairData
        """
        self.finalize()

        self._current_input = self._inputs.pop(0)
        self.session.current_input = self._current_input
        self.logger().info("Reading from: " + str(self.session.current_input))
        self._current_input = open_file(self._current_input, mode="rt", encoding=self.encoding, logger=self.logger())
        self._current_reader = self._init_reader(self._current_input)

        for row in self._current_reader:
            try:
                val_instruction = None
                val_input = None
                val_output = None
                if self.no_header:
                    if self.idx_instruction > -1:
                        val_instruction = row[self.idx_instruction]
                    if self.idx_input > -1:
                        val_input = row[self.idx_input]
                    if self.idx_output > -1:
                        val_output = row[self.idx_output]
                else:
                    if self.col_instruction is not None:
                        val_instruction = row[self.col_instruction]
                    if self.col_input is not None:
                        val_input = row[self.col_input]
                    if self.col_output is not None:
                        val_output = row[self.col_output]

                id_ = None
                if self.col_id is not None:
                    if self.no_header:
                        id_ = row[self.idx_id]
                    else:
                        id_ = row[self.col_id]

                meta = None

                # file
                meta = add_metadata(meta, "file", self.session.current_input)

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

                yield PairData(
                    instruction=val_instruction,
                    input=val_input,
                    output=val_output,
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


class AbstractCsvLikePairsWriter(BatchPairWriter, abc.ABC, PlaceholderSupporter):
    """
    Ancestor for writers of CSV-like files.
    """

    def __init__(self, target: str = None, no_header: bool = False,
                 col_instruction: str = None, col_input: str = None, col_output: str = None, col_id: str = None,
                 encoding: str = None, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param no_header: whether to suppress the header row
        :type no_header: bool
        :param col_instruction: the column with the instruction data
        :type col_instruction: str
        :param col_input: the column with the input data
        :type col_input: str
        :param col_output: the column with the output data
        :type col_output: str
        :param col_id: the (optional) column containing row IDs
        :type col_id: str
        :param encoding: the encoding to use, None for default
        :type encoding: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.target = target
        self.no_header = no_header
        self.col_instruction = col_instruction
        self.col_input = col_input
        self.col_output = col_output
        self.col_id = col_id
        self.encoding = encoding
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
        parser.add_argument("-o", "--output", type=str, help=self._get_output_description() + "; " + placeholder_list(obj=self), required=True)
        parser.add_argument("--col_instruction", metavar="COL", type=str, default=None, help="The name of the column for the instructions", required=False)
        parser.add_argument("--col_input", metavar="COL", type=str, default=None, help="The name of the column for the inputs", required=False)
        parser.add_argument("--col_output", metavar="COL", type=str, default=None, help="The name of the column for the outputs", required=False)
        parser.add_argument("--col_id", metavar="COL", type=str, default=None, help="The name of the column for the row IDs (uses 'id' from meta-data)", required=False)
        parser.add_argument("-n", "--no_header", action="store_true", help="For suppressing the header row", required=False)
        parser.add_argument("--encoding", metavar="ENC", type=str, default=None, help="The encoding to force instead of using the default, e.g., 'utf-8'", required=False)
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
        self.no_header = ns.no_header
        self.encoding = ns.encoding

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        if not self.no_header and (self.col_instruction is None) and (self.col_input is None) and (self.col_output is None):
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

    def write_batch(self, data: Iterable[PairData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of PairData
        :type data: Iterable
        """
        target = expand_placeholders(self.target)
        if self._has_input_changed(update=True) and self._output_needs_changing(self._current_output, target, self._get_extension()):
            self.finalize()
            self._current_output = generate_output(self.session.current_input, target, self._get_extension(), self.session.options.compression)
            self.logger().info("Writing to: " + self._current_output)
            self._output = open_file(self._current_output, mode="wt", encoding=self.encoding)
            self._output_writer = self._init_writer(self._output)
            if not self.no_header:
                row = []
                if self.col_id is not None:
                    row.append(self.col_id)
                if self.col_instruction is not None:
                    row.append(self.col_instruction)
                if self.col_input is not None:
                    row.append(self.col_input)
                if self.col_output is not None:
                    row.append(self.col_output)
                self._output_writer.writerow(row)

        for item in data:
            row = []
            if self.col_id is not None:
                if (item.meta is not None) and ("id" in item.meta):
                    row.append(item.meta["id"])
                else:
                    row.append(None)
            if self.no_header:
                row.extend([empty_str_if_none(item.instruction), empty_str_if_none(item.input), empty_str_if_none(item.output)])
            else:
                if self.col_instruction is not None:
                    row.append(empty_str_if_none(item.instruction))
                if self.col_input is not None:
                    row.append(empty_str_if_none(item.input))
                if self.col_output is not None:
                    row.append(empty_str_if_none(item.output))
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


class CsvPairsReader(AbstractCsvLikePairsReader):
    """
    Reader for CSV files.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 no_header: bool = False, col_instruction: str = None, col_input: str = None, col_output: str = None,
                 col_id: str = None, col_meta: List[str] = None, encoding: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param no_header: whether the data files have no header
        :type no_header: bool
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
        :param encoding: the encoding to use, None for auto-detect
        :type encoding: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(source=source, source_list=source_list,
                         no_header=no_header, col_instruction=col_instruction, col_input=col_input,
                         col_output=col_output, col_id=col_id, col_meta=col_meta, encoding=encoding,
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
        return "Reads prompt/output pairs in CSV format."

    def _get_input_description(self) -> str:
        """
        Returns the description to use for the input file in the argparser.

        :return: the description
        :rtype: str
        """
        return "Path to the CSV file(s) to read; glob syntax is supported"

    def _get_default_glob(self) -> str:
        """
        Returns the default glob to use for locate_files.

        :return: the glob, can be None
        :rtype: str
        """
        return "*.csv"

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


class CsvPairsWriter(AbstractCsvLikePairsWriter):
    """
    Writer for CSV files.
    """

    def __init__(self, target: str = None, no_header: bool = False,
                 col_instruction: str = None, col_input: str = None, col_output: str = None, col_id: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param no_header: whether to suppress the header row
        :type no_header: bool
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
        super().__init__(target=target, no_header=no_header, col_instruction=col_instruction, col_input=col_input,
                         col_output=col_output, col_id=col_id, logger_name=logger_name, logging_level=logging_level)

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
        return "Writes prompt/output pairs in CSV format."

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


class TsvPairsReader(AbstractCsvLikePairsReader):
    """
    Reader for TSV files.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 no_header: bool = False, col_instruction: str = None, col_input: str = None, col_output: str = None,
                 col_id: str = None, col_meta: List[str] = None, encoding: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param no_header: whether the data files have no header
        :type no_header: bool
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
        :param encoding: the encoding to use, None for auto-detect
        :type encoding: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(source=source, source_list=source_list,
                         no_header=no_header, col_instruction=col_instruction, col_input=col_input,
                         col_output=col_output, col_id=col_id, col_meta=col_meta, encoding=encoding,
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
        return "Reads prompt/output pairs in TSV format."

    def _get_input_description(self) -> str:
        """
        Returns the description to use for the input file in the argparser.

        :return: the description
        :rtype: str
        """
        return "Path to the TSV file(s) to read; glob syntax is supported"

    def _get_default_glob(self) -> str:
        """
        Returns the default glob to use for locate_files.

        :return: the glob, can be None
        :rtype: str
        """
        return "*.tsv"

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


class TsvPairsWriter(AbstractCsvLikePairsWriter):
    """
    Writer for TSV files.
    """

    def __init__(self, target: str = None, no_header: bool = False,
                 col_instruction: str = None, col_input: str = None, col_output: str = None, col_id: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param no_header: whether to suppress the header row
        :type no_header: bool
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
        super().__init__(target=target, no_header=no_header, col_instruction=col_instruction, col_input=col_input,
                         col_output=col_output, col_id=col_id, logger_name=logger_name, logging_level=logging_level)

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
        return "Writes prompt/output pairs in TSV format."

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
