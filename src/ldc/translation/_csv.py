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
from ldc.api.translation import TranslationData, TranslationReader, BatchTranslationWriter
from ldc.utils import str_to_column_index
from ldc.text_utils import empty_str_if_none


class AbstractCsvLikeTranslationReader(TranslationReader, abc.ABC, PlaceholderSupporter):
    """
    Ancestor for readers of CSV-like files.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 no_header: bool = False, col_id: str = None, col_meta: List[str] = None,
                 columns: List[str] = None, languages: List[str] = None, encoding: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param no_header: whether the data files have no header
        :type no_header: bool
        :param col_id: the (optional) 1-based column containing the row ID
        :type col_id: str
        :param col_meta: the columns to store in the meta-data, can be None
        :type col_meta: list
        :param columns: the columns with the language data (1-based indices)
        :type columns: list
        :param languages: the language IDs (ISO 639-1) corresponding to the columns
        :type languages: list
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
        self.col_id = col_id
        self.idx_id = -1
        self.col_meta = col_meta
        self.idx_meta = None
        self.columns = columns
        self.languages = languages
        self.indices = None
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
        parser.add_argument("-c", "--columns", metavar="COL", type=str, default=None, help="The 1-based column indices with the language data", required=True, nargs="+")
        parser.add_argument("-g", "--languages", metavar="LANG", type=str, default=None, help="The language IDs (ISO 639-1) corresponding to the columns", required=True, nargs="+")
        parser.add_argument("-n", "--no_header", action="store_true", help="For files with no header row", required=False)
        parser.add_argument("--col_id", metavar="COL", type=str, default=None, help="The 1-based column containing the row ID", required=False)
        parser.add_argument("--col_meta", metavar="COL", type=str, default=None, help="The name (or 1-based index) of the columns to store in the meta-data", required=False, nargs="*")
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
        self.columns = ns.columns[:]
        self.languages = ns.languages[:]
        self.no_header = ns.no_header
        self.col_id = ns.col_id
        self.col_meta = ns.col_meta
        self.encoding = ns.encoding

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self.indices = []
        for col in self.columns:
            self.indices.append(str_to_column_index(col, fail_on_non_digit=True))
        if len(self.columns) != len(self.languages):
            raise Exception("Number of columns and languages differ: %d != %d" % (len(self.columns), len(self.languages)))

        if (self.col_id is not None) and (len(self.col_id) > 0):
            self.idx_id = str_to_column_index(self.col_id)

        if self.col_meta is not None:
            self.idx_meta = []
            for c in self.col_meta:
                self.idx_meta.append(str_to_column_index(c))

        self._inputs = locate_files(self.source, input_lists=self.source_list, fail_if_empty=True, default_glob=self._get_default_glob())

    def _init_reader(self, current_input) -> csv.reader:
        """
        Initializes and returns the CSV reader to use.

        :param current_input: the file pointer to initialize with
        :return: the reader to use
        :rtype: csv.reader
        """
        raise NotImplementedError()

    def read(self) -> Iterable[TranslationData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: TranslationData
        """
        self.finalize()

        self._current_input = self._inputs.pop(0)
        self.session.current_input = self._current_input
        self.logger().info("Reading from: " + str(self.session.current_input))
        self._current_input = open_file(self._current_input, mode="rt", encoding=self.encoding, logger=self.logger())
        self._current_reader = self._init_reader(self._current_input)

        count = 0
        for row in self._current_reader:
            try:
                count += 1
                translations = dict()
                for index in self.indices:
                    cell = row[index]
                    if cell is not None:
                        cell = cell.strip()
                        if len(cell) > 0:
                            translations[self.languages[index]] = cell

                meta = None

                # file
                meta = add_metadata(meta, "file", self.session.current_input)

                # ID?
                if self.idx_id > -1:
                    meta = add_metadata(meta, "id", row[self.idx_id])
                else:
                    meta = add_metadata(meta, "id", str(count))

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

                yield TranslationData(
                    translations=translations,
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


class AbstractCsvLikeTranslationWriter(BatchTranslationWriter, abc.ABC, PlaceholderSupporter):
    """
    Ancestor for writers of CSV-like files.
    """

    def __init__(self, target: str = None, no_header: bool = False, no_col_id: bool = False,
                 languages: List[str] = None, encoding: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param no_header: whether to suppress the header row
        :type no_header: bool
        :param no_col_id: whether to suppress the column with the row ID
        :type no_col_id: bool
        :param languages: the list of languages to output
        :type languages: list
        :param encoding: the encoding to use, None for default
        :type encoding: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.target = target
        self.languages = languages
        self.no_header = no_header
        self.no_col_id = no_col_id
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
        parser.add_argument("-g", "--languages", metavar="LANG", type=str, default=None, help="The language IDs (ISO 639-1) to output in separate columns", required=True, nargs="+")
        parser.add_argument("-n", "--no_header", action="store_true", help="For suppressing the header row", required=False)
        parser.add_argument("--no_col_id", action="store_true", help="For suppressing the column with the row IDs", required=False)
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
        self.languages = ns.languages
        self.no_header = ns.no_header
        self.no_col_id = ns.no_col_id
        self.encoding = ns.encoding

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        if (self.languages is None) or (len(self.languages) == 0):
            raise Exception("No languages specified!")

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

    def write_batch(self, data: Iterable[TranslationData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of TranslationData
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
                if not self.no_col_id:
                    row.append("ID")
                row.extend(self.languages[:])
                self._output_writer.writerow(row)

        for item in data:
            row = []
            if not self.no_col_id:
                if (item.meta is not None) and ("id" in item.meta):
                    row.append(item.meta["id"])
                else:
                    row.append(None)
            for lang in self.languages:
                if lang in item.translations:
                    row.append(empty_str_if_none(item.translations[lang]))
                else:
                    row.append(None)
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


class CsvTranslationReader(AbstractCsvLikeTranslationReader):
    """
    Reader for CSV files.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 no_header: bool = False, col_id: str = None, col_meta: List[str] = None,
                 columns: List[str] = None, languages: List[str] = None, encoding: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param no_header: whether the data files have no header
        :type no_header: bool
        :param col_id: the (optional) 1-based column containing the row ID
        :type col_id: str
        :param col_meta: the columns to store in the meta-data, can be None
        :type col_meta: list
        :param columns: the columns with the language data (1-based indices)
        :type columns: list
        :param languages: the language IDs (ISO 639-1) corresponding to the columns
        :type languages: list
        :param encoding: the encoding to use, None for auto-detect
        :type encoding: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(source=source, source_list=source_list,
                         no_header=no_header, columns=columns, languages=languages,
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
        return "Reads translation data in CSV format."

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

    def _init_reader(self, current_input) -> csv.reader:
        """
        Initializes and returns the CSV reader to use.

        :param current_input: the file pointer to initialize with
        :return: the reader to use
        :rtype: csv.reader
        """
        reader = csv.reader(current_input)
        if not self.no_header:
            next(reader)
        return reader


class CsvTranslationWriter(AbstractCsvLikeTranslationWriter):
    """
    Writer for CSV files.
    """

    def __init__(self, target: str = None, no_header: bool = False,
                 languages: List[str] = None, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param no_header: whether to suppress the header row
        :type no_header: bool
        :param languages: the list of languages to output
        :type languages: list
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(target=target, no_header=no_header, languages=languages,
                         logger_name=logger_name, logging_level=logging_level)

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
        return "Writes translation data in CSV format."

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


class TsvTranslationReader(AbstractCsvLikeTranslationReader):
    """
    Reader for TSV files.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 no_header: bool = False, col_id: str = None, col_meta: List[str] = None,
                 columns: List[str] = None, languages: List[str] = None, encoding: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param no_header: whether the data files have no header
        :type no_header: bool
        :param columns: the columns with the language data (1-based indices)
        :type columns: list
        :param col_id: the (optional) 1-based column containing the row ID
        :type col_id: str
        :param col_meta: the columns to store in the meta-data, can be None
        :type col_meta: list
        :param languages: the language IDs (ISO 639-1) corresponding to the columns
        :type languages: list
        :param encoding: the encoding to use, None for auto-detect
        :type encoding: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(source=source, source_list=source_list,
                         no_header=no_header, columns=columns, languages=languages,
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
        return "Reads translation data in TSV format."

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

    def _init_reader(self, current_input) -> csv.reader:
        """
        Initializes and returns the CSV reader to use.

        :param current_input: the file pointer to initialize with
        :return: the reader to use
        :rtype: csv.reader
        """
        reader = csv.reader(current_input, delimiter='\t')
        if not self.no_header:
            next(reader)
        return reader


class TsvTranslationWriter(AbstractCsvLikeTranslationWriter):
    """
    Writer for TSV files.
    """

    def __init__(self, target: str = None, no_header: bool = False,
                 languages: List[str] = None, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param no_header: whether to suppress the header row
        :type no_header: bool
        :param languages: the list of languages to output
        :type languages: list
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(target=target, no_header=no_header, languages=languages,
                         logger_name=logger_name, logging_level=logging_level)

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
        return "Writes translation data in TSV format."

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
