import abc
import argparse
import csv
from typing import Iterable, List, Union

from ldc.core import LOGGING_WARN, domain_suffix
from ldc.io import locate_files, open_file, generate_output
from ._core import TranslationData, TranslationReader, BatchTranslationWriter


class AbstractCsvLikeTranslationReader(TranslationReader, abc.ABC):
    """
    Ancestor for readers of CSV-like files.
    """

    def __init__(self, source: Union[str, List[str]] = None, no_header: bool = False, col_id: str = None,
                 columns: List[str] = None, languages: List[str] = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param no_header: whether the data files have no header
        :type no_header: bool
        :param col_id: the (optional) 1-based column containing the row ID
        :type col_id: str
        :param columns: the columns with the language data (1-based indices)
        :type columns: list
        :param languages: the language IDs (ISO 639-1) corresponding to the columns
        :type languages: list
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.source = source
        self.no_header = no_header
        self.col_id = col_id
        self.idx_id = -1
        self.columns = columns
        self.languages = languages
        self.indices = None
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

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help=self._get_input_description(), required=True, nargs="+")
        parser.add_argument("-c", "--columns", metavar="COL", type=str, default=None, help="The 1-based column indices with the language data", required=True, nargs="+")
        parser.add_argument("-g", "--languages", metavar="LANG", type=str, default=None, help="The language IDs (ISO 639-1) corresponding to the columns", required=True, nargs="+")
        parser.add_argument("-n", "--no_header", action="store_true", help="For files with no header row", required=False)
        parser.add_argument("--col_id", metavar="COL", type=str, default=None, help="The 1-based column containing the row ID", required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.source = ns.input
        self.columns = ns.columns[:]
        self.languages = ns.languages[:]
        self.no_header = ns.no_header
        self.col_id = ns.col_id

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self.indices = []
        for col in self.columns:
            try:
                self.indices.append(int(col) - 1)
            except:
                raise Exception("Failed to parse column: %s" % col)
        if len(self.columns) != len(self.languages):
            raise Exception("Number of columns and languages differ: %d != %d" % (len(self.columns), len(self.languages)))

        if (self.col_id is not None) and (len(self.col_id) > 0):
            try:
                self.idx_id = int(self.col_id) - 1
            except:
                raise Exception("Failed to parse ID column as integer: %s" % self.col_id)

        self._inputs = locate_files(self.source, fail_if_empty=True)

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
        self._current_input = open_file(self._current_input, mode="rt")
        self._current_reader = self._init_reader(self._current_input)

        count = 0
        for row in self._current_reader:
            count += 1
            translations = dict()
            for index in self.indices:
                cell = row[index]
                if cell is not None:
                    cell = cell.strip()
                    if len(cell) > 0:
                        translations[self.languages[index]] = cell

            meta = dict()
            if self.idx_id > -1:
                meta["id"] = row[self.idx_id]
            else:
                meta["id"] = str(count)

            yield TranslationData(
                translations=translations,
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
            self._current_reader = None
            self._current_input.close()
            self._current_input = None


class AbstractCsvLikeTranslationWriter(BatchTranslationWriter, abc.ABC):
    """
    Ancestor for writers of CSV-like files.
    """

    def __init__(self, target: str = None, no_header: bool = False, no_col_id: bool = False,
                 languages: List[str] = None, logging_level: str = LOGGING_WARN):
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
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.target = target
        self.languages = languages
        self.no_header = no_header
        self.no_col_id = no_col_id
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
        parser.add_argument("-g", "--languages", metavar="LANG", type=str, default=None, help="The language IDs (ISO 639-1) to output in separate columns", required=True, nargs="+")
        parser.add_argument("-n", "--no_header", action="store_true", help="For suppressing the header row", required=False)
        parser.add_argument("--no_col_id", action="store_true", help="For suppressing the column with the row IDs", required=False)
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
        if self._has_input_changed(update=True):
            self.finalize()
            output = generate_output(self.session.current_input, self.target, self._get_extension(), self.session.options.compression)
            self.logger().info("Writing to: " + output)
            self._output = open_file(output, mode="wt")
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
                    row.append(item.translations[lang])
                else:
                    row.append(None)
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


class CsvTranslationReader(AbstractCsvLikeTranslationReader):
    """
    Reader for CSV files.
    """

    def __init__(self, source: Union[str, List[str]] = None, no_header: bool = False, col_id: str = None,
                 columns: List[str] = None, languages: List[str] = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param no_header: whether the data files have no header
        :type no_header: bool
        :param col_id: the (optional) 1-based column containing the row ID
        :type col_id: str
        :param columns: the columns with the language data (1-based indices)
        :type columns: list
        :param languages: the language IDs (ISO 639-1) corresponding to the columns
        :type languages: list
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(source=source, no_header=no_header, columns=columns, languages=languages,
                         col_id=col_id, logging_level=logging_level)

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
                 languages: List[str] = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param no_header: whether to suppress the header row
        :type no_header: bool
        :param languages: the list of languages to output
        :type languages: list
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(target=target, no_header=no_header, languages=languages, logging_level=logging_level)

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

    def __init__(self, source: Union[str, List[str]] = None, no_header: bool = False, col_id: str = None,
                 columns: List[str] = None, languages: List[str] = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param no_header: whether the data files have no header
        :type no_header: bool
        :param columns: the columns with the language data (1-based indices)
        :type columns: list
        :param col_id: the (optional) 1-based column containing the row ID
        :type col_id: str
        :param languages: the language IDs (ISO 639-1) corresponding to the columns
        :type languages: list
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(source=source, no_header=no_header, columns=columns, languages=languages,
                         col_id=col_id, logging_level=logging_level)

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
                 languages: List[str] = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the writer.

        :param target: the filename/dir to write to
        :type target: str
        :param no_header: whether to suppress the header row
        :type no_header: bool
        :param languages: the list of languages to output
        :type languages: list
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(target=target, no_header=no_header, languages=languages, logging_level=logging_level)

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