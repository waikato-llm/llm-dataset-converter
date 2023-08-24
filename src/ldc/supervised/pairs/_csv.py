import argparse
import csv
from typing import Iterable, List, Union

from ldc.core import LOGGING_WARN
from ldc.io import locate_files, open_file, generate_output
from ._core import PairData, PairReader, BatchPairWriter


class AbstractCsvLikePairsReader(PairReader):
    """
    Ancestor for readers of CSV-like files.
    """

    def __init__(self, source: Union[str, List[str]] = None, no_header: bool = False,
                 col_instruction: str = None, col_input: str = None, col_output: str = None,
                 col_id: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the reader.

        :param source: the filename(s)
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
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.source = source
        self.no_header = no_header
        self.col_instruction = col_instruction
        self.col_input = col_input
        self.col_output = col_output
        self.col_id = col_id
        self.idx_instruction = -1
        self.idx_input = -1
        self.idx_output = -1
        self.idx_id = -1
        self._inputs = None
        self._current_input = None
        self._current_reader = None

    def _get_input_description(self) -> str:
        """
        Returns the description to use for the input file in the argparser.

        :return: the description
        :rtype: str
        """
        raise NotImplemented()

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help=self._get_input_description(), required=True, nargs="+")
        parser.add_argument("--col_instruction", metavar="COL", type=str, default=None, help="The name of the column (or 1-based index if no header row) with the instructions", required=False)
        parser.add_argument("--col_input", metavar="COL", type=str, default=None, help="The name of the column (or 1-based index if no header row) with the inputs", required=False)
        parser.add_argument("--col_output", metavar="COL", type=str, default=None, help="The name of the column (or 1-based index if no header row) with the outputs", required=False)
        parser.add_argument("--col_id", metavar="COL", type=str, default=None, help="The name (or 1-based index if no header row) of the column with the row IDs (gets stored under 'id' in meta-data)", required=False)
        parser.add_argument("-n", "--no_header", action="store_true", help="For files with no header row", required=False)
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
        self.col_id = ns.col_id
        self.no_header = ns.no_header

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        try:
            self.idx_instruction = int(self.col_instruction) - 1
        except:
            self.idx_instruction = -1
        try:
            self.idx_input = int(self.col_input) - 1
        except:
            self.idx_input = -1
        try:
            self.idx_output = int(self.col_output) - 1
        except:
            self.idx_output = -1
        if not self.no_header and (self.col_instruction is None) and (self.col_input is None) and (self.col_output is None):
            raise Exception("Header row expected but no columns specified!")
        if self.no_header and (self.idx_instruction == -1) and (self.idx_input == -1) and (self.idx_output == -1):
            raise Exception("No header row expected but no column indices specified!")

        try:
            self.idx_id = int(self.col_id) - 1
        except:
            self.idx_id = -1

        self._inputs = locate_files(self.source, fail_if_empty=True)

    def _init_reader(self, current_input) -> Union[csv.reader, csv.DictReader]:
        """
        Initializes and returns the CSV reader to use.

        :param current_input: the file pointer to initialize with
        :return: the reader to use
        :rtype: csv.reader or csv.DictReader
        """
        raise NotImplemented()

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
        self._current_input = open_file(self._current_input, mode="rt")
        self._current_reader = self._init_reader(self._current_input)
        self.session.input_changed = True

        for row in self._current_reader:
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
            if id_ is not None:
                meta = {"id": id_}

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
            self._current_reader = None
            self._current_input.close()
            self._current_input = None


class AbstractCsvLikePairsWriter(BatchPairWriter):
    """
    Ancestor for writers of CSV-like files.
    """

    def __init__(self, target: str = None, no_header: bool = False,
                 col_instruction: str = None, col_input: str = None, col_output: str = None, col_id: str = None,
                 logging_level: str = LOGGING_WARN):
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
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logging_level=logging_level)
        self.target = target
        self.no_header = no_header
        self.col_instruction = col_instruction
        self.col_input = col_input
        self.col_output = col_output
        self.col_id = col_id
        self._output = None
        self._output_writer = None

    def _get_output_description(self) -> str:
        """
        Returns the description to use for the output file in the argparser.

        :return: the description
        :rtype: str
        """
        raise NotImplemented()

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help=self._get_output_description(), required=True)
        parser.add_argument("--col_instruction", metavar="COL", type=str, default=None, help="The name of the column for the instructions", required=False)
        parser.add_argument("--col_input", metavar="COL", type=str, default=None, help="The name of the column for the inputs", required=False)
        parser.add_argument("--col_output", metavar="COL", type=str, default=None, help="The name of the column for the outputs", required=False)
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
        self.col_instruction = ns.col_instruction
        self.col_input = ns.col_input
        self.col_output = ns.col_output
        self.col_id = ns.col_id
        self.no_header = ns.no_header

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
        raise NotImplemented()

    def _get_extension(self) -> str:
        """
        Returns the extension to use for output files.

        :return: the extension to use (incl dot)
        :rtype: str
        """
        raise NotImplemented()

    def write_batch(self, data: Iterable[PairData]):
        """
        Saves the data in one go.

        :param data: the data to write as iterable of PairData
        :type data: Iterable
        """
        if self.session.input_changed:
            self.finalize()
            output = generate_output(self.session.current_input, self.target, self._get_extension(), self.session.options.compression)
            self.logger().info("Writing to: " + output)
            self._output = open_file(output, mode="wt")
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
                row.extend([item.instruction, item.input, item.output])
            else:
                if self.col_instruction is not None:
                    row.append(item.instruction)
                if self.col_input is not None:
                    row.append(item.input)
                if self.col_output is not None:
                    row.append(item.output)
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


class CsvPairsReader(AbstractCsvLikePairsReader):
    """
    Reader for CSV files.
    """

    def __init__(self, source: Union[str, List[str]] = None, no_header: bool = False,
                 col_instruction: str = None, col_input: str = None, col_output: str = None,
                 col_id: str = None, skip_duplicate_ids: bool = False,
                 logging_level: str = LOGGING_WARN):
        """
        Initializes the reader.

        :param source: the filename(s)
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
        :param skip_duplicate_ids: with a ID column defined, duplicate rows can be skipped
        :type skip_duplicate_ids: bool
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(source=source, no_header=no_header, col_instruction=col_instruction, col_input=col_input,
                         col_output=col_output, col_id=col_id, logging_level=logging_level)

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


class CsvPairsWriter(AbstractCsvLikePairsWriter):
    """
    Writer for CSV files.
    """

    def __init__(self, target: str = None, no_header: bool = False,
                 col_instruction: str = None, col_input: str = None, col_output: str = None, col_id: str = None,
                 logging_level: str = LOGGING_WARN):
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
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(target=target, no_header=no_header, col_instruction=col_instruction, col_input=col_input,
                         col_output=col_output, col_id=col_id, logging_level=logging_level)

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

    def __init__(self, source: Union[str, List[str]] = None, no_header: bool = False,
                 col_instruction: str = None, col_input: str = None, col_output: str = None,
                 col_id: str = None, skip_duplicate_ids: bool = False,
                 logging_level: str = LOGGING_WARN):
        """
        Initializes the reader.

        :param source: the filename(s)
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
        :param skip_duplicate_ids: with a ID column defined, duplicate rows can be skipped
        :type skip_duplicate_ids: bool
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(source=source, no_header=no_header, col_instruction=col_instruction, col_input=col_input,
                         col_output=col_output, col_id=col_id, logging_level=logging_level)

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "from-tsv-pairs"

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
                 logging_level: str = LOGGING_WARN):
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
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(target=target, no_header=no_header, col_instruction=col_instruction, col_input=col_input,
                         col_output=col_output, col_id=col_id, logging_level=logging_level)

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "to-tsv-pairs"

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
